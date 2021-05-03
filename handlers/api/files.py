import tornado.web

from handlers.base import BaseHandler


class FilesHandler(BaseHandler):
    async def post(self):
        username = self.get_argument("username")
        password = self.get_argument("password")

        if any(not field for field in [username, password]):
            raise tornado.web.HTTPError(400, "All fileds need to be filled")

        query = """SELECT *
                   FROM users
                   WHERE users.username=$1;
                """
        user = await self.application.database.fetchrow(query, username)
        if not user:
            raise tornado.web.HTTPError(400, "Invalid username")

        password_valid = await self.check_password(
            password,
            user["hashed_password"]
        )
        if not password_valid:
            raise tornado.web.HTTPError(400, "Invalid password")

        filedata = self.request.files.get("filedata")
        if not filedata:
            raise tornado.web.HTTPError(400, "No filedata found")

        for data in filedata:
            splitted = data.get("filename").split(".", 1)
            filename = splitted[0]
            extension = f".{splitted[1]}" if len(splitted) == 2 else ""

            body = data.get("body")

            if any(not field for field in [filename, body]):
                raise tornado.web.HTTPError(
                    400,
                    "Filedata must have a name and body"
                )

            identifier = self.generate_random_string()
            while await self.get_file(identifier):
                identifier = self.generate_random_string()

            filename = f"{identifier}{extension}"
            with open(f"static/uploads/{filename}", "wb") as file:
                file.write(body)

            query = """INSERT INTO files (id, filename, user_id)
                       VALUES ($1, $2, $3);
                    """
            await self.application.database.execute(
                query,
                identifier,
                filename,
                user["id"]
            )

        self.write(f"{self.application.url}/{filename}")
