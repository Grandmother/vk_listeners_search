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

app_id = 3517309
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

def get_needed_songs(songs, queries):
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
            for gtd_song in goted_songs:
                song_id = gtd_song["id"]
                owner_id = gtd_song["owner_id"]
                if songs.get((owner_id, song_id)) is None:
                    songs[(owner_id, song_id)] = defaultdict()
                    songs[(owner_id, song_id)]["id"] = gtd_song["id"]
                    songs[(owner_id, song_id)]["owner_id"] = gtd_song["owner_id"]
                    songs[(owner_id, song_id)]["artist"] = gtd_song["artist"]
                    songs[(owner_id, song_id)]["title"] = gtd_song["title"]
            dumpData(songs, neededSongs)
            sleep(1)
        print("Needed songs count: ", len(songs.keys()))

def add_needed_songs(songs, goted_songs):
    for goted_song in goted_songs:
        song_id = goted_song["id"]
        owner_id = goted_song["owner_id"]

        # If song already in our base
        if songs.get((owner_id, song_id)) is None:
            for query in queries:
                if fuzz.token_set_ratio(goted_song["artist"], query) > 70:
                    songs[(owner_id, song_id)] = defaultdict()
                    songs[(owner_id, song_id)]["id"] = goted_song["id"]
                    songs[(owner_id, song_id)]["owner_id"] = goted_song["owner_id"]
                    songs[(owner_id, song_id)]["artist"] = goted_song["artist"]
                    songs[(owner_id, song_id)]["title"] = goted_song["title"]
    print("Needed songs count: ", len(songs.keys()))

def analyze_collection(user_id, songs, goted_songs):
    for gtd_song in goted_songs:
        if songs.get((gtd_song["owner_id"], gtd_song["id"])) is not None:
            if users_songs.get(user_id) is None:
                users_songs[user_id] = set()
            users_songs[user_id].add((gtd_song["owner_id"], gtd_song["id"]))

def analyze_users(users, users_songs, songs):
    # sort cities by users count
    sorted_users = sorted(users.items(), key = lambda x: x[1]["count"], reverse = True)

    for city in sorted_users:
        city_users = city[1]["users"]
        for user in city_users:
            if user in analized_users:
                continue
            try:
                response = pool.get_next_api().audio.get(owner_id = user
                                                         , count = 6000
                                                         , v = "5.44")
            except vk.exceptions.VkAPIError as ex:
                if ex.code == 201:
                    analized_users.add(user)
                    continue
                else:
                    print(ex)
                    continue
            if response["count"] == 0:
                continue
            goted_songs = response["items"]
            add_needed_songs(songs, goted_songs)
            dumpData(songs, neededSongs)
            analyze_collection(user, songs, goted_songs)
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

    # song_id
    # owner_id
    # artist
    # title
    songs = dict()

    # user_id
    # owner_id
    # song_id
    users_songs = defaultdict(set)

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

    if os.stat(analizedUsers).st_size == 0:
        analized_users = set()
        dumpData(analized_users, analizedUsers)
    analized_users = loadData(analizedUsers)



    # get_needed_songs(songs, queries)

    analyze_users(users, users_songs, songs)
