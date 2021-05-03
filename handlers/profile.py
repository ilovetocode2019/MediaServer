import tornado.web

from .base import BaseHandler


class ProfileHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render(
            "profile.html",
            current_user=self.current_user,
            message=None
        )

    @tornado.web.authenticated
    async def post(self):
        action = self.get_argument("action")

        if action == "changeUsername":
            username = self.get_argument("username")

            query = """SELECT *
                       FROM users
                       WHERE users.username=$1;
                    """
            user = await self.application.database.fetchrow(query, username)

            if user:
                self.render(
                    "profile.html",
                    current_user=self.current_user,
                    message="Username is already taken",
                    color="#ff5349"
                )
                return

            query = """UPDATE users
                       SET username=$1
                       WHERE users.id=$2;
                    """
            await self.application.database.execute(
                query,
                username,
                self.current_user["id"]
            )

            self.current_user["username"] = username
            self.render(
                "profile.html",
                current_user=self.current_user,
                message="Username successfully updated",
                color="green"
            )

        elif action == "changePassword":
            password = self.get_argument("password")
            hashed_password = await self.hash_password(password)

            query = """UPDATE users
                       SET hashed_password=$1
                       WHERE users.id=$2;
                    """
            await self.application.database.execute(
                query,
                hashed_password,
                self.current_user["id"]
            )

            self.current_user["hashed_password"] = hashed_password
            self.render(
                "profile.html",
                current_user=self.current_user,
                message="Password successfully updated",
                color="green"
            )

        elif action == "deleteAccount":
            if self.current_user["id"] == 1:
                self.render(
                    "profile.html",
                    current_user=self.current_user,
                    message="The Admin user can't be deleted",
                    color="#ff5349"
                )
                return

            query = """DELETE FROM files
                       WHERE files.user_id=$1;
                    """
            await self.application.database.execute(
                query,
                self.current_user["id"]
            )

            query = """DELETE FROM invites
                       WHERE invites.user_id=$1;
                    """
            await self.application.database.execute(
                query,
                self.current_user["id"]
            )

            query = """DELETE FROM users
                       WHERE users.id=$1;
                    """
            await self.application.database.execute(
                query,
                self.current_user["id"]
            )

            self.clear_cookie("username")
            self.clear_cookie("password")
            self.redirect("/")
