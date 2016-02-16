#!/usr/bin/python3.4

import vk
from time import sleep
from collections import defaultdict
from random import randint
import pickle
import os

from accounts_pool import Pool
from account import Account

global pool

app_id = 
scope = 278527

usersFile = "usersBase"
citiesFile = "citiesBase"
neededCities = "neededCities"
accountsFile = "accounts.json"

def dumpData(users, file):
    with open(file, 'wb') as f:
        pickle.dump(users, f, pickle.HIGHEST_PROTOCOL)

def loadData(file):
    with open(file, 'rb') as f:
        return pickle.load(f)

def get_city_users_count(city_id: int):
    response = pool.get_next_api().users.search(city = city_id
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

def char_range(c1, c2):
    """Generates the characters from `c1` to `c2`, inclusive."""
    for c in range(ord(c1), ord(c2)+1):
        yield chr(c)

def find_users(users: defaultdict, city_id, cities, needed_cities):
    response = pool.get_next_api().users.search(city = city_id
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
                response = pool.get_next_api().friends.get( user_id = user_id
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
            sleep(randint(1,3))
    else:
        print ("City is exists")

def get_cities_count_in_region(region_id: int):
    response = pool.get_next_api().database.getCities(country_id = 1
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
        response = pool.get_next_api().database.getCities(country_id = 1
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
            sleep(randint(1,3))
    return cities

region_id = 1077676

if __name__ == "__main__":
    # init_vk_api()

    global pool
    if os.stat(accountsFile).st_size == 0:
        raise Exception("""Please fill the file {} in format:
                 {
                    [
                    {"login":"user_login", "passwd":"user_password", "access_token":""}
                    ]
                 }""".format(accountsFile))

    accounts = list()
    with open(accountsFile) as f:
        accounts = json.load(f)

    pool = Pool()
    for i in range(0, len(accounts)):
        if accounts[i]["access_token"] == "":
            pool.add_account(Account(accounts[i]["login"], accounts[i]["passwd"], app_id, scope))
        else:
            print("access_token(", accounts[i]["login"], "): ", accounts[i]["access_token"])
            pool.add_account(Account(accounts[i]["login"], accounts[i]["passwd"], app_id, scope, accounts[i]["access_token"]))

        accounts[i]["access_token"] = pool.get_account(accounts[i]["login"]).access_token
        dumpData(accounts, accountsFile)
        sleep(randint(5,7))

    pool.show_all_accounts()

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
    get_cities(cities, region_id, users, needed_cities)
