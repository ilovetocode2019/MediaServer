import tornado.web

from .base import BaseHandler


class SetupHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render("setup.html", username=self.current_user["username"])
