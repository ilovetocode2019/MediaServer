
import tornado.web

from .base import BaseHandler


class UploadHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render("upload.html", message=None)

    @tornado.web.authenticated
    async def post(self):
        filedata = self.request.files.get("filedata")

        if not filedata:
            self.render(
                "upload.html",
                message="Please select a file",
                color="#ff5349"
            )
            return

        for data in filedata:
            filename, extension = data.get("filename").split(".", 1)
            body = data.get("body")

            identifier = self.generate_random_string()
            while await self.get_file(identifier):
                identifier = self.generate_random_string()

            filename = f"{identifier}.{extension}"
            with open(f"static/uploads/{filename}", "wb") as file:
                file.write(body)

            query = """INSERT INTO files (id, filename, user_id)
                       VALUES ($1, $2, $3);
                    """
            await self.application.database.execute(
                query,
                identifier,
                filename,
                self.current_user["id"]
            )

        self.redirect(f"/file/{identifier}")
