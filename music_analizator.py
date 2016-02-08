#!/usr/bin/python3.5

from accounts_pool import Pool
from account import Account

import os
import pickle
from time import sleep
from collections import defaultdict


usersFile = "usersBase"
citiesFile = "citiesBase"
neededCities = "neededCities"
accountsFile = "accounts.json"

app_id = 3517309
scope = 278527

global pool

def analyze_collection():
    pass

def analyze_users(users, users_songs, songs, songs_vkSongs):
    for city in cities:
        user
    pass

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
    for i in range(0, len(accounts)):
        if accounts[i]["access_token"] == "":
            pool.add_account(Account(accounts[i]["login"], accounts[i]["passwd"], app_id, scope))
            accounts[i]["access_token"] = pool.get_account(accounts[i]["login"]).access_token
            dumpData(accounts, accountsFile)
        else:
            print("access_token(", accounts[i]["login"], "): ", accounts[i]["access_token"])
            pool.add_account(Account(accounts[i]["login"], accounts[i]["passwd"], app_id, scope, accounts[i]["access_token"]))
        sleep(6)

    pool.show_all_accounts()

    # SONG_id
    # artist
    # title
    songs = dict()

    # SONG_id
    # user_id
    users_songs = dict()

    # SONG_id
    # song_vkid
    # song_vkowner
    songs_vkSongs = dict()

    if os.stat(usersFile).st_size == 0:
        users = defaultdict()
        dumpData(users, usersFile)
    users = loadData(usersFile)

    if os.stat(citiesFile).st_size == 0:
        cities = defaultdict()
        dumpData(cities, citiesFile)
    cities = loadData(citiesFile)

    analyze_users(users, users_songs, songs, songs_vkSongs)
