from google.appengine.ext import webapp

class Index(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'

        self.response.out.write("<html><body>\n")
        self.response.out.write("""<form action='/insertusername'
                                         method='post'""")
        self.response.out.write("Enter Username:")
        self.response.out.write("<input type='text' name='username'")
        self.response.out.write("<input type='submit'>")

        self.response.out.write("</form></body></html>\n")
