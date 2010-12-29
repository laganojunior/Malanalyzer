from google.appengine.ext import webapp

import WebGrab
from Entities import *

import logging

class Extractor(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'

        # Get the next username on the list
        username = self.getNextUser()

        if username == None:
            logging.debug('None in queue, inserting more')
            self.redirect('/fillqueue')
            return

        self.response.out.write('Getting %s' % username)

        # Get the users animelist and id
        animelist = WebGrab.getAnimeList(username)
        userid = WebGrab.getUserId(username)

        # Get the user object
        user = self.getUserObject(userid, username)

        # Get the list of known ratings of this user
        oldRatings = Rating.gql('WHERE user = :1', user)

        # Go through each rating in the new list and create a map from
        # id to rating
        ratingMap = {}
        nameMap   = {}
        for anime in animelist:
            animeid   = anime['id']
            rating    = anime['score']
            
            if rating != 0:
                ratingMap[animeid] = rating
                nameMap[animeid]   = anime['title']

        # Go through each known rating
        for rating in oldRatings:
            animeid = rating.anime.animeid

            if animeid in ratingMap:
                # Update to new score if there is one
                rating.rating = ratingMap[animeid]
                rating.put()

                # Delete the entry from the map to avoid it being
                # inserted later
                del ratingMap[animeid]
            else:
                # Otherwise, delete the rating to reflect that it is now
                # gone
                rating.delete()

        # Now insert new ratings
        for animeid in ratingMap:
            animename = nameMap[animeid]
            score = ratingMap[animeid]

            # Get the anime object from the database
            anime = self.getAnimeObject(animeid, animename)

            # Generate the rating object
            rating = Rating()
            rating.user = user
            rating.anime = anime
            rating.rating = score
            
            rating.put()

    def getUserObject(self, userid, username):
        # Check if the user is already in the database
        query = User.gql('WHERE userid = :1', userid)
        res = query.fetch(1)

        if res == []:
            user = User()
            user.name = username
            user.userid = userid
            user.put()
            return user
        else:
            return res[0]

    def getAnimeObject(self, animeid, animename):
        # Check if the anime is already in the database
        query = Anime.gql('WHERE animeid = :1', animeid)
        res = query.fetch(1)

        if res == []:
            anime = Anime()
            anime.name = animename
            anime.animeid = animeid
            anime.put()
            return anime
        else:
            return res[0]

    def getNextUser(self):
        query = QueueUser.gql('ORDER BY date')
        res = query.fetch(1)

        if res == []:
            return None
        else:
            username = res[0].username
            res[0].delete()
            return username
