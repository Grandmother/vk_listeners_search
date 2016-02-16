#!/usr/bin/python3.4

import pickle
import os
import pprint

usersFile = "usersBase"
citiesFile = "citiesBase"
neededCities = "neededCities"
neededSongs = "neededSongs"
analizedUsers = "analizedUsers"
usersSongs = "usersSongs"



def loadData(file):
    with open(file, 'rb') as f:
        return pickle.load(f)

if os.stat(usersFile).st_size != 0:
    users = loadData(usersFile)

if os.stat(citiesFile).st_size != 0:
    cities = loadData(citiesFile)

if os.stat(neededCities).st_size != 0:
    needed_cities = loadData(neededCities)

if os.stat(neededSongs).st_size != 0:
    needed_songs = loadData(neededSongs)

if os.stat(analizedUsers).st_size != 0:
    analized_users = loadData(analizedUsers)

if os.stat(usersSongs).st_size != 0:
    users_songs = loadData(usersSongs)

print("Cities:")
for city in sorted(cities.values(), key = lambda x : x["uc"], reverse=True):
    city_id = city["id"]
    if city["uc"] != -1 and users.get(city_id) is not None:
        print(city_id, ":\t", city["title"], " = ", len(users[city_id]["users"]), "/", city["uc"])

# print("Users:")
# for user in users_songs.keys():
    # print(user, ": ", users_songs[user])

print("Analized users: ", len(analized_users), "Needed: ", len(analized_users & users_songs.keys()))

print("Statistics:")
print("Good users: ", len(users_songs.keys()), " of ", len(analized_users))
