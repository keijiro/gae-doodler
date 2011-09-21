#!/usr/bin/env python

import math, time;

from google.appengine.api import memcache
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

class MainHandler(webapp.RequestHandler):
    def get(self):
        self.response.out.write('ready')

class GetHandler(webapp.RequestHandler):
    def post(self):
        data = memcache.get(self.request.get("uid"))
        self.response.out.write(data or "none")

class SetHandler(webapp.RequestHandler):
    def post(self):
        guid = self.request.get("uid")
        data = self.request.get("data")
        
        if not guid or not data:
            self.response.out.write('invalid')
            return

        memcache.set(guid, data, 60)
        self.response.out.write('ok')

def main():
    application = webapp.WSGIApplication([('/', MainHandler),
                                          ('/get', GetHandler),
                                          ('/set', SetHandler)],
                                        debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
