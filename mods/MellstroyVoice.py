# Name: MellstroyVoice
# Description: голосовые Мелстроя
# authors: @neistv 
# version: 1.2.2
# meta developer: @latexmods
# requires: pydub audioop-lts
# meta banner: https://github.com/neistv/mods/raw/main/assets/MellstroyVoice.png

import io

import requests
from pydub import AudioSegment

from .. import loader, utils

BASE_URL = "https://raw.githubusercontent.com/neistv/mods/main/assets%20mellstroy/"
REQUEST_TIMEOUT = 15


async def _send_voice(module, message, filename: str):
    reply = await message.get_reply_message()

    if message.out:
        await message.delete()

    response = await utils.run_sync(
        requests.get,
        BASE_URL + filename,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    voice_bytes = response.content

    byte = io.BytesIO()
    AudioSegment.from_file(io.BytesIO(voice_bytes)).export(byte, format="ogg")
    byte.name = "voice.ogg"
    byte.seek(0)

    await message.client.send_file(
        message.to_id,
        byte,
        voice_note=True,
        reply_to=reply.id if reply else None,
    )


@loader.tds
class MellstroyVoiceMod(loader.Module):
    """голосовые Мелстроя!!!"""

    strings = {"name": "MellstroyVoice"}

    async def амамамcmd(self, message):
        """​"""
        await _send_voice(self, message, "amamam.mp3")

    async def блятьcmd(self, message):
        """​"""
        await _send_voice(self, message, "bluat.mp3")

    async def бравоcmd(self, message):
        """​"""
        await _send_voice(self, message, "bravoo.mp3")

    async def щавельcmd(self, message):
        """​"""
        await _send_voice(self, message, "chavel.mp3")

    async def чтотыдумалcmd(self, message):
        """​"""
        await _send_voice(self, message, "chotidumal.mp3")

    async def эхтыcmd(self, message):
        """​"""
        await _send_voice(self, message, "extisuka.mp3")

    async def идинахуйcmd(self, message):
        """​"""
        await _send_voice(self, message, "idinaxyu.mp3")

    async def раздваcmd(self, message):
        """​"""
        await _send_voice(self, message, "razdva.mp3")

    async def скольконахуйcmd(self, message):
        """​"""
        await _send_voice(self, message, "skolkanaxuy.mp3")

    async def стопстопстопcmd(self, message):
        """​"""
        await _send_voice(self, message, "stopstopstop.mp3")

    async def свистcmd(self, message):
        """​"""
        await _send_voice(self, message, "svist.mp3")

    async def виноградcmd(self, message):
        """​"""
        await _send_voice(self, message, "vinpgrad.mp3")

    async def хахахаcmd(self, message):
        """​"""
        await _send_voice(self, message, "xaxaxa.mp3")

    async def ухуcmd(self, message):
        """​"""
        await _send_voice(self, message, "yxyyy.mp3")
