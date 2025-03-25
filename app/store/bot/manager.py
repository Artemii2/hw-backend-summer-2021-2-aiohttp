import typing

from app.store.vk_api.dataclasses import Message, Update

if typing.TYPE_CHECKING:
    from app.web.app import Application


class BotManager:
    def __init__(self, app: "Application"):
        self.app = app

    async def handle_updates(self, updates: list[Update]):
        for upd in updates:
            await self.app.store.vk_api.send_message(message=Message(user_id=upd.object.message.from_id,text=upd.object.message.text))
