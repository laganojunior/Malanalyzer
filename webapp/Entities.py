from google.appengine.ext import db

class User(db.Model):
    name = db.StringProperty(indexed=False)

class Anime(db.Model):
    name = db.StringProperty(indexed=False)

class Rating(db.Model):
    user = db.ReferenceProperty(User)
    anime = db.ReferenceProperty(Anime)
    rating = db.IntegerProperty(indexed=False)

class QueueUser(db.Model):
    username = db.StringProperty()
    date = db.DateTimeProperty(auto_now_add=True)
