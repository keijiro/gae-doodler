#!/usr/bin/env python

from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

class Doodler(db.Model):
    uid = db.StringProperty()
    stroke = db.StringProperty()

class MainHandler(webapp.RequestHandler):
    def get(self):
        self.response.out.write('ready')

class GetHandler(webapp.RequestHandler):
    def post(self):
        uid = self.request.get('uid')

        if not uid:
            self.response.out.write('invalid')
            return
        
        doodler = memcache.get(uid)
        if not doodler:
            doodler = Doodler.get_by_key_name(uid)
            memcache.set(uid, doodler, 10)
        
        self.response.out.write(doodler.stroke if doodler else 'none')

class SetHandler(webapp.RequestHandler):
    def post(self):
        uid = self.request.get('uid')
        stroke = self.request.get('str')

        if not uid or not stroke:
            self.response.out.write('invalid')
            return

        doodler = Doodler(key_name = uid, stroke = stroke)
        doodler.put()
        memcache.set(uid, stroke, 10)

        self.response.out.write('ok')

def main():
    application = webapp.WSGIApplication([('/', MainHandler),
                                          ('/get', GetHandler),
                                          ('/set', SetHandler)],
                                        debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
