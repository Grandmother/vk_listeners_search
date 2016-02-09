import vk
from vk_auth import Auth
from time import sleep

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

        self._access_token = access_token

        self.get_access()

    @property
    def vkapi(self):
        if not self.check_access():
            self.get_access()

        return self._vkapi

    @property
    def login(self):
        return self._login

    @property
    def access_token(self):
        return self._access_token

    def check_access(self) -> bool:
        #Проверим, сработал ли acess_token
        sleep(1)
        try:
            self._vkapi.users.get(user_id=1)
        except:
            print("check access fault")
            sleep(1)
            return False
        # access is seems to be.
        print("check access succeeeeed")
        return True

    def get_access(self):
        if self._access_token != "":
            self._session = vk.Session(access_token=self._access_token)
            self._vkapi = vk.API(self._session)

            if self.check_access():
                print("get access with access_token")
                return
        self._vk_auth = Auth(self._login, self._passwd, self._app_id, str(self._scope))
        self._access_token, uid = self._vk_auth()

        session = vk.Session(access_token=self._access_token)
        self._vkapi = vk.API(session, lang='ru')

        print("get access without access_token")
        if self.check_access():
            print("got it for ", self._login)
            return
        else:
            print("can't get access as ", self._login)