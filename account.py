import vk
from vk_auth import Auth

class Account:
    def __init__(self, user_login: str = "",
                 user_passwd: str = "",
                 app_id: int = 3517309,
                 scope: int = 278527,
                 access_token: str = ""):
        self._login = user_login
        self._passwd = user_passwd
        self._app_id = app_id
        self._scope = scope

        if access_token != "":
            self._acess_token = access_token

        self.get_access()

    @property.getter
    def vkapi(self):
        if self.check_access():
            return self.vkapi()

    def check_access(self) -> bool:
        #Проверим, сработал ли acess_token
        try:
            self._vkapi.users.get(user_id=1)
        except:
            return False
        # access is seems to be.
        return True

    def get_access(self):
        self._session = vk.Session(access_token=self._access_token)
        self._vkapi = vk.API(self._session)

        if self.check_access():
            return

        self._vk_auth = Auth(self._login, self._passwd, self._app_id, str(self._scope))
        self._access_token, uid = self._vk_auth()

        session = vk.Session(access_token=self._access_token)
        self._vkapi = vk.API(session, lang='ru')