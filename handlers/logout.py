from .base import BaseHandler


class AuthLogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("username")
        self.clear_cookie("password")
        self.redirect("/")
