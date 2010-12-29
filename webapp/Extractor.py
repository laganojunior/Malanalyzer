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
            logging.debug('None in queue')
            return

        self.response.out.write('Getting %s' % username)
        logging.debug('Getting %s' % username)

        # Get the users animelist and id
        animelist = WebGrab.getAnimeList(username)
        userid = WebGrab.getUserId(username)

        # Get the user object
        user = self.getUserObject(userid, username)

        # Get the list of known ratings of this user
        query = Rating.gql('WHERE user = :1', user)

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
        ratings = []
        for rating in query:
            animeid = rating.anime.animeid

            if animeid in ratingMap:
                # Update to new score if there is one
                rating.rating = ratingMap[animeid]
                ratings.append(rating)

                # Delete the entry from the map to avoid it being
                # inserted later
                del ratingMap[animeid]
                del nameMap[animeid]
            else:
                # Otherwise, delete the rating to reflect that it is now
                # gone
                rating.delete()

        # Now insert new ratings
        animes = self.getAnimeObjects(nameMap)
        for anime in animes:
            # Generate the rating object
            rating = Rating()
            rating.user = user
            rating.anime = anime
            rating.rating = ratingMap[anime.animeid]
            ratings.append(rating)

        # Batch update the ratings
        db.put(ratings)

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

    def getAnimeObjects(self, namemap):
        ids   = namemap.keys()
        idSet = set(ids)

        # Get the list of existing objects from the database, batching
        # the maximum at a time
        MAX_PER_BATCH = 30
        objs = []
        for i in range(len(ids) / MAX_PER_BATCH + 1):
            if i * MAX_PER_BATCH >= len(ids):
                break

            query = Anime.gql('WHERE animeid IN :1', ids[i*MAX_PER_BATCH:
                                                         (i+1)*MAX_PER_BATCH])

            for anime in query:
                objs.append(anime)
                idSet.remove(anime.animeid)

        # Insert new objects for those not found
        newAnimes = []
        for animeid in idSet:
            anime = Anime()
            anime.animeid = animeid
            anime.name = namemap[animeid]
            objs.append(anime)
            newAnimes.append(anime)

        db.put(newAnimes)

        return objs 

    def getNextUser(self):
        query = QueueUser.gql('ORDER BY date')
        res = query.fetch(1)

        if res == []:
            return None
        else:
            username = res[0].username
            res[0].delete()
            return username
