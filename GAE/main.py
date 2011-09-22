#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import * 

from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

# 接続の生存期限。
con_expire = 30.0

# グループ作成用のダミーモデル。
class Entry(db.Model):
    None

# マッチング情報。
class Match(db.Model):
    his_uid = db.StringProperty()

# ストローク情報。
class Stroke(db.Model):
    data = db.TextProperty()

# 最後通信情報。
class LastAccess(db.Model):
    dateTime = db.DateTimeProperty()

# マッチング処理。
class MatchHandler(webapp.RequestHandler):
    def post(self):
        # 引数の取得。
        uid = self.request.get('uid')
        if not uid:
            self.response.out.write('invalid')
            return
        # マッチング候補に入れる。
        match_entry = Entry.get_or_insert('match')
        Match(parent = match_entry, key_name = uid, his_uid = 'none').put()
        # UIDベースの情報の初期化を行う。
        user_entry = Entry.get_or_insert(uid)
        def txn():
            stroke = Stroke(parent = user_entry, key_name = uid)
            last = LastAccess(parent = user_entry, key_name = uid, dateTime = datetime.now())
            db.put((stroke, last))
        db.run_in_transaction(txn)
        # とりあえず成功を返しておく。
        self.response.out.write('ok')

# マッチ相手の取得。
class GetMateHandler(webapp.RequestHandler):
    def post(self):
        # 引数の取得。
        uid = self.request.get('uid')
        if not uid:
            self.response.out.write('invalid')
            return
        # 適当にペアを作ってマッチさせる。
        match_entry = Entry.get_or_insert('match')
        def txn():
            pair = Match.all().ancestor(match_entry).filter('his_uid =', 'none').fetch(2)
            if len(pair) > 1:
                pair[0].his_uid = pair[1].key().name()
                pair[1].his_uid = pair[0].key().name()
                db.put(pair)
        db.run_in_transaction(txn)
        # 相手のUIDをレスポンスとして返す。
        match = Match.get_by_key_name(uid, match_entry)
        self.response.out.write(match.his_uid if match else 'invalid')

# ストロークの取得。
class GetStrokeHandler(webapp.RequestHandler):
    def post(self):
        # 引数の取得。
        uid = self.request.get('uid')
        if not uid:
            self.response.out.write('invalid')
            return
        # ストロークをレスポンスとして返す。
        stroke = Stroke.get_by_key_name(uid, Entry.get_by_key_name(uid))
        self.response.out.write(stroke.data if stroke else 'invalid')

# ストロークの更新。
class UpdateStrokeHandler(webapp.RequestHandler):
    def post(self):
        # 引数の取得。
        uid = self.request.get('uid')
        data = self.request.get('data')
        if not uid or not data:
            self.response.out.write('invalid')
            return
        # 情報の更新。
        user_entry = Entry.get_by_key_name(uid)
        def txn():
            stroke = Stroke(parent = user_entry, key_name = uid, data = data)
            last = LastAccess(parent = user_entry, key_name = uid, dateTime = datetime.now())
            db.put((stroke, last))
        db.run_in_transaction(txn)
        # 成功メッセージを返す。
        self.response.out.write('ok')

# 切断処理。
class QuitHandler(webapp.RequestHandler):
    def post(self):
        # 引数の取得。
        uid = self.request.get('uid')
        if not uid:
            self.response.out.write('invalid')
            return
        # 削除。
        match = Match.get_by_key_name(uid, Entry.get_by_key_name('match'))
        if match: match.delete();
        # ともかく成功メッセージを返す。
        self.response.out.write('ok')

# トップページのハンドラー。
class MainHandler(webapp.RequestHandler):
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
