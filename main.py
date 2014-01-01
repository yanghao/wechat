import logging
import webapp2

from view import WeChatView
from view import Not_Found

urls = [ (r'/?', WeChatView),
         (r'/.*', Not_Found),
]

logging.basicConfig(level=logging.INFO)

application = webapp2.WSGIApplication(urls, debug=True)
