import os
from opencage.geocoder import OpenCageGeocode
from dotenv import load_dotenv
load_dotenv()

openCageGeocode_key = os.getenv('OpenCageGeocod_KEY')

# 透過地址查找經緯度
def get_lat_long(address):
    geocoder = OpenCageGeocode(openCageGeocode_key)
    result = geocoder.geocode(address)
    if result:
        lat = result[0]['geometry']['lat']
        lng = result[0]['geometry']['lng']
        # For Test
        # print(f"地址: {address}, 經度: {lng}, 緯度: {lat}")
        return lng, lat
    else:
        print("地址無法找到")
        return None, None

# 設置虛擬機GPS位址
def set_virtual_location(latitude, longitude):
    os.system(f"adb emu geo fix {latitude} {longitude}")