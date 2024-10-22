import subprocess
import re
import time
import random
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 隨機等待函數
def random_delay(min_delay=1, max_delay=3):
    delay = random.uniform(min_delay, max_delay)
    print(f"隨機等待 {delay:.2f} 秒")
    time.sleep(delay)

# 清除應用資料
def clear_app_data():
    try:
        subprocess.run(['adb', 'shell', 'pm', 'clear', 'com.hhaexchange.caregiver'], check=True)
        print("應用資料已清除")
    except subprocess.CalledProcessError as e:
        print(f"清除應用資料失敗: {e}")

# W3C Actions Tap 操作
def tap_element(driver, element):
    action = ActionChains(driver)
    # 獲取元素的中心位置
    x = element.location['x'] + (element.size['width'] / 2)
    y = element.location['y'] + (element.size['height'] / 2)
    
    # 模擬點擊行為
    random_delay
    action.w3c_actions.pointer_action.move_to_location(x, y)
    action.w3c_actions.pointer_action.pointer_down()
    action.w3c_actions.pointer_action.pointer_up()
    action.perform()
    random_delay

# 登入步驟
def login(driver, wait, account, password):
    next_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//android.widget.TextView[@content-desc='Next']")))
    tap_element(driver, next_button)

    allow_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//android.widget.Button[@resource-id='com.android.permissioncontroller:id/permission_allow_button']")))
    tap_element(driver, allow_button)

    allow_all_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//android.widget.Button[@resource-id='com.android.permissioncontroller:id/permission_allow_all_button']")))
    tap_element(driver, allow_all_button)

    email_input = wait.until(EC.visibility_of_element_located((By.XPATH, '//android.widget.EditText[@resource-id="com.hhaexchange.caregiver:id/txt_email"]')))
    password_input = wait.until(EC.visibility_of_element_located((By.XPATH, '//android.widget.EditText[@resource-id="com.hhaexchange.caregiver:id/txt_password"]')))
    email_input.send_keys(account)
    password_input.send_keys(password)

    login_button = driver.find_element(By.XPATH, '//android.widget.Button[@resource-id="com.hhaexchange.caregiver:id/btn_login"]')
    tap_element(driver, login_button)
    # 新增等待時間
    time.sleep(10)

# 打上班卡步驟
def Clock_in(driver, wait):
    clock_in_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//android.widget.Button[@resource-id="com.hhaexchange.caregiver:id/btn_clock_in"]')))
    tap_element(driver, clock_in_button)

    gps_title = wait.until(EC.element_to_be_clickable((By.XPATH, "//android.widget.TextView[@resource-id='com.hhaexchange.caregiver:id/label_title' and @text='GPS']")))
    tap_element(driver, gps_title)

    allow_foreground_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//android.widget.Button[@resource-id='com.android.permissioncontroller:id/permission_allow_foreground_only_button']")))
    tap_element(driver, allow_foreground_button)

    clock_in_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//android.widget.Button[@resource-id="com.hhaexchange.caregiver:id/btn_clock_in"]')))
    tap_element(driver, clock_in_button)

    gps_title = wait.until(EC.element_to_be_clickable((By.XPATH, "//android.widget.TextView[@resource-id='com.hhaexchange.caregiver:id/label_title' and @text='GPS']")))
    tap_element(driver, gps_title)

    # before click confirm, Sleep 10 sec
    time.sleep(10)
    confirm_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//android.widget.Button[@resource-id='com.hhaexchange.caregiver:id/btn_confirm']")))
    tap_element(driver, confirm_button)

    print('上班打卡成功')

# 打下班卡步驟
def Clock_out(task_ids, driver, wait):
    if not task_ids or pd.isna(task_ids):
        print("Task_ID 為空，使用預設的任務 ID 列表")
        task_ids = "20, 22, 40, 47, 50, 51"

    clock_out_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//android.widget.Button[@resource-id='com.hhaexchange.caregiver:id/btn_clock_out']")))
    tap_element(driver, clock_out_button)

    gps_title = wait.until(EC.element_to_be_clickable((By.XPATH, "//android.widget.TextView[@resource-id='com.hhaexchange.caregiver:id/label_title' and @text='GPS']")))
    tap_element(driver, gps_title)

    allow_foreground_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//android.widget.Button[@resource-id='com.android.permissioncontroller:id/permission_allow_foreground_only_button']")))
    tap_element(driver, allow_foreground_button)

    clock_out_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//android.widget.Button[@resource-id='com.hhaexchange.caregiver:id/btn_clock_out']")))
    tap_element(driver, clock_out_button)

    gps_title = wait.until(EC.element_to_be_clickable((By.XPATH, "//android.widget.TextView[@resource-id='com.hhaexchange.caregiver:id/label_title' and @text='GPS']")))
    tap_element(driver, gps_title)
    # before click confirm, Sleep 10 sec
    time.sleep(10)
    confirm_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//android.widget.Button[@resource-id='com.hhaexchange.caregiver:id/btn_confirm']")))
    tap_element(driver, confirm_button)

    all_task_texts = set()
    task_id_list = [task_id.strip() for task_id in task_ids.split(',')]

    while True:
        task_elements = driver.find_elements(By.ID, "com.hhaexchange.caregiver:id/lbl_task_id")
        last_element = task_elements[-1]

        for index, task_element in enumerate(task_elements, start=1):
            task_text = task_element.text
            match = re.match(r"(\d+) -", task_text)
            if match:
                task_id_in_text = match.group(1)

                if task_text not in all_task_texts:
                    print(f"任務 ID 的文本: {task_text}")
                    all_task_texts.add(task_text)

                    if task_id_in_text in task_id_list:
                        print(f"匹配到的任務 ID: {task_id_in_text}, 勾選該任務")
                        
                        checkbox_xpath = f"(//android.widget.CheckBox[@content-desc='Performed'])[{index}]"
                        checkbox_element = driver.find_element(By.XPATH, checkbox_xpath)
                        tap_element(driver, checkbox_element)

                        task_id_list.remove(task_id_in_text)

                        if not task_id_list:
                            print("所有任務已經勾選，結束操作")
                            save_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//android.widget.Button[@content-desc="Save"]')))
                            tap_element(driver, save_button)
                            print('下班打卡成功')
                            return

        if not task_id_list:
            break

        action = ActionChains(driver)
        action.w3c_actions.pointer_action.move_to_location(500, 1600)
        action.w3c_actions.pointer_action.pointer_down()
        action.w3c_actions.pointer_action.move_to_location(500, 1000)
        action.w3c_actions.pointer_action.pointer_up()
        action.perform()

        task_elements = driver.find_elements(By.ID, "com.hhaexchange.caregiver:id/lbl_task_id")

        if not task_elements or task_elements[-1].text == last_element.text:
            break
