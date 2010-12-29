from google.appengine.ext import webapp
from google.appengine.ext import db

import WebGrab
from Entities import *

import logging

class FillQueue(webapp.RequestHandler):

    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'

        # Fill the queue with most recent online users
        # Get the next username on the list
        usernamelist = WebGrab.getRecentOnlineUsernames()

        if usernamelist == []:
            self.response.out.write('Webgrab got 0 results')
            logging.debug('Webgrab got 0 results')            

        insertList = []
        for username in usernamelist:
            queueEntry = QueueUser()
            queueEntry.username = username
            insertList.append(queueEntry)

        db.put(insertList)
        
