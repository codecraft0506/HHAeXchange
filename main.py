import threading
import pandas as pd
import os
import time
import pytz
import io
import base64
import logging
from PIL import Image
from datetime import datetime
from appium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from Schedule_Function import load_schedule_with_mod_time
from Schedule_Function import get_new_shifts
from app_operate import clear_app_data, login, Clock_in, Clock_out
from Set_Location import get_lat_long, set_virtual_location
from notify import send_notification

file_lock = threading.Lock()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 获取脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))

# 设置 Appium driver
def setup_app():
    desired_caps = {
        "platformName": "Android",
        "platformVersion": "15",
        "deviceName": "emulator-5554",
        "automationName": "UiAutomator2",
        "appPackage": "com.hhaexchange.caregiver",
        "appActivity": "com.hhaexchange.caregiver.AppLaunchActivity",
        "noReset": True,
        "fullReset": False,
        "sessionOverride": True
    }
    try:
        driver = webdriver.Remote('http://localhost:4723', desired_caps)
        return driver
    except Exception as e:
        logging.error(f"初始化 Appium driver 时发生错误: {e}")
        return None

# 读取 Action_Schedule.csv 并检查数据笔数
def check_action_schedule():
    action_schedule_path = os.path.join(script_dir, 'Action_Schedule.csv')
    if os.path.exists(action_schedule_path):
        action_df = pd.read_csv(action_schedule_path)
        if len(action_df) <= 3:
            logging.info("提醒用戶更新 Schedule.csv")
            send_notification("需要更新 Schedule.csv了")
    else:
        logging.error("Action_Schedule.csv 不存在")

# 使用更新后的 load_schedule_with_mod_time 来检查更新时间
def check_schedule_update(last_mod_time):
    schedule_df, current_mod_time = load_schedule_with_mod_time()
    if current_mod_time != last_mod_time:
        logging.info("Schedule.csv 有更新，開始更新 Action_Schedule.csv")
        update_action_schedule(schedule_df)
        return current_mod_time
    return last_mod_time

# 更新 Action_Schedule.csv 的逻辑
def update_action_schedule(schedule_df):
    with file_lock:
        # 获取新班次
        new_shifts_df = get_new_shifts()

        # 定义文件路径
        action_schedule_path = os.path.join(script_dir, 'Action_Schedule.csv')

        if os.path.exists(action_schedule_path):
            # 读取现有的班次
            existing_shifts_df = pd.read_csv(action_schedule_path)

            # 合并并去重
            combined_shifts_df = pd.concat([existing_shifts_df, new_shifts_df], ignore_index=True)
            combined_shifts_df.drop_duplicates(subset=['User', 'Action', 'Origin_Date', 'Original_Punch_In_Time'], inplace=True)

            # 可选：删除已过期的班次
            today = datetime.now().strftime('%Y-%m-%d')
            combined_shifts_df = combined_shifts_df[combined_shifts_df['Origin_Date'] >= today]

            # 保存更新
            combined_shifts_df.to_csv(action_schedule_path, index=False)
        else:
            # 保存新的班次
            new_shifts_df.to_csv(action_schedule_path, index=False)

        logging.info("Action_Schedule.csv 已更新")

# 使用多线程更新 Action_Schedule.csv
def schedule_update_thread():
    schedule_df, last_mod_time = load_schedule_with_mod_time()
    while True:
        time.sleep(60)
        schedule_df, current_mod_time = load_schedule_with_mod_time()
        if current_mod_time != last_mod_time:
            logging.info("Schedule.csv 有更新，開始更新 Action_Schedule.csv")
            update_action_schedule(schedule_df)
            last_mod_time = current_mod_time

def retry_login(account, password):
    max_attempts = 10
    attempts = 0
    success = False
    driver = None
    while attempts < max_attempts and not success:
        try:
            clear_app_data()
            driver = setup_app()
            if driver is None:
                raise Exception("无法初始化 Appium driver")
            wait = WebDriverWait(driver, 10)

            # 登录并执行动作
            login(driver, wait, account, password)
            wait.until(EC.element_to_be_clickable((
                By.XPATH, '//android.widget.LinearLayout[@resource-id="com.hhaexchange.caregiver:id/layout_list_home"]/android.widget.RelativeLayout[3]'
            ))).click()
            success = True
            return driver, wait
        except Exception as e:
            logging.info(f"第 {attempts + 1} 次尝试失败，错误: {e}")
            attempts += 1
            # 关闭驱动程序并等待一段时间后再重试
            if driver:
                driver.quit()
                driver = None
            time.sleep(5)
            # time.sleep(200)
    if not success:
        logging.error("多次嘗試登入失敗，請檢查網路連線或帳號密碼。")
        # 在这里添加失败后的处理逻辑，例如跳过此排程或通知用户
        send_notification("多次嘗試登入失敗，請檢查網路連線或帳號密碼。", account)
        return None, None

# 根据 action 执行操作
def execute_action(wait, driver, action_type, Schedule_Date_formatted, Punch_In_Time, Punch_Out_Time, task_ids, user, Clock=True):
    if driver is None or wait is None:
        logging.error("driver 或 wait 为空，无法执行操作")
        return

    def get_element_text(item, xpath, default="無時間"):
        try:
            element = item.find_element(By.XPATH, xpath)
            return element.text.strip() if element.text else default
        except:
            return default
        
    def get_element(item, xpath):
        try:
            return item.find_element(By.XPATH, xpath)
        except:
            return None  # 如果元素不存在，返回 None
    
    def check_status(pixel_color):
        # 成功狀態顏色
        success_color = (91, 164, 64, 255)
        # 失敗狀態顏色
        failure_color = (232, 68, 68, 255)

        if pixel_color == success_color:
            logging.info("狀態：成功")
            send_notification("打卡成功", user)
            return "成功"
        elif pixel_color == failure_color:
            logging.info("狀態：失敗")
            send_notification("打卡失敗", user)
            return "失敗"
        else:
            logging.info("狀態：未打卡")
            send_notification("未打卡", user)
            return "未打卡"

    # 等待列表加载完成
    try:
        wait.until(EC.visibility_of_element_located((By.XPATH, '//android.widget.ListView[@resource-id="com.hhaexchange.caregiver:id/list_today_schedule"]')))
    except Exception as e:
        logging.error(f"無法加載列表，錯誤: {e}")
        return

    max_scroll_attempts = 5  # 調整滾動次數限制
    scroll_attempt = 0

    while scroll_attempt < max_scroll_attempts:
        try:
            # 查找所有 RelativeLayout 子項
            list_items = driver.find_elements(By.XPATH, '//android.widget.ListView[@resource-id="com.hhaexchange.caregiver:id/list_today_schedule"]/android.widget.RelativeLayout')
        except Exception as e:
            logging.error(f"無法找到列表項目，錯誤: {e}")
            continue

        if list_items:
            # 遍歷列表項目並匹配操作
            for item in list_items:
                punch_in_text = get_element_text(item, './/android.widget.TextView[@resource-id="com.hhaexchange.caregiver:id/lbl_schedule_start_time"]')
                punch_out_text = get_element_text(item, './/android.widget.TextView[@resource-id="com.hhaexchange.caregiver:id/lbl_schedule_end_time"]')
                date_text = get_element_text(item, './/android.widget.TextView[@resource-id="com.hhaexchange.caregiver:id/lbl_date"]', "無日期")
                imgStartTime = get_element(item, './/android.widget.ImageView[@resource-id="com.hhaexchange.caregiver:id/imgStartTime"]')
                imgEndTime = get_element(item, './/android.widget.ImageView[@resource-id="com.hhaexchange.caregiver:id/imgEndTime"]')

                # 根據 action 匹配時間和日期
                if action_type == "Punch In" and punch_in_text == Punch_In_Time and date_text == Schedule_Date_formatted:
                    if Clock:
                        logging.info(f"找到匹配上班日期: {date_text} 和時間: {punch_in_text}")
                        item.click()
                        Clock_in(wait)  # 執行打卡
                        return
                    else:
                        # 1. 截取整個畫面
                        screenshot = driver.get_screenshot_as_base64()

                        # 2. 使用 Pillow 讀取截圖
                        image = Image.open(io.BytesIO(base64.b64decode(screenshot)))
                        if imgStartTime is not None:
                            # 3. 元素的位置和大小
                            location = imgStartTime.location
                            size = imgStartTime.size
                            x, y = location['x'], location['y']
                            width, height = size['width'], size['height']

                            # 4. 定義裁剪區域，(left, upper, right, lower)
                            box = (x, y, x + width, y + height)

                            # 5. 裁剪圖像
                            imgStartTime_image = image.crop(box)
                            # 測試用截圖
                            # imgStartTime_image.save("imgStartTime_image.png")
                            # 6. 獲取最左側且垂直至中的像素顏色
                            left_x = 0  # 水平最左側
                            center_y = height // 2  # 垂直中間
                            pixel_color = imgStartTime_image.getpixel((left_x, center_y))  # 使用 left_x 和 center_y

                            status = check_status(pixel_color)
                        else:
                            logging.error("imgEndTime 元素未找到，無法進行截圖操作，可能是尚未打卡或APP尚未更新狀態")
                            send_notification("imgEndTime 元素未找到，無法進行截圖操作，可能是尚未打卡或APP尚未更新狀態", user)
                        return

                elif action_type == "Punch Out" and punch_out_text == Punch_Out_Time and date_text == Schedule_Date_formatted:
                    if Clock:
                        logging.info(f"找到匹配下班日期: {date_text} 和時間: {punch_out_text}")
                        item.click()
                        logging.info('執行下班打卡操作')
                        Clock_out(task_ids, driver, wait)  # 執行打卡
                        return
                    else:
                        # 1. 截取整個畫面
                        screenshot = driver.get_screenshot_as_base64()

                        # 2. 使用 Pillow 讀取截圖
                        image = Image.open(io.BytesIO(base64.b64decode(screenshot)))
                        # 先確定 imgEndTime 是否存在
                        if imgEndTime is not None:
                            # 3. 元素的位置和大小
                            location = imgEndTime.location
                            size = imgEndTime.size
                            x, y = location['x'], location['y']
                            width, height = size['width'], size['height']

                            # 4. 定義裁剪區域，(left, upper, right, lower)
                            box = (x, y, x + width, y + height)

                            # 5. 裁剪圖像
                            imgEndTime_image = image.crop(box)
                            # 測試用截圖
                            # imgEndTime_image.save("imgEndTime_image.png")
                            # 6. 獲取最左側且垂直至中的像素顏色
                            left_x = 0  # 水平最左側
                            center_y = height // 2  # 垂直中間
                            pixel_color = imgEndTime_image.getpixel((left_x, center_y))  # 使用 left_x 和 center_y

                            status = check_status(pixel_color)
                        else:
                            logging.error("imgEndTime 元素未找到，無法進行截圖操作，可能是尚未打卡或APP尚未更新狀態")
                            send_notification("imgEndTime 元素未找到，無法進行截圖操作，可能是尚未打卡或APP尚未更新狀態", user)
                        return

        # 每次滾動後更新滾動次數
        scroll_attempt += 1

        # 滾動頁面
        try:
            action = ActionChains(driver)
            action.w3c_actions.pointer_action.move_to_location(500, 1600)  # 起點位置
            action.w3c_actions.pointer_action.pointer_down()  # 按下屏幕
            action.w3c_actions.pointer_action.move_to_location(500, 400)  # 滑動至屏幕上方
            action.w3c_actions.pointer_action.pointer_up()  # 放開屏幕
            action.perform()

        except Exception as e:
            logging.error(f"W3C 滾動失敗，錯誤: {e}")

    logging.error("未找到匹配的項目，操作失敗")

# 檢查打卡狀態是否成功
def check_action_status(driver, action):
    logging.info('打卡狀態檢查成功')

# 刪除已成功打卡的 Action_Schedule.csv 中的資料
def delete_action_from_schedule(row_to_delete):
    with file_lock:
        action_schedule_path = os.path.join(script_dir, 'Action_Schedule.csv')
        action_schedule = pd.read_csv(action_schedule_path)

        # 将 row_to_delete 转换为 DataFrame
        row_df = row_to_delete.to_frame().T

        # 处理缺失值
        action_schedule.fillna('', inplace=True)
        row_df.fillna('', inplace=True)

        # 定义用于比较的列
        columns_to_compare = ['Time', 'Origin_Date', 'Action', 'User', 'Account', 'Password', 'Address', 'Task_ID',
                            'Original_Punch_In_Time', 'Original_Punch_Out_Time', 'Time Zone']

        # 确保所有列都存在
        for col in columns_to_compare:
            if col not in action_schedule.columns:
                action_schedule[col] = ''
            if col not in row_df.columns:
                row_df[col] = ''

        # 将所有用于比较的列转换为字符串并去除空格
        for col in columns_to_compare:
            action_schedule[col] = action_schedule[col].astype(str).str.strip()
            row_df[col] = row_df[col].astype(str).str.strip()

        # 统一日期格式
        action_schedule['Origin_Date'] = pd.to_datetime(action_schedule['Origin_Date'], errors='coerce').dt.strftime('%Y-%m-%d')
        row_df['Origin_Date'] = pd.to_datetime(row_df['Origin_Date'], errors='coerce').dt.strftime('%Y-%m-%d')

        # 创建布尔掩码
        mask = pd.Series([True] * len(action_schedule))

        for col in columns_to_compare:
            mask &= action_schedule[col] == row_df.iloc[0][col]

        # 打印调试信息
        logging.debug("用于比较的列的值：")
        logging.debug("row_df：")
        logging.debug(row_df[columns_to_compare])
        logging.debug("action_schedule：")
        logging.debug(action_schedule[columns_to_compare])
        logging.debug("匹配掩码：")
        logging.debug(mask)

        if mask.any():
            action_schedule = action_schedule[~mask]
            action_schedule.to_csv(action_schedule_path, index=False)
            logging.info(f"已删除用户 {row_df.iloc[0]['User']} 的动作 {row_df.iloc[0]['Action']}。")
        else:
            logging.error("未找到匹配的行进行删除。")

# 主邏輯
def main():
    action_schedule_path = os.path.join(script_dir, 'Action_Schedule.csv')
    action_schedule = pd.read_csv(action_schedule_path)
    driver = None
    for index, row in action_schedule.iterrows():
        check_action_schedule()
        action_time_str = row['Time']
        Schedule_Date_str = row['Origin_Date']
        Punch_In_Time = row['Original_Punch_In_Time']
        Punch_Out_Time = row["Original_Punch_Out_Time"]
        user = row['User']
        action = row['Action']
        account = row['Account']
        password = row['Password']
        address = row['Address']
        task_ids = row['Task_ID']
        Time_Zone = row['Time Zone']

        # 解析 Schedule_Date
        Schedule_Date = datetime.strptime(Schedule_Date_str, '%Y-%m-%d')
        Schedule_Date_formatted = Schedule_Date.strftime("%m/%d/%Y")

        # # 如果时区为空，默认使用美东时间
        # if pd.isna(Time_Zone) or Time_Zone.strip() == '':
        #     Time_Zone = 'America/New_York'  # 默认美东时间

        # # 设置时区
        # local_tz = pytz.timezone(Time_Zone)
        # now_utc = datetime.now(pytz.utc)  # 获取当前UTC时间
        # now_local = now_utc.astimezone(local_tz)  # 转换为指定时区时间

        # # 解析 action_time_str
        # try:
        #     # 根据 CSV 中的时间格式进行解析
        #     action_time = datetime.strptime(action_time_str, '%Y-%m-%d %H:%M:%S')
        #     action_time = local_tz.localize(action_time)
        # except ValueError as ve:
        #     logging.error(f"无法解析时间 '{action_time_str}'，错误: {ve}")
        #     continue  # 如果解析失败，跳过当前循环

        # # 計算當前時間與打卡時間之間的差異
        # time_difference = (action_time - now_local).total_seconds()

        # # 如果當前時間尚未達到打卡時間，則計算等待的時間（幾時幾分幾秒）
        # if time_difference > 0:
        #     hours, remainder = divmod(time_difference, 3600)  # 計算小時
        #     minutes, seconds = divmod(remainder, 60)  # 計算分鐘和秒
        #     logging.info(f"等待 {int(hours)} 小時 {int(minutes)} 分 {int(seconds)} 秒，執行 {user} 在 {action_time} 的 {action} 動作")
        #     time.sleep(time_difference)

        # 虛擬機模擬定位
        if isinstance(address, str) and not pd.isna(address):
            longitude, latitude = get_lat_long(address)
            if longitude is not None and latitude is not None:
                set_virtual_location(longitude, latitude)
            else:
                longitude, latitude = get_lat_long("384 Grand St, Test2 York, NY 10002")
                set_virtual_location(longitude, latitude)

        # 清除應用快取並啟動 Appium session
        driver, wait = retry_login(account, password)

        if driver and wait:
            # 執行打卡操作
            execute_action(wait, driver, action, Schedule_Date_formatted, Punch_In_Time, Punch_Out_Time, task_ids, user, Clock=True)
            time.sleep(5)

            # 清除應用快取並重新啟動 Appium session
            driver.quit()
            driver = None
            driver, wait = retry_login(account, password)

            if driver and wait:
                execute_action(wait, driver, action, Schedule_Date_formatted, Punch_In_Time, Punch_Out_Time, task_ids, user, Clock=False)
                delete_action_from_schedule(row)  # 傳遞 row 而不是 index
                # 關閉當前的 session
                driver.quit()
                driver = None
            else:
                logging.error("應用重啟失敗，跳過當前排程")
                continue
        else:
            logging.error("登入失敗，跳過當前排程")
            continue

    # 關閉最後的 session
    if driver:
        driver.quit()

if __name__ == "__main__":
    # 啟動多線程檢查 Schedule.csv 的更新
    thread = threading.Thread(target=schedule_update_thread)
    thread.daemon = True  # 設置為守護進程，主進程結束時子線程也會結束
    thread.start()

    # 執行打卡操作的主邏輯
    main()
