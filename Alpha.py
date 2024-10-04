import os
from opencage.geocoder import OpenCageGeocode

# 透過地址查找經緯度
def get_lat_long(address):
    key = 'OpenCage API KEY'  # 替換為你的 OpenCage API 金鑰
    geocoder = OpenCageGeocode(key)
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
    status = os.system(f"adb emu geo fix {latitude} {longitude}")
    if status == 0:
        print("虛擬位置設置成功")
    else:
        print("虛擬位置設置失敗: 未偵測到模擬器")

if __name__ == "__main__":
    # 根據打卡人地址去判斷經緯度，而後設置虛擬位置
    address = '384 Grand St, New York, NY 10002'
    longitude, latitude = get_lat_long(address)
    if longitude is not None and latitude is not None:
        set_virtual_location(longitude, latitude)  # 设置虚拟位置
