import os
import subprocess
import pandas as pd
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
    # 確認有沒有連接到模擬器
    emulator_id = get_connected_emulator()
    if not emulator_id:
        print("未檢測到已連接的模擬器。請確認模擬器已經啟動。")
        return
    
    try:
        # 設定 GPS 位址
        command = f"adb -s {emulator_id} emu geo fix {latitude} {longitude}"
        result = os.system(command)
        if result == 0:
            print(f"GPS 位址已設置為經度: {latitude}, 緯度: {longitude}")
        else:
            print("無法設置 GPS 位址，請檢查 adb 連接狀態。")
    except Exception as e:
        print(f"執行時發生錯誤: {e}")

# 獲取已連接的模擬器 ID
def get_connected_emulator():
    try:
        # 執行 adb devices 列出所有連接的裝置
        output = subprocess.check_output("adb devices", shell=True).decode("utf-8")
        # 查找第一個模擬器裝置 (通常格式為 emulator-5554)
        lines = output.strip().split("\n")[1:]
        for line in lines:
            if "emulator" in line and "device" in line:
                return line.split("\t")[0]
    except Exception as e:
        print(f"無法獲取模擬器列表: {e}")
    return None
