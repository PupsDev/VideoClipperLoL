from riotWrapper import Lolwrapper
import json
import time
import datetime
from datetime import timedelta


wrapper = Lolwrapper("API-KEY")

summoner = wrapper.requestSummonerData("Pentapups")
matchlist = wrapper.requestMatchList(summoner["accountId"])


string = "31_07_2020_23_59_59"
timestamp = time.mktime(datetime.datetime.strptime(string, 
                                             "%d_%m_%Y_%H_%M_%S").timetuple())

for match in matchlist["matches"]:
	#['gameDuration']
	matchData = wrapper.requestMatch(str(match['gameId']))
	if(matchData["gameCreation"]>timestamp*1000):
	#print(str(time.strftime('%d-%m %H:%M', time.localtime(matchData["gameCreation"]/1000))))
		duration = matchData["gameDuration"]
		formattedDuration = timedelta(seconds = duration)
		print(str(formattedDuration))
	else:
		break






  

