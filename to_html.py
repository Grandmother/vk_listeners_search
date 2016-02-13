#!/usr/bin/python3.5
# -*- coding: utf-8 -*-

import pickle
import os
from collections import defaultdict

usersFile = "usersBase"
citiesFile = "citiesBase"
neededCities = "neededCities"
neededSongs = "neededSongs"
analizedUsers = "analizedUsers"
usersSongs = "usersSongs"


def loadData(file):
    with open(file, 'rb') as f:
        return pickle.load(f)


if os.stat(neededSongs).st_size != 0:
    needed_songs = loadData(neededSongs)

if os.stat(analizedUsers).st_size != 0:
    analized_users = loadData(analizedUsers)

if os.stat(usersSongs).st_size != 0:
    users_songs = loadData(usersSongs)

data = dict()
data[0] = list()
data[0].append("User ID")
data[0].append("Songs count")
data[0].append("Songs")

counter = 0

for user in sorted(users_songs.items(), key = lambda x: len(x[1]), reverse = True) :
    counter += 1

    data[counter] = list()
    data[counter].append(str(user[0]))
    data[counter].append(str(len(user[1])))
    data[counter].append(str())
    for song in user[1]:
        # if song in needed_songs:
        data[counter][2] += needed_songs[song]["artist"] + " - " + needed_songs[song]["title"] + "<br>"

# print(data)

html = '<head>\
<meta charset="UTF-8">\
</head>\
Текущее количество пользователей: ' + str(len(data) - 1) + '\
<table border="1" style="width:100%">\
<tr><th>' + '</th><th>'.join(data[0]) + '</th></tr>'
del data[0]

for row in data.values():
    # html += '<tr><td>' + '</td><td>'.join(row) + '</td></tr>'
    html += '<tr><td>' + row[0] + '</td><td>' + row[1] + '</td><td>' + row[2] + '</td></tr>'

html += '</table>'

print (html)