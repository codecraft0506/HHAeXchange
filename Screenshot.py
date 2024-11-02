from appium import webdriver

desired_caps = {
    "platformName": "Android",
    "deviceName": "emulator-5554",
    "automationName": "UiAutomator2",
}

appium_server_url = 'http://localhost:4723'

# 連接 Appium 伺服器
driver = webdriver.Remote(appium_server_url, desired_caps)

# 截圖並儲存
screenshot_path = "./screenshot.png"
driver.get_screenshot_as_file(screenshot_path)
print(f"Screenshot saved at {screenshot_path}")

# 關閉驅動
driver.quit()

