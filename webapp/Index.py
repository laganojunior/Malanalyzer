from google.appengine.ext import webapp

class Index(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'

        self.response.out.write("Hello")

