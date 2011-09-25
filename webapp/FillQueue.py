from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api import taskqueue

import WebGrab
import logging

class FillQueue(webapp.RequestHandler):

    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'

        # Fill the queue with most recent online users
        # Get the next username on the list
        usernamelist = WebGrab.getRecentOnlineUsernames()

        if usernamelist == []:
            self.response.out.write('Webgrab got 0 results<br>')
            logging.debug('Webgrab got 0 results')

        # Create task queue items for each user
        for username in usernamelist:
            taskqueue.add(url='/extract',
                          params={'username' : username},
                          name="user_extract-%s" % username,
                          queue_name="user-extract")

        # Create another request to refill the queue in 1 second
        taskqueue.add(url='/fillqueue', name='fillqueue',
                      countdown = 20)

    def post(self):
        self.get()
