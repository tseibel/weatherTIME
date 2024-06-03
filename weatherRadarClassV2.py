import requests
import xmltodict
import geotiler
import numpy as np
import time

from PIL import Image
from datetime import datetime
from io import BytesIO

class weather():
    def __init__(self, secrets, layer):
        self.station = secrets['station']
        self.header = secrets['header']
        self.layer = layer#secrets['layer']
        self.lat = secrets['lat']
        self.lon = secrets['lon']
        self.frames = None

    def getStationData(self):
        station_url = f"https://api.weather.gov/radar/stations?stationType=WSR-88D,"
        station_json = requests.get(station_url + self.station, headers=self.header, timeout=20).json()

        # Select name and mode of station from station secret
        for record in station_json['features']:
                if record['properties']['id'] == self.station.upper(): #If the ID matches
                    station_name = record['properties']['name']
                    station_mode = record['properties']['rda']['properties']['volumeCoveragePattern'] 

        return station_name, station_mode

    def getMostRecentRadarTime(self):
        capabilities_url = f'https://opengeo.ncep.noaa.gov:443/geoserver/{self.station}/{self.station}_{self.layer}/wms?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetCapabilities'
        response = requests.get(capabilities_url, headers=self.header, timeout=10)

        if response:
            xml_file = BytesIO(response.content)
            capabilties_dict = xmltodict.parse(xml_file.read())
            times = capabilties_dict["WMS_Capabilities"]["Capability"]["Layer"]["Layer"]["Dimension"]["#text"]

            times = times.split(',')
            maxTime = max(times)
        else:
            print('Bad Response: ' + response)

        return maxTime, datetime.strptime(maxTime,'%Y-%m-%dT%H:%M:%S.000Z')

    def getMostRecentRadarScan(self, scanTime, mapParameters, gifParameters):

        SRS, format, transparent, bg_colour, EXCEPTION = gifParameters[0], gifParameters[1], gifParameters[2], gifParameters[3], gifParameters[4]
        minx, miny, maxx, maxy, size = mapParameters[0], mapParameters[1], mapParameters[2], mapParameters[3], mapParameters[4]
        bbox=f'{miny}%2C{minx}%2C{maxy}%2C{maxx}'


        scanTimeURL = str(scanTime).replace(':','%3A')

        radar_url = f"https://opengeo.ncep.noaa.gov:443/geoserver/{self.station}/ows?SERVICE=WMS&service=WMS&version=1.3.0&request=GetMap&layers={self.station}_{self.layer}&styles=&width={size[0]}&height={size[1]}&crs={SRS}&bbox={bbox}&format={format}&transparent={transparent}&bgcolor={bg_colour}&exceptions={EXCEPTION}&time={scanTimeURL}"

        try: #Try to get the radar image
            responseRadar = requests.get(radar_url, headers=self.header, timeout=10)
        except requests.exceptions.ConnectionError:
            print("Connection problems")
            time.sleep(5)
            
        if responseRadar: #If we can get a radar image
            radar = Image.open(BytesIO(responseRadar.content))
        else: #or if we can't
            print(f"\tCouldn't get radar image! ({responseRadar})")

        return radar
    
    def makeTransparent(self, image, transparency):
        ''' Make opague parts of a transparent image, transparent!

            Param image: The image to use.
            Param transparent: value between 0 & 255. 0 = full transparent, 255 = opaque.

            Returns a reconstructed image.
        '''
        #Make sure the image has an alpha channel
        image = image.convert("RGBA")

        #Do some array magic.
        img_array = np.array(image)
        img_array[:, :, 3] = (transparency * (img_array[:, :, :3] != 255).any(axis=2))

        return Image.fromarray(img_array)

    def getMap(self, mode = 'coordinate', zoom = 7, width = 320,  provider = 'stamen-toner'):

        size = (width, round(width * 0.75)) #

        if mode == "coordinate":
            # Use our lat/long (in secrets) and map size as the basis for the extent of the map.
            map = geotiler.Map( center=(self.lon,self.lat),
                                zoom=zoom,
                                size=(800,600)
                                #provider=provider
                                )
            
            map_labels = geotiler.Map(center=(self.lon,self.lat),
                                size=size,
                                zoom=zoom,
                                #provider='stamen-toner-labels'
                                )
            minx, miny, maxx, maxy = map.extent

        else:
            # Use the minx, miny, maxx, maxy extents from the radar layer.
            map = geotiler.Map( extent=(minx, miny, maxx, maxy),
                                zoom=zoom,
                                provider=provider)
            
            map_labels = geotiler.Map( extent=(minx, miny, maxx, maxy),
                                zoom=map.zoom,
                                provider='stamen-toner-labels')

        (map_center_x,map_center_y) = map.rev_geocode(map.center)
        base_map = geotiler.render_map(map)
        base_map_labels = geotiler.render_map(map_labels)

        minx, miny, maxx, maxy = map.extent
        return base_map, base_map_labels, map, [minx, miny, maxx, maxy, map.size]
    