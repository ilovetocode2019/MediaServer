import os
import tornado.web

from .base import BaseHandler


class FilesHandler(BaseHandler):
    async def get_files(self):
        query = """SELECT *
                   FROM files
                   WHERE files.user_id=$1
                   ORDER BY files.created_at DESC;
                """
        records = await self.application.database.fetch(
            query,
            self.current_user["id"]
        )
        records = [dict(record) for record in records]

        files = []

        for record in records:
            record["path"] = os.path.join(
                "static",
                "uploads",
                record["filename"]
            )
            files.append(record)

        return files

    @tornado.web.authenticated
    async def get(self):
        raw_page = self.get_argument("page", "1")
        current_page = int(raw_page) if raw_page.isdigit() else 0

        per_page = 12
        start = (current_page - 1) * per_page
        end = current_page * per_page

        files = await self.get_files()
        pages = int(len(files) / per_page) + 1

        if current_page < 1 or current_page > pages:
            self.redirect("?page=1")

        self.render(
            "files.html",
            files=files[start:end],
            pages=pages,
            current_page=current_page
        )

    @tornado.web.authenticated
    async def post(self):
        action = self.get_argument("action")
        raw_page = self.get_argument("page", 1)
        page = int(raw_page)

        per_page = 12
        start = (page - 1) * per_page
        end = page * per_page

        if action == "deleteFile":
            file_id = self.get_argument("file_id")
            file = await self.get_file(file_id)

            if not file:
                raise tornado.web.HTTPError(404, "This file doesn't exist")

            if file["user_id"] != self.current_user["id"]:
                raise tornado.web.HTTPError(403, "You don't own this file")

            query = """DELETE FROM files
                       WHERE files.id=$1;
                    """
            await self.application.database.execute(query, file_id)

            files = await self.get_files()
            self.render(
                "files.html",
                files=files[start:end],
                pages=int(len(files) / per_page) + 1,
                current_page=page
            )
