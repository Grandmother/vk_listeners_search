from account import Account
import random

class Pool:
    def __init__(self):
        self._accounts = []
        self._last_used = None
        pass

    # Добавить аккаунт в пул
    # def add_account(self, user_login: str,
    #              user_passwd: str,
    #              app_id: int,
    #              scope: int):
    #     self._accounts.append(Account(user_login, user_passwd, app_id, scope))
    #     self._last_used = len(self._accounts) - 1

    def add_account(self, account: Account):
        self._accounts.append(account)
        self._last_used = len(self._accounts) - 1

    def show_all_accounts(self):
        for account in self._accounts:
            print(account.login)

    def get_account(self, login: str):
        for account in self._accounts:
            if account._login == login:
                return account
        return None

    # удалить аккаунт из пула
    def del_account(self, login):
        self._accounts.pop(login)
        self._last_used = len(self._accounts) - 1

    # Получение api для работы с функциями. В идеале пользователь будет получать один api для выполнения одного метода.
    def get_random_api(self):
        return random.choice(self._accounts)

    def get_next_api(self):
        index = (self._last_used + 1) % len(self._accounts)
        self._last_used = index
        print("got vkapi from ", self._accounts[index].login)
        return self._accounts[index].vkapi


    # Проверка работоспособности всех аккаунтов и переподключение, если что-то не так
    def check_api(self):
        for account in self._accounts:
            if not account.check_access():
                account.get_access()