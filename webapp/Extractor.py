from google.appengine.ext import webapp

import WebGrab
from Entities import *

import logging

class Extractor(webapp.RequestHandler):
    def post(self):
        self.response.headers['Content-Type'] = 'text/html'

        username = self.request.get('username')

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
                nameMap[str(animeid)]   = anime['title']

        # Insert the user and anime objects if needed
        user   = self.getNewUserObject(userid, username)
        animes = self.getNewAnimeObjects(nameMap)

        if user:
            newInsert = animes + [user]
        else:
            newInsert = animes

        # Now insert new ratings
        ratings = [0] * len(ratingMap)

        for i, animeid in enumerate(nameMap):
            # Generate the rating object
            rating = Rating(key_name=str(userid) + "_" + animeid)
            rating.userid = userid
            rating.animeid = int(animeid)
            rating.rating = ratingMap[animeid]
            ratings[i] = rating

        # Batch update everything
        db.put(ratings + newInsert)

    def getNewUserObject(self, userid, username):
        # Check if the user is already in the database
        user = User.get_by_key_name(str(userid))

        if not user:
            user = User(key_name=str(userid))
            user.name = username
            user.userid = userid
            return user
        else:
            return None

        return user

    def getNewAnimeObjects(self, namemap):
        ids = namemap.keys()
        animes = Anime.get_by_key_name(ids)

        # Fill in the ones that have not been inserted yet
        newAnime = []
        for i, anime in enumerate(animes):
            if anime is None:
                anime = Anime(key_name = ids[i])
                anime.name = namemap[ids[i]]
                newAnime.append(anime) 

        return newAnime
