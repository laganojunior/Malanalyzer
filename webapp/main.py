from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from Extractor import Extractor
from Index import Index
from FillQueue import FillQueue

# Profile mode. Can be "Print", "Log", or "None"
PROFILE = "None"

def main():
    application = webapp.WSGIApplication(
                                     [('/extract', Extractor),
                                      ('/fillqueue', FillQueue),
                                      ('/', Index)],
                                     debug=True)
    run_wsgi_app(application)

if __name__ == "__main__":
    if PROFILE == "Print":
        import cProfile, pstats
        prof = cProfile.Profile()
        prof = prof.runctx("main()", globals(), locals())
        print "<pre>"
        stats = pstats.Stats(prof)
        stats.sort_stats("cumulative")  # Or cumulative
        stats.print_stats()  # 80 = how many to print
        print "</pre>" 
    elif PROFILE == "Log":
        import cProfile, pstats, StringIO, logging
        prof = cProfile.Profile()
        prof = prof.runctx("main()", globals(), locals())
        stream = StringIO.StringIO()
        stats = pstats.Stats(prof, stream=stream)
        stats.sort_stats("cumulative")  # Or cumulative
        stats.print_stats()  # 80 = how many to print
        # The rest is optional.
        logging.info("Profile data:\n%s", stream.getvalue())
    else:
        main()
