from google.appengine.ext import db

MAX_TOPICS = 50
THRESHOLD_WEIGHT = .00001

class Anime(db.Model):
    animeid = db.StringProperty(indexed=False)
    name = db.StringProperty(indexed=False)

class Topic(db.Model):
    weight = db.FloatProperty(indexed=False)
    animes = db.BlobProperty(indexed=False)
