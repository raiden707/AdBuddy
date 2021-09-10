from geopy.geocoders import Nominatim
import time
from pprint import pprint

# instantiate a new Nominatim client
app = Nominatim(user_agent="tutorial")
def get_coords(place):
    """
    (list) -> (string,string,string)
    Returns the coordinates of the input place 
    """
    location_data = []


    location = app.geocode(place).raw
    location_data.append(place)
    location_data.append( location['lat'])
    location_data.append(location['lon'])
    return location_data


