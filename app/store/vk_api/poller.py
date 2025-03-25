from asyncio import Task

from app.store import Store
from app.store.vk_api.dataclasses import Update, UpdateMessage, UpdateObject


class Poller:
    def __init__(self, store: Store) -> None:
        self.store = store
        self.is_running = False
        self.poll_task: Task | None = None

    async def start(self) -> None:
        # TODO: добавить asyncio Task на запуск poll
        self.is_running=True
        self.poll_task=Task(self.poll())

    async def stop(self) -> None:
        # TODO: gracefully завершить Poller
        self.is_running=False
        await self.poll_task

    async def poll(self) -> None:
        while self.is_running:
            data=await self.store.vk_api.poll()
            updates=data["updates"]
            upd=[]
            for update in updates:
                mes=update["object"]["message"]
                upd.append(Update(type=update["type"],object=UpdateObject(message=UpdateMessage(id=mes["id"],from_id=mes["from_id"],text=mes["text"]))))
            await self.store.bots_manager.handle_updates(upd)


        
