#!/usr/bin/python3.5

from accounts_pool import Pool
from account import Account

import vk
import os
import pickle
from time import sleep
from random import randint
from collections import defaultdict
from fuzzywuzzy import fuzz


usersFile = "usersBase"
citiesFile = "citiesBase"
neededCities = "neededCities"
accountsFile = "accounts.json"
neededSongs = "neededSongs"
analizedUsers = "analizedUsers"
usersSongs = "usersSongs"

# app_id = 3517309
app_id = 5283939
scope = 278527

queries = [
    "Машина Времени",
    "Константин Никольский",
    "Осколки Сикорского",
    "Группа Стаса Намина",
    "Воскресение",
    "Зеркало мира"
]

global pool

def get_needed_songs(queries):
    global songs

    for query in queries:
        for i in range(0, 3):
            response = pool.get_next_api().audio.search(q = query
                                             , auto_complete = 1
                                             , performer_only = 1
                                             , offset = i * 250
                                             , count = 250
                                             , v = "5.44")
            count = response["count"]
            goted_songs = response["items"]
            for goted_song in goted_songs:
                if fuzz.token_set_ratio(goted_song["artist"], query) > 90:
                    song_id = goted_song["id"]
                    if songs.get(song_id) is None:
                        songs[song_id] = defaultdict()
                        songs[song_id]["id"] = goted_song["id"]
                        songs[song_id]["owner_id"] = goted_song["owner_id"]
                        songs[song_id]["artist"] = goted_song["artist"]
                        songs[song_id]["title"] = goted_song["title"]
            dumpData(songs, neededSongs)
            sleep(1)
        print("Needed songs count: ", len(songs.keys()))

def add_song_user(user_id, song_id):
    global users_songs

    if users_songs.get(user_id) is None:
        users_songs[user_id] = set()
    users_songs[user_id].add(song_id)
    print("User ", user_id, "added")
    dumpData(users_songs, usersSongs)

def add_needed_songs(user_id, goted_songs):
    global songs

    for goted_song in goted_songs:
        song_id = goted_song["id"]

        # If song not in our base
        if songs.get(song_id) is None:
            for query in queries:
                if fuzz.token_set_ratio(goted_song["artist"], query) > 90:
                    songs[song_id] = defaultdict()
                    songs[song_id]["id"] = goted_song["id"]
                    songs[song_id]["owner_id"] = goted_song["owner_id"]
                    songs[song_id]["artist"] = goted_song["artist"]
                    songs[song_id]["title"] = goted_song["title"]
                    add_song_user(user_id, song_id)
        else:
            add_song_user(user_id, song_id)

    print("Needed songs count: ", len(songs.keys()))

def analyze_users():
    global users
    global songs

    # sort cities by users count
    sorted_users = sorted(users.items(), key = lambda x: x[1]["count"], reverse = True)

    for city in sorted_users:
        city_users = city[1]["users"]
        # for user in city_users:
        for user in users_songs.keys():
            # if user in analized_users:
            #     continue
            try:
                response = pool.get_next_api().audio.get(owner_id = user
                                                         , count = 6000
                                                         , v = "5.44")
                print(response)
            except vk.exceptions.VkAPIError as ex:
                if ex.code == 201:
                    analized_users.add(user)
                    continue
                else:
                    print(ex)
                    continue
            if response["count"] == 0:
                print("response count is zero: ", response)
                continue
            goted_songs = response["items"]

            add_needed_songs(user, goted_songs)
            dumpData(songs, neededSongs)

            analized_users.add(user)
            dumpData(analized_users, analizedUsers)

def dumpData(users, file):
    with open(file, 'wb') as f:
        pickle.dump(users, f, pickle.HIGHEST_PROTOCOL)

def loadData(file):
    with open(file, 'rb') as f:
        return pickle.load(f)

if __name__ == "__main__":
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
    #todo: Сделать проверку давности получения access_token. Чтобы не проверять каждый раз при подключении.
    for i in range(0, len(accounts)):
        if accounts[i]["access_token"] == "":
            pool.add_account(Account(accounts[i]["login"], accounts[i]["passwd"], app_id, scope))
        else:
            print("access_token(", accounts[i]["login"], "): ", accounts[i]["access_token"])
            pool.add_account(Account(accounts[i]["login"], accounts[i]["passwd"], app_id, scope, accounts[i]["access_token"]))

        # Сохраним access_token после логина (вдруг обновился)
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

    if os.stat(neededSongs).st_size == 0:
        songs = defaultdict()
        dumpData(songs, neededSongs)
    songs = loadData(neededSongs)

    if os.stat(usersSongs).st_size == 0:
        users_songs = defaultdict(set)
        dumpData(users_songs, usersSongs)
    users_songs = loadData(usersSongs)

    if os.stat(analizedUsers).st_size == 0:
        analized_users = set()
        dumpData(analized_users, analizedUsers)
    analized_users = loadData(analizedUsers)

    # get_needed_songs(queries)

    analyze_users()
