import vk
from vk_auth import Auth
from time import sleep
from collections import defaultdict
from random import randint
import pickle
import os

# period = 25
# time_to_rate = 20
period = 2
time_to_rate = 20


vk_user_id = 225002811
# vk_user_phone = "+79518248241"
# vk_user_pass = "RybakovVk_32"
vk_user_phone = "+79167174642"
vk_user_pass = "RybakovVk_32"

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
                and item.get("city").get("id") != city_id:
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
        print(count, len(users[city_id]))
        print( "percent: " , abs(count - len(users[city_id])) * 100 / count, end=' ')
        if count > 1000:
            if len(users[city_id]) != 0:
                users_before = set(users[city_id])
            else:
                users_before = set()
                for item in response["items"]:
                    users_before.add(item["id"])
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
                if (abs(count - len(users[city_id])) * 100 / count < 5) or (len(users[city_id]) > count):
                    print("less then 3% ")
                    break
                sleep(randint(9,15))
        else:
            add_users(users, city_id, response["items"])
            print(count)
    else:
        print ("City is exists")

def get_city_users_count(city_id: int):
    response = vkapi.users.search(city = city_id
                                  , count = 1
                                  , v="5.44"
                                  )
    return response["count"]

def get_cities_count_in_region(region_id: int):
    response = vkapi.database.getCities(country_id = 1
                             , region_id = region_id
                             , need_all = 1
                             , offset = 0
                             , count = 1
                             , v="5.44")
    return response["count"]


def get_cities(cities, region_id: int):
    count = 1000
    offset = 0
    while count == 1000:
        response = vkapi.database.getCities(country_id = 1
                                 , region_id = region_id
                                 , need_all = 1
                                 , offset = offset
                                 , count = 1000
                                 , v="5.44")
        for city in response["items"]:
            city_id = city["id"]
            if cities.get(city_id) == None:
                cities[city_id] = defaultdict()
                cities[city_id]["title"] = city["title"]
                cities[city_id]["uc"] = get_city_users_count(city_id)
                cities[city_id]["id"] = city_id
                dumpData(cities, citiesFile)
                print(len(cities))
                sleep(0.5)
        count = len(response["items"])
        offset += 1000
        print(count)
    return cities


region_id = 1077676

if __name__ == "__main__":
    init_vk_api()

    if (os.stat(citiesFile).st_size == 0):
        cities = defaultdict()
        dumpData(cities, citiesFile)
    cities = loadData(citiesFile)

    if ( len(cities) != get_cities_count_in_region(region_id) ):
        get_cities(cities, region_id)


    if (os.stat(usersFile).st_size == 0):
        users = defaultdict()
        dumpData(users, usersFile)
    users = loadData(usersFile)

    for city in cities:
        print(city["title"], ": ", end="")
        city_id = city["id"]
        if users.get(city_id) == None:
            users[city_id]["usesrs"] = set()
            users[city_id]["count"] = 0
            dumpData(users,usersFile)
        find_users(users, city["id"], city["title"])
        dumpData(users,usersFile)
        print()