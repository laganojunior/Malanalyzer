from google.appengine.ext import webapp
from google.appengine.api import taskqueue

import WebGrab
import urllib2
from Entities import *

import logging
import cgi

class InsertUsername(webapp.RequestHandler):
    def post(self):
        self.response.headers['Content-Type'] = 'text/html'

        username = self.request.get('username')

        logging.debug('Got request to queue %s' % cgi.escape(username))

        # Verify the user profile is real
        try:
            userid = WebGrab.getUserId(username)
        except urllib2.URLError:
            self.response.out.write('Could not find user %s' %
                                     cgi.escape(username))
            return
        except WebGrab.UnknownUser:
            self.response.out.write('Could not find user %s' %
                                     cgi.escape(username))
            return

        # Enter the user into the taskqueue
        taskqueue.add(url='/extract',
                      params={'username' : username},
                      name="user_extract-%s" % username,
                      queue_name="user-extract")
