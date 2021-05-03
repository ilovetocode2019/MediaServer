import os
import random
import string
import sys

import asyncpg
import bcrypt
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.locks
import tornado.options
import tornado.web

import handlers

tornado.options.define("title", default="Media Server", help="The title for the media server")
tornado.options.define("domain", default="localhost", help="The domain for the server")
tornado.options.define("port", default=8080, type=int, help="The port to run the server on")
tornado.options.define("ssl_enabled", default=True, type=bool, help="Whether to enable ssl (https support)")
tornado.options.define("url_legnth", default=4, type=int, help="The URL legnth for uploaded files")
tornado.options.define("database_uri", help="The URI for the postgresql database")
tornado.options.define("cookie_secret", help="The cookie secret for storing secure cookies")
tornado.options.define("debug", default=False, type=bool, help="Whether to run the server in debug mode")


async def create_tables(database):
    with open("schema.sql") as file:
        schema = file.read()
        await database.execute(schema)

    query = """SELECT *
               FROM users;
            """
    user = await database.fetchrow(query)

    if not user:
        password = "".join(
            random.choice(string.ascii_letters+string.digits)
            for x in range(8)
        )
        password = tornado.escape.utf8(password)
        hashed_password = await tornado.ioloop.IOLoop.current(
        ).run_in_executor(None, bcrypt.hashpw, password, bcrypt.gensalt())

        query = """INSERT INTO users (username, hashed_password)
                   VALUES ($1, $2);
                """
        await database.execute(
            query,
            "Admin",
            tornado.escape.to_unicode(hashed_password)
        )

        print(
            "The admin user has been created with the username Admin "
            f"and the password {tornado.escape.to_unicode(password)}. "
            "You can change your username and password on the settings page.",
            file=sys.stderr
        )


class Application(tornado.web.Application):
    def __init__(self, database):
        handler_urls = [
            (r"/", handlers.FilesHandler),
            (r"/profile", handlers.ProfileHandler),
            (r"/setup", handlers.SetupHandler),
            (r"/upload", handlers.UploadHandler),
            (r"/gallery", handlers.GalleryHandler),
            (r"/settings/users", handlers.SettingsUsersHandler),
            (r"/settings/invites", handlers.SettingsInvitesHandler),
            (r"/auth/login", handlers.AuthLoginHandler),
            (r"/auth/logout", handlers.AuthLogoutHandler),
            (r"/api/files", handlers.api.FilesHandler),
            (r"/api/text", handlers.api.TextHandler),
            (r"/api/links", handlers.api.LinksHandler),
            (r"/api/download", handlers.api.DownloadHandler),
            (r"/file/(.*)", handlers.FileHandler),
            (r"/invite/(.*)", handlers.InviteHandler),
            (
                r"/(.*)",
                handlers.StaticHandler,
                {
                    "path": os.path.join(
                        os.path.dirname(__file__),
                        "static",
                        "uploads"
                    )
                }
            )
        ]

        settings = dict(
            app_title=tornado.options.options.title,
            template_path=os.path.join(
                os.path.dirname(__file__),
                "templates"
            ),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            cookie_secret=tornado.options.options.cookie_secret,
            login_url="/auth/login",
            debug=tornado.options.options.debug,
        )

        super().__init__(handler_urls, **settings)
        self.database = database
        self.url_legnth = tornado.options.options.url_legnth

    @property
    def url(self):
        protocol = "https" if tornado.options.options.ssl_enabled else "http"
        port = tornado.options.options.port
        display_port = "" if port in (80, 443) else f":{port}"

        return f"{protocol}://{tornado.options.options.domain}{display_port}"


async def main():
    tornado.options.parse_command_line()
    tornado.options.options.parse_config_file("app.conf")

    async with asyncpg.create_pool(
        tornado.options.options.database_uri
    ) as database:
        await create_tables(database)

        ssl_options = {
            "certfile": os.path.join(os.path.dirname(__file__), "cert.pem"),
            "keyfile": os.path.join(os.path.dirname(__file__), "key.pem"),
        }

        if not tornado.options.options.ssl_enabled:
            ssl_options = None

        app = Application(database)
        server = tornado.httpserver.HTTPServer(app, ssl_options=ssl_options)
        server.listen(tornado.options.options.port)

        shutdown = tornado.locks.Event()
        await shutdown.wait()

if __name__ == "__main__":
    tornado.ioloop.IOLoop.current().run_sync(main)
