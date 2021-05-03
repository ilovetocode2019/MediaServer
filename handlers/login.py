from .base import BaseHandler


class AuthLoginHandler(BaseHandler):
    def get(self):
        self.render("login.html", message=None)

    async def post(self):
        username = self.get_argument("username")
        password = self.get_argument("password")

        if any(not field for field in [username, password]):
            self.render(
                "login.html",
                message="Please fill out all the fields",
                color="#ff5349"
            )
            return

        query = """SElECT *
                   FROM users
                   WHERE users.username=$1;
                """
        user = await self.application.database.fetchrow(query, username)

        if not user:
            self.render(
                "login.html",
                message="Username is not registered",
                color="#ff5349"
            )
            return

        password_valid = await self.check_password(
            password,
            user["hashed_password"]
        )
        if not password_valid:
            self.render(
                "login.html",
                message="Password is invalid",
                color="#ff5349"
            )
            return

        self.set_secure_cookie("username", username)
        self.set_secure_cookie("password", password)
        self.redirect("/")
