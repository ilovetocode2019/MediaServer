import datetime

import tornado.web

from .base import BaseHandler


class SettingsInvitesHandler(BaseHandler):
    async def get_invites(self):
        query = """SELECT *
                   FROM invites;
                """
        records = await self.application.database.fetch(query)
        records = [dict(record) for record in records]

        invites = []

        for record in records:
            if (
                record["expires_at"]
                and record["expires_at"] <= datetime.datetime.utcnow()
            ):
                query = """DELETE FROM invites
                           WHERE invites.id=$1;
                        """
                await self.application.database.execute(query, record["id"])
                continue

            query = """SELECT *
                       FROM users
                       WHERE users.id=$1;
                    """
            creator = await self.application.database.fetchrow(
                query,
                record["user_id"]
            )

            record["creator"] = creator["username"]
            invites.append(record)

        return invites

    @tornado.web.authenticated
    async def get(self):
        if self.current_user["id"] != 1:
            raise tornado.web.HTTPError(
                403,
                "You don't have permissions to manage invites"
            )

        invites = await self.get_invites()
        self.render("invites.html", invites=invites, message=None)

    @tornado.web.authenticated
    async def post(self):
        action = self.get_argument("action")

        if action == "createInvite":
            raw_max_uses = self.get_argument("max_uses")
            raw_expires_in = self.get_argument("expires_in")

            try:
                max_uses = int(raw_max_uses)
            except Exception:
                raise tornado.web.HTTPError(
                    400,
                    "Max uses must be an integer"
                ) from None

            try:
                expires_in = int(raw_expires_in)
            except Exception:
                raise tornado.web.HTTPError(
                    400,
                    "Expires in must be an integer"
                ) from None

            if self.current_user["id"] != 1:
                raise tornado.web.HTTPError(
                    403,
                    "You don't have permissions to manage invites"
                )

            identifier = self.generate_random_string(legnth=8)
            while await self.get_invite(identifier):
                identifier = self.generate_random_string(legnth=8)

            expires_at = (
                datetime.datetime.utcnow() +
                datetime.timedelta(minutes=expires_in)
                if expires_in else None
            )

            query = """INSERT INTO invites (id, user_id, max_uses, expires_at)
                       VALUES ($1, $2, $3, $4);
                    """
            await self.application.database.execute(
                query,
                identifier, self.current_user["id"], max_uses, expires_at
            )

            invites = await self.get_invites()
            self.render(
                "invites.html",
                invites=invites,
                message="Successfully created invite",
                color="green"
            )

        elif action == "deleteInvite":
            invite_id = self.get_argument("invite_id")

            query = """DELETE FROM invites
                       WHERE invites.id=$1;
                    """
            await self.application.database.execute(query, invite_id)

            invites = await self.get_invites()
            self.render(
                "invites.html",
                invites=invites,
                message="Successfully deleted invite",
                color="green"
            )
