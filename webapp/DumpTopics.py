from google.appengine.ext import webapp
from google.appengine.ext import db

from Entities import *

class DumpTopics(webapp.RequestHandler):

    def get(self):
        self.response.headers['Content-Type'] = 'text/html'

        # Get all topics and anime
        topics = Topic.all()
        animes  = Anime.all()

        # Create a mapping from animeid to name
        names = {}
        for anime in animes:
            names[anime.animeid] = anime.name

        # Now dump each topic by weight order
        for i, topic in enumerate(topics):
            self.response.out.write("<h1>Topic %d:%f</h1>" % (i, topic.weight))

            topicMap = eval(str(topic.animes))

            topicMapWeights = topicMap.items()
            topicMapWeights.sort(key = lambda x: x[1], reverse=True)

            self.response.out.write("<ul>")
            for (animeid, weight) in topicMapWeights:
                self.response.out.write("<li>%s: %f</li>" % (names[animeid],
                                                             weight))
                
            self.response.out.write("</ul>")
