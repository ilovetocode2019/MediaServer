
import os
import random
import string

import bcrypt
import traceback
import tornado.escape
import tornado.ioloop
import tornado.locks
import tornado.web


class BaseHandler(tornado.web.RequestHandler):
    async def prepare(self):
        self.current_user = None

        raw_username = self.get_secure_cookie("username")
        raw_password = self.get_secure_cookie("password")

        username = tornado.escape.to_unicode(raw_username)
        password = tornado.escape.to_unicode(raw_password)

        if username and password:
            query = """SELECT *
                       FROM users
                       WHERE users.username=$1;
                    """
            record = await self.application.database.fetchrow(query, username)

            if (
                record
                and await self.check_password(
                    password,
                    record["hashed_password"]
                )
            ):
                self.current_user = dict(record)
                self.current_user["password"] = password

    def write_error(self, status_code, **kwargs):
        if status_code == 404:
            self.render("errors/404.html")
        elif self.settings.get("serve_traceback") and "exc_info" in kwargs:
            formatted_exc = traceback.format_exception(*kwargs["exc_info"])
            self.render("errors/exception.html", formatted=formatted_exc)
        else:
            self.render(
                "errors/any.html",
                status_code=status_code,
                reason=self._reason
            )

    async def hash_password(self, password):
        password = tornado.escape.utf8(password)

        hashed_password = await tornado.ioloop.IOLoop.current(
        ).run_in_executor(None, bcrypt.hashpw, password, bcrypt.gensalt())
        return tornado.escape.to_unicode(hashed_password)

    async def check_password(self, password, hashed_password):
        password = tornado.escape.utf8(password)
        hashed_password = tornado.escape.utf8(hashed_password)

        checked = await tornado.ioloop.IOLoop.current(
        ).run_in_executor(None, bcrypt.checkpw, password, hashed_password)
        return checked

    def generate_random_string(self, legnth=None):
        legnth = self.application.url_legnth
        return "".join(
            random.choice(string.ascii_letters+string.digits)
            for x in range(legnth)
        )

    async def get_file(self, file_id):
        query = """SELECT *
                   FROM files
                   WHERE files.id=$1;
                """
        record = await self.application.database.fetchrow(query, file_id)
        file = dict(record) if record else None

        if not file:
            return None

        query = """SELECT *
                   FROM users
                   WHERE users.id=$1;
                """
        record = await self.application.database.fetchrow(
            query,
            file["user_id"]
        )
        user = dict(record) if record else None

        file["uploader"] = user["username"] if user else None
        file["path"] = os.path.join("static", "uploads", file["filename"])

        return file

    async def get_invite(self, invite_id):
        query = """SELECT *
                   FROM invites
                   WHERE invites.id=$1;
                """
        record = await self.application.database.fetchrow(query, invite_id)
        invite = dict(record) if record else None

        if not invite:
            return

        query = """SELECT *
                   FROM users
                   WHERE users.id=$1;
                """
        record = await self.application.database.fetchrow(
            query,
            invite["user_id"]
        )
        user = dict(record) if record else None

        invite["creator"] = user["username"] if user else None

        return invite
