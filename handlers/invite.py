import asyncpg
import datetime

import tornado.web

from .base import BaseHandler


class InviteHandler(BaseHandler):
    async def get(self, code):
        query = """SELECT *
                   FROM invites
                   WHERE invites.id=$1;
                """
        invite = await self.application.database.fetchrow(query, code)

        if not invite:
            raise tornado.web.HTTPError(404, "Invite is invalid or expired")

        if invite["expires_at"] <= datetime.datetime.utcnow():
            query = """DELETE FROM invites
                       WHERE invites.id=$1;
                    """
            await self.application.database.execute(query, invite["id"])

            raise tornado.web.HTTPError(404, "Invite has expired")

        self.render("invite.html", code=code, message=None)

    async def post(self, code):
        username = self.get_argument("username")
        password = self.get_argument("password")

        query = """SELECT *
                   FROM invites
                   WHERE invites.id=$1;
                """
        invite = await self.application.database.fetchrow(query, code)

        if not invite:
            raise tornado.web.HTTPError(404, "Invite is invalid or expired")

        if (
            invite["expires_at"]
            and invite["expires_at"] <= datetime.datetime.utcnow()
        ):
            query = """DELETE FROM invites
                       WHERE invites.id=$1;
                    """
            await self.application.database.execute(query, invite["id"])

            self.render(
                "invite.html",
                code=code,
                message="Invite has expired",
                color="#ff5349"
            )
            return

        hashed_password = await self.hash_password(password)

        query = """INSERT INTO users (username, hashed_password)
                   VALUES ($1, $2)
                   RETURNING id;
                """

        try:
            await self.application.database.fetchval(
                query,
                username,
                hashed_password
            )
        except asyncpg.UniqueViolationError:
            self.render(
                "invite.html",
                code=code,
                message="This username is already registered",
                color="#ff5349"
            )
            return

        if invite["uses"]+1 == invite["max_uses"]:
            query = """DELETE FROM invites
                       WHERE invites.id=$1;
                    """
            await self.application.database.execute(query, invite["id"])
        else:
            query = """UPDATE invites
                       SET invites.uses=$1
                       WHERE invites.id=$2;
                    """
            await self.application.database.execute(
                query,
                invite["uses"] + 1,
                invite["id"]
            )

        self.set_secure_cookie("username", username)
        self.set_secure_cookie("password", password)
        self.redirect("/setup")
