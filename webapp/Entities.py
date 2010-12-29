from google.appengine.ext import db

class User(db.Model):
    userid = db.IntegerProperty()
    name = db.StringProperty(indexed=False)

class Anime(db.Model):
    animeid = db.IntegerProperty()
    name = db.StringProperty(indexed=False)

class Rating(db.Model):
    user = db.ReferenceProperty(User)
    anime = db.ReferenceProperty(Anime)
    rating = db.IntegerProperty(indexed=False)

class QueueUser(db.Model):
    username = db.StringProperty()
    date = db.DateTimeProperty(auto_now_add=True)
