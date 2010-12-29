from google.appengine.ext import db

class User(db.Model):
    userid = db.IntegerProperty()
    name = db.StringProperty()

class Anime(db.Model):
    animeid = db.IntegerProperty()
    name = db.StringProperty()

class Rating(db.Model):
    user = db.ReferenceProperty(User)
    anime = db.ReferenceProperty(Anime)
    rating = db.IntegerProperty()

class QueueUser(db.Model):
    username = db.StringProperty()
    date = db.DateTimeProperty(auto_now_add=True)
