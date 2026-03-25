# Name: HookUsername
# Description: хук юзернейма
# authors: @neistv 
# version: 1.0.0
# meta developer: @latexmods
# meta banner: https://github.com/neistv/mods/raw/main/assets/HookUsername.jpg
import io
import logging
import re
import requests
from telethon.tl import functions
from telethon.tl.types import InputChatUploadedPhoto
from herokutl.types import Message

from .. import loader, utils

logging.basicConfig(level=logging.INFO)

@loader.tds
class HookUsername(loader.Module):
    """хук юзернейма"""

    strings = {"name": "HookUsername"}

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "channel_title",
                "Этот юзернейм зарезервирован.",
                "название канала при захвате юзернейма",
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "channel_about",
                "",
                "описание канала при захвате юзернейма",
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "channel_avatar_url",
                "https://raw.githubusercontent.com/neistv/mods/main/assets/rezerv.png",
                "ссылка на аватарку канала",
                validator=loader.validators.String(),
            ),
        )

    async def client_ready(self, client, db):
        self._db = db
        self._client = client

    async def _check(self, username: str) -> bool:
        try:
            return await self._client(
                functions.account.CheckUsernameRequest(username=username)
            )
        except Exception as e:
            logging.exception(f"ошибка при проверке юзернейма {username}: {e}")
            return False

    async def _grab_username(self, username: str) -> tuple[bool, str]:
        try:
            result = await self._client(
                functions.channels.CreateChannelRequest(
                    title=self.config["channel_title"],
                    about=self.config["channel_about"],
                    megagroup=False,
                )
            )
            channel = result.chats[0]

            await self._client(
                functions.channels.UpdateUsernameRequest(
                    channel=channel,
                    username=username,
                )
            )

            avatar_url = self.config["channel_avatar_url"].strip()
            if avatar_url:
                try:
                    resp = await utils.run_sync(requests.get, avatar_url, allow_redirects=True)
                    img_bytes = resp.content
                    buf = io.BytesIO(img_bytes)
                    buf.name = "avatar.png"
                    uploaded = await self._client.upload_file(buf)
                    await self._client(
                        functions.channels.EditPhotoRequest(
                            channel=channel,
                            photo=InputChatUploadedPhoto(file=uploaded),
                        )
                    )
                    
                   
                    async for msg in self._client.iter_messages(channel, limit=10):
                        if msg.action:
                            await msg.delete()
                            
                except Exception as e:
                    logging.warning(f"ошибка с аватаркой: {e}")

            return True, f"t.me/{username}"
        except Exception as e:
            logging.exception(f"Ошибка при захвате: {e}")
            return False, str(e)

    @loader.command(ru_doc="<юзернейм> — проверяет доступность юзернейма")
    async def uz(self, message: Message):
        """<юзернейм> - проверяет доступность юзернейма"""
        args = utils.get_args_raw(message).strip().lstrip("@")

        if not args:
            await utils.answer(message, "<b>укажи юзак!!</b>")
            return

        # Проверка на наличие русских букв (кириллицы)
        if re.search(r'[а-яА-ЯёЁ]', args):
            await utils.answer(message, "<b><tg-emoji emoji-id=5220197908342648622>❗️</tg-emoji>в юзернейме не может быть русских букв!!</b>")
            return

        available = await self._check(args)

        if available:
            await self.inline.form(
                text=(
                    f"юзак <b>@{args}</b> — свободен!!!\n\n"
                    f"хочешь занять этот юзернейм?"
                ),
                message=message,
                reply_markup=[
                    [
                        {"text": "✔ занять", "callback": self._grab_cb, "args": (args,)},
                        {"text": "✖", "callback": self._close_cb}
                    ]
                ],
            )
        else:
            await self.inline.form(
                text=(
                    f"<tg-emoji emoji-id='5220197908342648622'>❗️</tg-emoji> "
                    f"<b>@{args}</b> — занят."
                ),
                message=message,
                reply_markup=[
                    [{"text": "✖ закрыть", "callback": self._close_cb}]
                ],
            )

    async def _grab_cb(self, call, username: str):
        await call.answer("Захватываю...", show_alert=False)
        success, info = await self._grab_username(username)

        if success:
            await call.edit(
                f"<tg-emoji emoji-id='5219901967916084166'>💥</tg-emoji> "
                f"<b>@{username}</b> успешно занят!\n\n"
                f"Канал: {info}",
                reply_markup=[[{"text": "✖ закрыть", "callback": self._close_cb}]],
            )
        else:
            await call.edit(
                f"<tg-emoji emoji-id='5220197908342648622'>❗️</tg-emoji> "
                f"<b>Ошибка:</b>\n<code>{info}</code>",
                reply_markup=[[{"text": "✖ закрыть", "callback": self._close_cb}]],
            )

    async def _close_cb(self, call):
        await call.delete()