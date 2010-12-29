from google.appengine.ext import webapp

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
        # Check if the user is already in the queue
        query = QueueUser.gql('WHERE username=:1', username)
        res = query.fetch(1)
        if res != []:
            self.response.out.write('%s already queued' %
                                     cgi.escape(username))
            return

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

        queueEntry = QueueUser()
        queueEntry.username = username
        queueEntry.put()

        self.response.out.write('Successfully queued %s' %
                                 cgi.escape(username))
