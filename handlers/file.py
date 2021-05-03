import tornado.web

from .base import BaseHandler


class FileHandler(BaseHandler):
    async def get(self, file_id):
        file = await self.get_file(file_id)

        if not file:
            raise tornado.web.HTTPError(404, "File not found")

        self.render("file.html", file=file)

    @tornado.web.authenticated
    async def post(self, file_id):
        action = self.get_argument("action")

        if action == "deleteFile":
            file = await self.get_file(file_id)

            if not file:
                raise tornado.web.HTTPError(404, "This file doesn't exist")

            if (
                file.user_id != self.current_user["id"]
                and self.current_user["id"] != 1
            ):
                raise tornado.web.HTTPError(
                    403,
                    "You don't have permissions to delete this file"
                )

            await file.delete()
            self.redirect("/")
