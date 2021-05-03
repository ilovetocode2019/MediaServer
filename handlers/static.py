import os

import tornado.web
import tornado.ioloop

from .base import BaseHandler


class StaticHandler(BaseHandler, tornado.web.StaticFileHandler):
    async def increase_view_count(self, filename):
        query = """UPDATE files
                   SET views=views + 1
                   WHERE files.filename=$1;
                """
        await self.application.database.execute(query, filename)

    def find_match(self, identifier):
        path = os.path.abspath(self.root)

        for filename in os.listdir(path):
            if filename.split(".")[0] == identifier:
                return filename

    def parse_url_path(self, url_path):
        if "." not in url_path:
            filename = self.find_match(url_path) or url_path
        else:
            filename = url_path

        tornado.ioloop.IOLoop.current().add_callback(
            self.increase_view_count,
            filename
        )
        return filename
