#!/usr/bin/python3.5

import pickle
import os
import pprint

usersFile = "usersBase"
citiesFile = "citiesBase"
neededCities = "neededCities"



def loadData(file):
    with open(file, 'rb') as f:
        return pickle.load(f)

if os.stat(usersFile).st_size != 0:
    users = loadData(usersFile)

if os.stat(citiesFile).st_size != 0:
    cities = loadData(citiesFile)

if os.stat(neededCities).st_size != 0:
    needed_cities = loadData(neededCities)

print("Cities:")
for city in sorted(cities.values(), key = lambda x : x["uc"], reverse=True):
    city_id = city["id"]
    if city["uc"] != -1 and users.get(city_id) is not None:
        print(city_id, ":\t", city["title"], " = ", len(users[city_id]["users"]), "/", city["uc"])