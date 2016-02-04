import vk
from vk_auth import Auth
from time import sleep
from collections import defaultdict

# period = 25
# time_to_rate = 20
period = 2
time_to_rate = 20


vk_user_id = 225002811
vk_user_phone = "+79518248241"
vk_user_pass = "RybakovVk_32"
# vk_user_phone = "+79167174642"
# vk_user_pass = "RybakovVk_32"

app_id = 3517309
scope = 278527

usersFile = "usersBase"
citiesFile = "citiesBase"

def init_vk_api():
    global vkapi

    vk_auth = Auth(vk_user_phone, vk_user_pass, app_id, str(scope))
    vk_access_token, uid = vk_auth()

    session = vk.Session(access_token=vk_access_token)
    vkapi = vk.API(session)

import pickle

def dumpData(users, file):
    with open(file, 'wb') as f:
        pickle.dump(users, f, pickle.HIGHEST_PROTOCOL)

def loadData(file):
    with open(file, 'rb') as f:
        return pickle.load(f)

def add_users(users, city_id, dict):
    for item in dict:
        users[city_id].add(item["id"])


def find_users(city_id, users: defaultdict):
    response = vkapi.users.search(city = city_id
                                   , v="5.44"
    )
    # print(response)
    count = response["count"]
    if count > 1000:
        # while len(users[city_id]) != count:
        add_users(users, city_id, response["items"])
    else:
        add_users(users, city_id, response["items"])
        print(count)

if __name__ == "__main__":
    init_vk_api()

    count = 1000
    offset = 0
    cities = list()
    while count == 1000:
        response = vkapi.database.getCities(country_id = 1
                                 , region_id = 1077676
                                 , need_all = 1
                                 , offset = offset
                                 , count = 1000
                                 , v="5.44")
        cities += response["items"]
        count = len(response["items"])
        offset += 1000
        sleep(0.2)
        print(count)

    users = loadData(usersFile)
    for city in users.keys():
        print(city, ": ", users[city])
    dumpData(cities, citiesFile)
    #
    # for city in cities:
    #     print(city["title"], "(", city["id"], "): ", end="")
    #     city_id = city["id"]
    #     users[city_id] = set()
    #     find_users(city["id"], users)
    #     dumpData(users,file)
    #     sleep(6)