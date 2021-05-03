from handlers.base import BaseHandler

SXCU_FILE = """
{{
    "Version": "13.3.0",
    "Name": "{name}",
    "DestinationType": "ImageUploader, FileUploader",
    "RequestMethod": "POST",
    "RequestURL": "{url}/api/files,
    "Parameters": {{
        "username": "{username}",
        "password": "{password}"
    }},
    "Headers": {{
    }},
    "Body": "MultipartFormData",
    "Arguments": {{
    }},
    "FileFormName": "filedata",
    "URL": "$json:url$",
    "ThumbnailURL": "$json:thumbnail_url$",
    "DeletionURL": "$json:deletion_url$",
    "ErrorMessage": "$json:error$"
}}
"""


class DownloadHandler(BaseHandler):
    async def get(self):
        username = self.get_argument("username", self.current_user["username"])
        password = self.get_argument("password", self.current_user["password"])
        app_title = self.settings["app_title"]

        filename = f"{app_title}.sxcu"
        content = SXCU_FILE.format(
            name=app_title,
            url=self.application.url,
            username=username,
            password=password,
        )

        self.set_header("Content-Type", "application/octet-stream")
        self.set_header(
            "Content-Disposition",
            f"attachment; filename={filename}"
        )
        self.write(content)
