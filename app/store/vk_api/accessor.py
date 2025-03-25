import typing
from urllib.parse import urlencode, urljoin

from aiohttp.client import ClientSession

from app.base.base_accessor import BaseAccessor
from app.store.vk_api.dataclasses import Message
from app.store.vk_api.poller import Poller

if typing.TYPE_CHECKING:
    from app.web.app import Application

API_VERSION = "5.131"


class VkApiAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.session: ClientSession | None = None
        self.key: str | None = None
        self.server: str | None = None
        self.poller: Poller | None = None
        self.ts: int | None = None

    async def connect(self, app: "Application"):
        # TODO: добавить создание aiohttp ClientSession,
        #  получить данные о long poll сервере с помощью метода groups.getLongPollServer
        #  вызвать метод start у Poller
        self.session=ClientSession()
        await self._get_long_poll_service()
        self.poller=Poller(app.store)
        await self.poller.start()    

    async def disconnect(self, app: "Application"):
        # TODO: закрыть сессию и завершить поллер
        await self.session.close()
        await self.poller.stop()

    @staticmethod
    def _build_query(host: str, method: str, params: dict) -> str:
        params.setdefault("v", API_VERSION)
        return f"{urljoin(host, method)}?{urlencode(params)}"

    async def _get_long_poll_service(self):
        async with self.session.get(VkApiAccessor._build_query("https://api.vk.com","method/groups.getLongPollServer",{"group_id":"229832073","access_token":"vk1.a.V6AdfKv34XZ1Kn5u5kxQS2lXO310gJsAfsm5sD9bKc-fY8oJHhGmQMnVauXSDg6zMnStDlYq94TVELYLKLR_8T8Gr7mq1KMleIu-xEFwadc1inoDXX5v-69FYQMR3FSLMpL1OO2GbMa1myJ_2SS0rFrUIWziXwM6Pm7Wkg-83WEoKexNIi5NpPCSjc6ez-6X_PNMJ_6QasvO17n3CZxCYw"})) as resp: 
            data=await resp.json()
            data=data["response"]
            self.key=data["key"]
            self.server=data["server"]
            self.ts=data["ts"]

    async def poll(self):
        q=self._build_query(self.server,"",{"act":"a_check","key":self.key,"ts":self.ts,"wait":25})
        async with self.session.get(q) as resp:
            data=await resp.json()
            self.ts=data["ts"]
            return data

    async def send_message(self, message: Message) -> None:
        print(message)
