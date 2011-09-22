#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import * 

from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

# データの生存期限。
doodler_expire = 30.0

class Matchmaker(db.Model):
    None

class Match(db.Model):
    his_uid = db.StringProperty()

class Stroke(db.Model):
    data = db.TextProperty()

class Timestamp(db.Model):
    dateTime = db.DateTimeProperty()

def match_pair(matchmaker):
    pair = Match.all().ancestor(matchmaker).filter('his_uid =', 'none').fetch(2)
    if len(pair) > 1:
        pair[0].his_uid = pair[1].key().name()
        pair[1].his_uid = pair[0].key().name()
        db.put(pair)

class MatchHandler(webapp.RequestHandler):
    '''マッチング処理'''
    def post(self):
        # 引数の取得。
        uid = self.request.get('uid')
        if not uid:
            self.response.out.write('invalid')
            return
        #
        matchmaker = Matchmaker.get_or_insert('global')
        Match(parent = matchmaker, key_name = uid, his_uid = 'none').put()
        Stroke(key_name = uid).put()
        #
        db.run_in_transaction(match_pair, matchmaker)
        #
        self.response.out.write('ok')

class GetMateHandler(webapp.RequestHandler):
    '''マッチ相手の取得'''
    def post(self):
        # 引数の取得。
        uid = self.request.get('uid')
        if not uid:
            self.response.out.write('invalid')
            return
        # 相手のUIDをレスポンスとして返す。
        match = Match.get_by_key_name(uid, Matchmaker.get_by_key_name('global'))
        self.response.out.write(match.his_uid if match else 'invalid')

class GetStrokeHandler(webapp.RequestHandler):
    '''ストロークの取得'''
    def post(self):
        # 引数の取得。
        uid = self.request.get('uid')
        if not uid:
            self.response.out.write('invalid')
            return
        # ストロークをレスポンスとして返す。
        stroke = Stroke.get_by_key_name(uid)
        self.response.out.write(stroke.data if stroke else 'invalid')

class UpdateStrokeHandler(webapp.RequestHandler):
    '''ストロークの更新'''
    def post(self):
        # 引数の取得。
        uid = self.request.get('uid')
        data = self.request.get('data')
        if not uid or not data:
            self.response.out.write('invalid')
            return
        # ストロークの更新。
        Stroke(key_name = uid, data = data).put()
        # 成功メッセージを返す。
        self.response.out.write('ok')

class QuitHandler(webapp.RequestHandler):
    '''切断処理'''
    def post(self):
        # 引数の取得。
        uid = self.request.get('uid')
        if not uid:
            self.response.out.write('invalid')
            return
        # 削除。
        match = Match.get_by_key_name(uid, Matchmaker.get_by_key_name('global'))
        if match: match.delete();
        # ともかく成功メッセージを返す。
        self.response.out.write('ok')

class MainHandler(webapp.RequestHandler):
    '''トップページのハンドラー'''
    def get(self):
        # ダミーメッセージ。
        self.response.out.write('ready')

def main():
    application = webapp.WSGIApplication([('/', MainHandler),
                                          ('/match', MatchHandler),
                                          ('/mate', GetMateHandler),
                                          ('/stroke', GetStrokeHandler),
                                          ('/update', UpdateStrokeHandler),
                                          ('/quit', QuitHandler)],
                                         debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
