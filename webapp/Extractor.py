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
        for anime in animelist:
            animeid   = anime['id']
            rating    = anime['score']

            ratingSum += rating
            ratingSumSquares += rating * rating

            nameMap[str(animeid)]   = anime['title']

        mean = rating / len(animelist)
        stddev = math.sqrt((ratingSumSquares / len(animelist)) - mean * mean)

        # Normalize all ratings
        if stddev < 0.1:
            # Standard deviation seems to indicate no variance, so set
            # all the animes to the same occurence
            for anime in animelist:
                ratingMap[str(anime['id'])] = 1.0
        else:
            for anime in animelist:
                rating = anime['score']
                animeid = str(anime['id'])
                if rating == 0:
                    # No rating
                    ratingMap[animeid] = 1.0
                else:
                    ratingMap[animeid] = 2.0 * math.exp((rating - mean) / stddev)

        # Get anime objects, creating new ones if necessary
        animes = self.getAnimeObjects(nameMap)

        # Get all topic objects, making new ones as needed
        topics = self.getTopicObjects(ratingMap.keys(), animes)

        # Deserialize the topic maps
        topicMaps = [0] * len(topics)
        for i, topic in enumerate(topics):
            topicMaps[i] = eval(str(topic.animes))

        # Get the topic weights for this user
        topicWeights = [0.000001] * len(topics)
        for i, topic in enumerate(topics):
            for animeid in ratingMap:
                if animeid in topicMaps[i]:
                    topicWeights[i] += topicMaps[i][animeid] *\
                                       ratingMap[animeid]

        # Smooth out the topics a bit and normalize
        topicWeightSum = sum(topicWeights)
        for i, weight in enumerate(topicWeights):
            topicWeights[i] += random.uniform(0, .1 / topicWeightSum)

        topicWeightSum = sum(topicWeights)
        for i, weight in enumerate(topicWeights):
            topicWeights[i] /= topicWeightSum

        # Move the topic weight proportion a little toward this user
        for i, topic in enumerate(topics):
            topic.weight = topic.weight * (1.0 - LEARNING_RATE) +\
                           topicWeights[i] * LEARNING_RATE

        # Redo topic->anime weights
        for i, topic in enumerate(topics):
            newTopicMap = {}
            weightSum = 0.0
            for animeid in ratingMap:
                if animeid in topicMaps[i]:
                    newTopicMap[animeid] = topicMaps[i][animeid]\
                                           * ratingMap[animeid]
                else:
                    newTopicMap[animeid] = THRESHOLD_WEIGHT * .9\
                                           * ratingMap[animeid]
                weightSum += newTopicMap[animeid]

            # Normalize new topics
            for animeid in newTopicMap:
                newTopicMap[animeid] /= weightSum
 
            # Push the topic proportions a little
            topicMap = topicMaps[i]
            finalTopicMap = {}
            keyUnion = set(topicMap.keys()) | set(newTopicMap.keys())
            weightSum = 0.0
            modLearningRate = LEARNING_RATE * topicWeights[i]\
                                                * MAX_TOPICS
            for animeid in keyUnion:
                weight  = 0.0
                if animeid in topicMap.keys():
                    weight += topicMap[animeid] * (1.0 - modLearningRate)

                if animeid in newTopicMap.keys():
                    weight += newTopicMap[animeid] * modLearningRate

                if weight < THRESHOLD_WEIGHT:
                    weight = 0.0
                else:
                    finalTopicMap[animeid] = weight
                    weightSum += weight

            # Normalize the finalized map
            for animeid in finalTopicMap:
                finalTopicMap[animeid] /= weightSum

            # Write the final map
            topic.animes = db.Blob(str(finalTopicMap))

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
        weightTotal = 0.0
        newTopicsAdded = False
        for i, topic in enumerate(topics):
            if topic is None:
                newTopicsAdded = True

                topic = Topic(key_name = ids[i])
                topic.weight = 1.0 / MAX_TOPICS

                # Choose a random bunch of animes and proportionally
                # choose between them
                if len(animeids) > MAX_ANIMES_IN_NEW_TOPIC:
                    chosen = random.sample(animeids, MAX_ANIMES_IN_NEW_TOPIC)
                else:
                    chosen = animeids

                # Update the new anime map
                new_anime_map = {}
                for j in chosen:
                    new_anime_map[j] = 1.0 / MAX_ANIMES_IN_NEW_TOPIC
 
                topic.animes = db.Blob(str(new_anime_map))
                topics[i] = topic

            weightTotal += topic.weight

        # Renormalize weights
        if newTopicsAdded:
            for i, topic in enumerate(topics):
                topic.weight /= weightTotal

        return topics
