from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api import taskqueue

import WebGrab
import logging

import time

class FillQueue(webapp.RequestHandler):

    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write("Sent fill request")

        # Fill up the queue
        taskqueue.add(url='/fillqueue', name='fillqueue-%s' % int(time.time()))

        # Request another filling in 20 minutes
        taskqueue.add(url='/fillqueue',
                      name='fillqueue-request-%s' % int(time.time()),
                      method='get',
                      countdown = 20 * 60)

    def post(self):
        self.response.headers['Content-Type'] = 'text/plain'

        # Fill the queue with most recent online users
        # Get the next username on the list
        usernamelist = WebGrab.getRecentOnlineUsernames()

        if usernamelist == []:
            self.response.out.write('Webgrab got 0 results<br>')
            logging.debug('Webgrab got 0 results')

        # Create task queue items for each user
        for i, username in enumerate(usernamelist):
            taskqueue.add(url='/extract',
                          params={'username' : username},
                          name="user_extract-%s-%s" % (username, 
               int(time.time())),
                          queue_name="user-extract")
