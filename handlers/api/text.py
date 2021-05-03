import tornado.web

from handlers.base import BaseHandler


class TextHandler(BaseHandler):
    async def post(self):
        username = self.get_argument("username")
        password = self.get_argument("password")
        text = self.get_argument("text")

        if any([not field for field in [username, password]]):
            raise tornado.web.HTTPError(
                400,
                "Both username and password need to be provided"
            )

        if not text:
            raise tornado.web.HTTPError(
                400,
                "Text to upload must be specified"
            )

        query = """SELECT *
                   FROM users
                   WHERE users.username=$1;
                """
        user = await self.application.database.fetchrow(query, username)
        if not user:
            raise tornado.web.HTTPError(
                400,
                "Invalid username"
            )

        password_valid = await self.check_password(
            password,
            user["hashed_password"]
        )
        if not password_valid:
            raise tornado.web.HTTPError(
                400,
                "Invalid password"
            )

        identifier = self.generate_random_string()
        while await self.get_file(identifier):
            identifier = self.generate_random_string()

        filename = f"{identifier}.txt"
        with open(f"static/uploads/{filename}", "w") as file:
            file.write(text)

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
