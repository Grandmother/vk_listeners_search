#!/usr/bin/python3.5

import vk
from vk_auth import Auth
from time import sleep
from collections import defaultdict
from random import randint
import pickle
import pprint
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
neededCities = "neededCities"

def init_vk_api():
    global vkapi

    vk_access_token = "7039f99746757ea44124f9d7e62c3f439d1a5b119beaade3daa720b1529704ed44c4d940c88105baa4f8c"

    try:
        session = vk.Session(access_token=vk_access_token)
        vkapi = vk.API(session)
        vkapi.users.get(user_id=1)
    except:
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

def get_city_users_count(city_id: int):
    response = vkapi.users.search(city = city_id
                                  , count = 1
                                  , v="5.44"
                                  )
    return response["count"]

def add_users(users, dict, needed_cities):
    # added_from_cities = defaultdict(int)

    for item in dict:
        # Если у пользователя указан город проживания
        if item.get("deactiveted"):
            print("user ", item.get("id"), "is ", item.get("deactivated"))
            continue
        if item.get("city") is not None:
            city_id = item["city"]["id"]
        else:
            continue

        # Если город есть в базе, но количество жителей в нём неизвестно
        if  cities.get(city_id) is not None\
                and cities[city_id]["uc"] == -1:
            cities[city_id]["uc"] = get_city_users_count(city_id)
            if cities[city_id]["uc"] > 5000:
                needed_cities.add(city_id)
            dumpData(cities, citiesFile)
            dumpData(needed_cities, neededCities)

        # Если город не входит в число нужных
        if city_id not in needed_cities:
            continue

        # Если города ещё нет в базе пользователей
        if users.get(city_id) == None:
            users[city_id] = defaultdict()
            users[city_id]["users"] = set()
            users[city_id]["count"] = 0

        # added_from_cities[city_id] += 1
        # Добавим пользователя
        users[city_id]["users"].add(item["id"])
        users[city_id]["count"] = len(users[city_id]["users"])

    # print("Added:")
    # for city_id in added_from_cities.keys():
    #     print(cities[city_id]["title"], ": ", added_from_cities[city_id])

def char_range(c1, c2):
    """Generates the characters from `c1` to `c2`, inclusive."""
    for c in range(ord(c1), ord(c2)+1):
        yield chr(c)

def find_users(users: defaultdict, city_id, cities, needed_cities):
    response = vkapi.users.search(city = city_id
                                  , count = 1000
                                  , v="5.44"
    )
    count = response["count"]
    if count == 0:
        print ("no users")
        return

    # Если города ещё нет в базе пользователей
    if users.get(city_id) == None:
        users[city_id] = defaultdict()
        users[city_id]["users"] = set()
        users[city_id]["count"] = 0

    # Если скачано меньше 95% людей из этого города.
    if abs(count - len(users[city_id]["users"])) * 100 / count > 5:
        print( "percent: " , abs(count - len(users[city_id]["users"])) * 100 / count)

        # Если в базе есть люди из этого города
        if len(users[city_id]["users"]) != 0:
            users_before = set(users[city_id]["users"])
        else:
            users_before = set()

        # Добавляем людей, полученных в результате запроса в базу и в users_before
        for item in response["items"]:
            users_before.add(item["id"])
            users[city_id]["users"].add(item["id"])

        for user_id in users_before:
            try:
                response = vkapi.friends.get( user_id = user_id
                                              , order = "random"
                                              , fields = "city"
                                              , v="5.44")
            except vk.exceptions.VkAPIError as err:
                print(err)
                users[city_id]["users"].discard(user_id)
                continue

            add_users(users, response["items"], needed_cities)
            print("users in ", cities[city_id]["title"], " now: ", len(users[city_id]["users"]))
            # print(response["items"])
            dumpData(users,usersFile)
            if (abs(count - len(users[city_id]["users"])) * 100 / count < 5) or (len(users[city_id]["users"]) > count):
                print("less then 3% ")
                break
            sleep(randint(5,10))
    else:
        print ("City is exists")

def get_cities_count_in_region(region_id: int):
    response = vkapi.database.getCities(country_id = 1
                             , region_id = region_id
                             , need_all = 1
                             , offset = 0
                             , count = 1
                             , v="5.44")
    return response["count"]

def get_region_cities(cities, needed_cities):
    count = 1000
    offset = 0
    while count == 1000:
        response = vkapi.database.getCities(country_id = 1
                                 , region_id = region_id
                                 # , need_all = 1
                                 , offset = offset
                                 , count = 1000
                                 , v="5.44")
        for city in response["items"]:
            city_id = city["id"]
            if cities.get(city_id) is not None:
                if cities[city_id]["uc"] > 5000:
                    needed_cities.add(city_id)
                continue
            cities[city_id] = defaultdict()
            cities[city_id]["title"] = city["title"]
            cities[city_id]["uc"] = -1
            cities[city_id]["id"] = city_id
        dumpData(cities, citiesFile)
        dumpData(needed_cities, neededCities)

        count = len(response["items"])
        offset += 1000
        print(count)

def get_cities(cities: defaultdict, region_id: int, users, needed_cities):
    for city_tup in sorted(cities.items(), key=lambda y : y[1]["uc"], reverse=True):
        city = city_tup[1]
        city_id = city["id"]
        if city["uc"] == -1:
            cities[city_id]["uc"] = get_city_users_count(city_id)
            city["uc"] = cities[city_id]["uc"]
            dumpData(cities, citiesFile)

        if city["uc"] > 5000:
            print(city["id"], ": ", city["title"], " - ", city["uc"])
            needed_cities.add(city_id)
            if users.get(city_id) == None:
                users[city_id] = defaultdict()
                users[city_id]["users"] = set()
                users[city_id]["count"] = 0
                dumpData(users,usersFile)
            find_users(users, city["id"], cities, needed_cities)
            dumpData(users,usersFile)
            sleep(randint(5,13))
    return cities

region_id = 1077676

if __name__ == "__main__":
    init_vk_api()

    if os.stat(usersFile).st_size == 0:
        users = defaultdict()
        dumpData(users, usersFile)
    users = loadData(usersFile)

    if os.stat(citiesFile).st_size == 0:
        cities = defaultdict()
        dumpData(cities, citiesFile)
    cities = loadData(citiesFile)

    if os.stat(neededCities).st_size == 0:
        needed_cities = set()
        dumpData(needed_cities, neededCities)
    needed_cities = loadData(neededCities)

    get_region_cities(cities, needed_cities)

    print("needed cities:")
    for city in needed_cities:
        print (cities[city]["id"], ": ", cities[city]["title"], cities[city]["uc"])

    get_cities(cities, region_id, users, needed_cities)

    print("needed cities:")
    for city in cities.items():
        if city["uc"] > 5000:
            needed_cities.add(city["id"])
            print (city["title"], city["uc"])
    dumpData(needed_cities, neededCities)