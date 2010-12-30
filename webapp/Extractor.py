from google.appengine.ext import webapp

import WebGrab
from Entities import *

import logging

class Extractor(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'

        # Get the next username on the list
        username = self.getNextUser()

        if username == None:
            logging.debug('None in queue')
            return

        self.response.out.write('Getting %s' % username)
        logging.debug('Getting %s' % username)

        # Get the users animelist and id
        animelist = WebGrab.getAnimeList(username)
        userid = WebGrab.getUserId(username)

        # Go through each rating in the new list and create a map from
        # id to rating
        ratingMap = {}
        nameMap   = {}
        for anime in animelist:
            animeid   = anime['id']
            rating    = anime['score']

            if rating != 0:
                ratingMap[str(animeid)] = rating
                nameMap[animeid]   = anime['title']

        # Insert the user and anime objects for the ratings to reference
        user = self.getUserObject(userid, username)
        animes = self.getAnimeObjects(nameMap)
        db.put(animes + [user])

        # Now insert new ratings
        ratings = [0] * len(ratingMap)

        for i, anime in enumerate(animes):
            # Generate the rating object
            keyname = anime.key().name()
            rating = Rating(key_name=str(user) + keyname)
            rating.user = user
            rating.anime = anime
            rating.rating = ratingMap[keyname]
            ratings[i] = rating

        # Batch update the ratings
        db.put(ratings)

    def getUserObject(self, userid, username):
        # Check if the user is already in the database
        user = User(key_name=str(userid))
        user.name = username
        return user
            
    def getAnimeObjects(self, namemap):
        animes = [0] * len(namemap)

        for i, animeid in enumerate(namemap):
            anime = Anime(key_name=str(animeid))
            anime.name = namemap[animeid]
            animes[i] = anime

        return animes 

    def getNextUser(self):
        query = QueueUser.gql('ORDER BY date')
        res = query.fetch(1)

        if res == []:
            return None
        else:
            username = res[0].username
            res[0].delete()
            return username
