from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from Extractor import Extractor
from Index import Index


if __name__ == "__main__":
    application = webapp.WSGIApplication(
                                     [('/extract', Extractor),
                                      ('/', Index)],
                                     debug=True)
    run_wsgi_app(application)
