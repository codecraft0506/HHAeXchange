import subprocess
import re
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 清除應用資料
def clear_app_data():
    try:
        subprocess.run(['adb', 'shell', 'pm', 'clear', 'com.hhaexchange.caregiver'], check=True)
        print("應用資料已清除")
    except subprocess.CalledProcessError as e:
        print(f"清除應用資料失敗: {e}")

# 登入步驟
def login(driver,wait,account,password):
    wait.until(EC.element_to_be_clickable((By.XPATH, "//android.widget.TextView[@content-desc='Next']"))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, "//android.widget.Button[@resource-id='com.android.permissioncontroller:id/permission_allow_button']"))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, "//android.widget.Button[@resource-id='com.android.permissioncontroller:id/permission_allow_all_button']"))).click()
    email_input = wait.until(EC.visibility_of_element_located((By.XPATH, '//android.widget.EditText[@resource-id="com.hhaexchange.caregiver:id/txt_email"]')))
    password_input = wait.until(EC.visibility_of_element_located((By.XPATH, '//android.widget.EditText[@resource-id="com.hhaexchange.caregiver:id/txt_password"]')))
    email_input.send_keys(account)
    password_input.send_keys(password)
    driver.find_element(By.XPATH, '//android.widget.Button[@resource-id="com.hhaexchange.caregiver:id/btn_login"]').click()

# 打上班卡步驟
def Clock_in(wait):
    print('當你上班打卡成功')
    #wait.until(EC.element_to_be_clickable((By.XPATH, '//android.widget.Button[@resource-id="com.hhaexchange.caregiver:id/btn_login"]'))).click()

# 打下班卡步驟
def Clock_out(task_ids,driver,wait):
    # # 如果 task_ids 為空值，使用預設的任務 ID
    # if not task_ids or pd.isna(task_ids):
    #     print("Task_ID 為空，使用預設的任務 ID 列表")
    #     task_ids = "20, 22, 40, 47, 50"  # 預設的任務 ID

    # wait.until(EC.element_to_be_clickable((By.XPATH, "//android.widget.Button[@resource-id='com.hhaexchange.caregiver:id/btn_clock_out']"))).click()
    # wait.until(EC.element_to_be_clickable((By.XPATH, "//android.widget.TextView[@resource-id='com.hhaexchange.caregiver:id/label_title' and @text='GPS']"))).click()
    # wait.until(EC.element_to_be_clickable((By.XPATH, "//android.widget.Button[@resource-id='com.android.permissioncontroller:id/permission_allow_foreground_only_button']"))).click()
    # wait.until(EC.element_to_be_clickable((By.XPATH, "//android.widget.Button[@resource-id='com.hhaexchange.caregiver:id/btn_clock_out']"))).click()
    # wait.until(EC.element_to_be_clickable((By.XPATH, "//android.widget.TextView[@resource-id='com.hhaexchange.caregiver:id/label_title' and @text='GPS']"))).click()
    # wait.until(EC.element_to_be_clickable((By.XPATH, "//android.widget.Button[@resource-id='com.hhaexchange.caregiver:id/btn_confirm']"))).click()

    # all_task_texts = set()  # 使用集合來避免重複

    # # 將 task_ids 拆分為單個 ID
    # task_id_list = [task_id.strip() for task_id in task_ids.split(',')]

    # while True:
    #     # 查找所有帶有 com.hhaexchange.caregiver:id/lbl_task_id 的元素
    #     task_elements = driver.find_elements(By.ID, "com.hhaexchange.caregiver:id/lbl_task_id")

    #     # 獲取當前頁面最後一個元素
    #     last_element = task_elements[-1]

    #     # 遍歷並處理每個元素
    #     for index, task_element in enumerate(task_elements, start=1):
    #         task_text = task_element.text  # 獲取元素的文本
    #         # 使用正則表達式提取任務 ID（假設任務 ID 是文本開頭的數字部分）
    #         match = re.match(r"(\d+) -", task_text)
    #         if match:
    #             task_id_in_text = match.group(1)  # 提取出數字的部分

    #             if task_text not in all_task_texts:  # 避免重複處理
    #                 print(f"任務 ID 的文本: {task_text}")
    #                 all_task_texts.add(task_text)  # 保存已找到的文本

    #                 # 如果任務 ID 匹配，則勾選該任務的 CheckBox
    #                 if task_id_in_text in task_id_list:
    #                     print(f"匹配到的任務 ID: {task_id_in_text}, 勾選該任務")
                        
    #                     # 構建 XPath 尋找與此元素對應的 CheckBox，使用 index 動態查找
    #                     checkbox_xpath = f"(//android.widget.CheckBox[@content-desc='Performed'])[{index}]"
    #                     checkbox_element = driver.find_element(By.XPATH, checkbox_xpath)
    #                     checkbox_element.click()  # 點擊該 CheckBox 進行勾選

    #                     # 將匹配的任務 ID 從列表中移除
    #                     task_id_list.remove(task_id_in_text)

    #                     # 如果所有任務都已經匹配並勾選完，跳出迴圈
    #                     if not task_id_list:
    #                         print("所有任務已經勾選，結束操作")
    #                         return
                        
    #     # 如果所有任務已經勾選完，跳出整個滾動和檢查流程
    #     if not task_id_list:
    #         break

    #     # 滾動頁面
    #     action = ActionChains(driver)
    #     action.w3c_actions.pointer_action.move_to_location(500, 1600)  # 起點位置
    #     action.w3c_actions.pointer_action.pointer_down()  # 按下屏幕
    #     action.w3c_actions.pointer_action.move_to_location(500, 400)  # 滑動至屏幕上方
    #     action.w3c_actions.pointer_action.pointer_up()  # 放開屏幕
    #     action.perform()

    #     # 滾動後，重新抓取 task_elements 並重新檢查
    #     task_elements = driver.find_elements(By.ID, "com.hhaexchange.caregiver:id/lbl_task_id")
        
    #     # 檢查是否滾動到最底部，如果滾動後的最後一個元素與滾動前的相同，則表示已經到底
    #     if not task_elements or task_elements[-1].text == last_element.text:
    #         break  # 滾動到底，停止滾動
    
    # 添加save.click()即可完成此涵式
    # wait.until(EC.element_to_be_clickable((By.XPATH, '//android.widget.Button[@content-desc="Save"]'))).click()
    print('當你下班打卡成功')