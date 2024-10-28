from appium import webdriver

capabilities = dict(
    platformName='Android',
    automationName='uiautomator2',
    deviceName='Android',
    appPackage='com.hhaexchange.caregiver',
    appActivity='.AppLaunchActivity',
    language='en',
    locale='US'
)

appium_server_url = 'http://localhost:4723'

driver = webdriver.Remote(appium_server_url, capabilities)
