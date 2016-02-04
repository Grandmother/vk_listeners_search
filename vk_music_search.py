import vk
from vk_auth import Auth
from time import sleep
from collections import defaultdict
from random import randint

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

def add_users(users, dict, city_id, city_title: str = ""):
    for item in dict:
        if city_title != ""\
                and item.get("city") is not None\
                and item.get("city").get("title") != city_title:
            continue
        users[city_id].add(item["id"])
    print("users now: ", len(users[city_id]))

def char_range(c1, c2):
    """Generates the characters from `c1` to `c2`, inclusive."""
    for c in range(ord(c1), ord(c2)+1):
        yield chr(c)

def find_users(users: defaultdict, city_id, city_title):
    response = vkapi.users.search(city = city_id
                                  , count = 1000
                                  , v="5.44"
    )
    sleep(0.4)
    count = response["count"]
    if count == 0:
        print ("no users")
        return
    if abs(count - len(users[city_id])) * 100 / count > 5:
        print(users[city_id])
        print( "percent: " , abs(count - len(users[city_id])) * 100 / count, end=' ')
        if count > 1000:
            users_before = set(users[city_id])
            for user_id in users_before:
                try:
                    response = vkapi.friends.get( user_id = user_id
                                                  , order = "random"
                                                  , fields = "city"
                                                  , v="5.44")
                except vk.exceptions.VkAPIError as err:
                    print(err)
                    users[city_id].discard(user_id)
                    continue

                add_users(users, response["items"], city_id, city_title)
                print(response["items"])
                dumpData(users,usersFile)
                if abs(count - len(users[city_id])) * 100 / count < 5:
                    print("less then 3% ")
                    break
                sleep(randint(9,15))
        # else:
            # add_users(users, city_id, response["items"])
            # print(count)
    else:
        print ("City is exists")

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


    users = defaultdict()
    users = loadData(usersFile)

    for city in cities:
        print(city["title"], ": ", end="")
        city_id = city["id"]
        if users.get(city_id) == None:
            users[city_id] = set()
            dumpData(users,usersFile)
        find_users(users, city["id"], city["title"])
        dumpData(users,usersFile)
        print()