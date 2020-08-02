from riotWrapper import Lolwrapper
import json
import time
import datetime
from datetime import timedelta
import glob
import os
import clipper as c
import subprocess

wrapper = Lolwrapper("RGAPI-71f96a59-cc9b-4da5-9e55-dbe259c88ed4")

summoner = wrapper.requestSummonerData("Pentapups")
matchlist = wrapper.requestMatchList(summoner["accountId"])


path = "C:/Users/Pups/Videos/ClashRecord/"

filesname = glob.glob(path+"*.mp4")

dico = {}
dico["creation"]=[]
dico["duration"]=[]

for file in filesname:
	fileCreation = file.split()[2]
	file2 = file.split("\\")[1]
	fileNoExtension = fileCreation.split(".")[0]

#string = "31_07_2020_23_59_59" format used with my Obs settings
	timestamp = time.mktime(datetime.datetime.strptime(fileNoExtension, 
	                                             "%d_%m_%Y_%H_%M_%S").timetuple())


	for match in matchlist["matches"]:

		matchData = wrapper.requestMatch(str(match['gameId']))
		if(matchData["gameCreation"]>timestamp*1000):

			duration = matchData["gameDuration"]
			formattedDuration = timedelta(seconds = duration)
			creationTime = (matchData["gameCreation"]/1000)-timestamp
			dico["creation"].append(str(timedelta(seconds=int(creationTime))))
			dico["duration"].append(str(formattedDuration))
			
		else:
			break
#We fetch the request from newest to oldest but we want them in the reverse order for editting the video
dico["duration"].reverse()
dico["creation"].reverse()
with open('C:/Users/Pups/Documents/python/PythonProject/gamesDuration.json', 'w') as outfile:
    json.dump(dico, outfile)

print("Processing file : "+file2)

with open('gamesDuration.json', 'r') as json_file:
		data = json.load(json_file)
c.clipper(data,path+file2)

