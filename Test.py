from main import setup_app, retry_login
from app_operate import Clock_out

account = "thehighpriestess5168@gmail.com"
password = "Moon1234!"
address = "384 Grand St, New York, NY 10002"

driver, wait = retry_login(account, password, address)
task_ids = "20, 22, 40, 47, 50, 51"
Clock_out(task_ids, driver, wait)