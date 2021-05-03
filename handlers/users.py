import tornado.web

from handlers.base import BaseHandler


class SettingsUsersHandler(BaseHandler):
    async def get_users(self):
        query = """SELECT *
                   FROM users;
                """
        users = await self.application.database.fetch(query)
        return [dict(user) for user in users]

    @tornado.web.authenticated
    async def get(self):
        if self.current_user["id"] != 1:
            raise tornado.web.HTTPError(
                403,
                "You don't have permissions to manage users"
            )

        users = await self.get_users()
        self.render("users.html", users=users, message=None)

    @tornado.web.authenticated
    async def post(self):
        argument = self.get_argument("user_id")
        user_id = int(argument)

        if self.current_user["id"] != 1:
            raise tornado.web.HTTPError(
                403,
                "You don't have permissions to manage users"
            )

        if user_id == 1:
            users = await self.get_users()
            self.render(
                "users.html",
                users=users,
                message="The Admin user can't be deleted",
                color="#ff5349"
            )
            return

        query = """DELETE FROM files
                   WHERE files.user_id=$1;
                """
        await self.application.database.execute(query, user_id)

        query = """DELETE FROM invites
                   WHERE invites.user_id=$1;
                """
        await self.application.database.execute(query, user_id)

        query = """DELETE FROM users
                   WHERE users.id=$1;
                """
        await self.application.database.execute(query, user_id)

        if self.current_user["id"] == user_id:
            self.clear_cookie("username")
            self.clear_cookie("password")
            self.redirect("/")
            return

        users = await self.get_users()
        self.render(
            "users.html",
            users=users,
            message="Successfully deleted user",
            color="green"
        )
