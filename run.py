import pandas as pd
import os
from weather_secrets import secrets
from weatherRadarClassV2 import weather
import time

from PIL import Image


station = secrets['station']
header = secrets['header']
layer = secrets['layer']
lat = secrets['lat']
lon = secrets['lon']

layer = 'sr_bref'
#'bdsa'

gifParameters = [f"EPSG%3A4326", 'image%2Fpng', True, 0xFFFFFF, "application/vnd.ogc.se_inimage"]
runRadar = weather(secrets, layer)
stationName, stationMode = runRadar.getStationData()
baseMap, baseMapLabels, map, mapParameters = runRadar.getMap()

directory = os.getcwd() + '/Images/' + stationName + '/' + layer

if os.path.isdir(directory):
    True
    #print(f"The directory: {directory} exists!")
else:
    os.makedirs(directory)
    #print(f"Directory {directory} created.")



while True:
    mostRecentRadarTime, mostRecentRadarDateTime = runRadar.getMostRecentRadarTime()
    mostRecentRadarScanName = str(mostRecentRadarDateTime).replace(' ', '_').replace(':', '~') + ".png"

    filePath = directory + '/' + mostRecentRadarScanName
    filePath2 = directory + '/' + 'noMAP_' + mostRecentRadarScanName

    if os.path.isfile(filePath):
        print(f"The file {mostRecentRadarScanName} exists.")
    else:
        print(f"The file {mostRecentRadarScanName} does not exist.")
        try:
            mostRecentRadarScan = runRadar.getMostRecentRadarScan(mostRecentRadarTime, mapParameters, gifParameters)

            mostRecentRadarScanTransparent = runRadar.makeTransparent(mostRecentRadarScan, 155)
            #mostRecentRadarScanTransparent.save(filePath2)
            #combined = Image.alpha_composite(baseMap, mostRecentRadarScanTransparent)
            #combined.save(filePath)
            mostRecentRadarScan.save(filePath)
            print('CREATED!')
        except:
            print('COULD NOT CREATE!')

    time.sleep(120)

#prevImages, prevTimes, times = runRadar.prepRadarGIF(stationMode)
#runRadar.makeGIF(prevImages, prevTimes, times, baseMap, mapParameters, gifParameters)