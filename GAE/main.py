#!/usr/bin/env python
# -*- coding: utf-8 -*-

from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

class Doodler(db.Model):
    '''プレイヤーのデータモデル'''
    mate = db.StringProperty()
    stroke = db.TextProperty()

class MatchHandler(webapp.RequestHandler):
    '''マッチング処理'''
    def post(self):
        # 引数の取得。
        uid = self.request.get('uid')
        if not uid:
            self.response.out.write('invalid')
            return
        # プレイヤーの初期化。
        doodler = Doodler(key_name = uid, mate = 'none')
        doodler.put()
        # マッチ相手が居ないプレイヤーを探す。
        query = Doodler.all()
        query.filter('__key__ !=', db.Key.from_path('Doodler', uid))
        query.filter('mate =', 'none')
        matched = query.get()
        if matched:
            # 自分と相手のマッチ情報を更新する。
            doodler.mate = matched.key().name()
            doodler.put()
            matched.mate = uid
            matched.put()
            # 相手のUIDをレスポンスとして返す。
            self.response.out.write(doodler.mate)
        else:
            # 相手無し。待ちに入る。
            self.response.out.write('wait')

class GetMateHandler(webapp.RequestHandler):
    '''マッチ相手の取得'''
    def post(self):
        # 引数の取得。
        uid = self.request.get('uid')
        if not uid:
            self.response.out.write('invalid')
            return
        # 相手のUIDをレスポンスとして返す。
        doodler = Doodler.get_by_key_name(uid)
        self.response.out.write(doodler.mate if doodler else 'invalid')

class GetStrokeHandler(webapp.RequestHandler):
    '''ストロークの取得'''
    def post(self):
        # 引数の取得。
        uid = self.request.get('uid')
        if not uid:
            self.response.out.write('invalid')
            return
        # ストロークをレスポンスとして返す。
        doodler = Doodler.get_by_key_name(uid)
        self.response.out.write(doodler.stroke if doodler else 'none')

class UpdateStrokeHandler(webapp.RequestHandler):
    '''ストロークの更新'''
    def post(self):
        # 引数の取得。
        uid = self.request.get('uid')
        stroke = self.request.get('str')
        if not uid or not stroke:
            self.response.out.write('invalid')
            return
        # 現状の取得。
        doodler = Doodler.get_by_key_name(uid)
        if not doodler:
            self.response.out.write('invalid')
            return
        # ストロークの更新。
        doodler.stroke = stroke;
        doodler.put()
        # 成功メッセージを返す。
        self.response.out.write('ok')

class MainHandler(webapp.RequestHandler):
    '''トップページのハンドラー'''
    def get(self):
        self.response.out.write('ready')

def main():
    application = webapp.WSGIApplication([('/', MainHandler),
                                          ('/match', MatchHandler),
                                          ('/mate', GetMateHandler),
                                          ('/stroke', GetStrokeHandler),
                                          ('/update', UpdateStrokeHandler)],
                                         debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
