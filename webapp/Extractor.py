from google.appengine.ext import webapp
from google.appengine.ext import db

import WebGrab
from Entities import *

import logging
import random
import math

MAX_ANIMES_TO_USE = 500
MAX_ANIMES_IN_NEW_TOPIC = 50

LEARNING_RATE = .1
REGULARIZATION_FACTOR = .1

class Extractor(webapp.RequestHandler):
    def post(self):
        self.response.headers['Content-Type'] = 'text/html'

        username = self.request.get('username')

        self.response.out.write('Getting %s' % username)
        logging.debug('Getting %s' % username)

        # Get the users animelist and id
        animelist = WebGrab.getAnimeList(username)

        # Limit the number of animes to use
        if len(animelist) > MAX_ANIMES_TO_USE:
            animelist = random.sample(animelist, MAX_ANIMES_TO_USE)

        # Go through each rating in the new list and create a map from
        # id to rating
        ratingMap = {}
        nameMap   = {}
        ratingSum = 0.0
        ratingSumSquares = 0.0
        trueCount = 0
        for anime in animelist:
            animeid   = anime['id']
            rating    = anime['score']

            ratingSum += rating
            ratingSumSquares += rating * rating

            nameMap[str(animeid)]   = anime['title']

            if rating != 0:
                trueCount += 1

        if trueCount != 0: 
            mean = ratingSum / trueCount
            stddev = math.sqrt((ratingSumSquares / trueCount) - mean * mean)
        else:
            mean = 0
            stddev = 0

        # Normalize all ratings
        if stddev < 0.1:
            # Standard deviation seems to indicate no variance, so set
            # all the animes to the average
            for anime in animelist:
                ratingMap[str(anime['id'])] = 0.0
        else:
            for anime in animelist:
                rating = anime['score']
                animeid = str(anime['id'])
                if rating == 0:
                    # No rating, default to average
                    ratingMap[animeid] = 0.0
                else:
                    ratingMap[animeid] = (rating - mean) / stddev

        # Get anime objects, creating new ones if necessary
        animes = self.getAnimeObjects(nameMap)

        # Get all topic objects, making new ones as needed
        topics = self.getTopicObjects(ratingMap.keys(), animes)

        # Deserialize the topic maps
        topicMaps = [0] * len(topics)
        for i, topic in enumerate(topics):
            topicMaps[i] = eval(str(topic.animes))

        # Get the topic weights for this user
        topicWeights = [0.1] * len(topics)
        for i, topic in enumerate(topics):
            for animeid in ratingMap:
                if animeid in topicMaps[i]:
                    topicWeights[i] += topicMaps[i][animeid] *\
                                       ratingMap[animeid]

        # Normalize by averaging over all ratings
        for i, weight in enumerate(topicWeights):
            topicWeights[i] /= len(ratingMap)

        # Now using the user weights, calculate error predictions from all
        # ratings
        ratingErrors = {}
        for animeid in ratingMap:
            ratingSum = 0.0
            for i, weight in enumerate(topicWeights):
                if animeid in topicMaps[i]:
                    ratingSum += weight * topicMaps[i][animeid]

            ratingErrors[animeid] = ratingSum - ratingMap[animeid]

        # Move the topic->anime weights using gradient descent
        for i, topic in enumerate(topics):

            key_union = set(ratingErrors.keys()) | set(topicMaps[i].keys())
            for animeid in key_union:
                if animeid not in topicMaps[i]:
                    topicMaps[i][animeid] = 0.0

                if animeid not in ratingErrors:
                    ratingErrors[animeid] = 0.0

                topicMaps[i][animeid] -= LEARNING_RATE * \
                                (ratingErrors[animeid] * topicWeights[i] + \
                                 REGULARIZATION_FACTOR * topicMaps[i][animeid])

                # Make sure the weight meets the threshold for keeping it
                if abs(topicMaps[i][animeid]) < THRESHOLD_WEIGHT:
                    del topicMaps[i][animeid]
 
            # Write the final map
            topic.animes = db.Blob(str(topicMaps[i]))

        # Batch update everything
        db.put(animes + topics)

    def getAnimeObjects(self, namemap):
        ids = namemap.keys()
        animes = Anime.get_by_key_name(ids)

        # Fill in the ones that have not been inserted yet
        for i, anime in enumerate(animes):
            if anime is None:
                anime = Anime(key_name = ids[i])
                anime.name = namemap[ids[i]]
                anime.animeid = ids[i]
                animes[i] = anime

        return animes

    def getTopicObjects(self, animeids, animeobjs):
        ids = [str(x) for x in range(MAX_TOPICS)]
        topics = Topic.get_by_key_name(ids)

        # Fill in the ones that have not been created yet, with random
        # choices from the group
        for i, topic in enumerate(topics):
            if topic is None:
                topic = Topic(key_name = ids[i])

                # Choose a random bunch of animes and proportionally
                # choose between them
                if len(animeids) > MAX_ANIMES_IN_NEW_TOPIC:
                    chosen = random.sample(animeids, MAX_ANIMES_IN_NEW_TOPIC)
                else:
                    chosen = animeids

                # Update the new anime map
                new_anime_map = {}
                for j in chosen:
                    new_anime_map[j] = random.uniform(-.1, .1)
 
                topic.animes = db.Blob(str(new_anime_map))
                topics[i] = topic

        return topics
