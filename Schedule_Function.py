import pandas as pd
import re
import os
from datetime import datetime, timedelta

schedule_file_path = './Schedule.csv'
variable_file_path = './variable.csv'  # 添加 variable.csv 文件路徑
account_file_path = './Account.csv'
taskid_file_path = './taskid.csv'

# 加載 Schedule.csv 並檢查更新時間
def load_schedule_with_mod_time():
    mod_time = os.path.getmtime(schedule_file_path)  # 獲取最後修改時間
    schedule_df = pd.read_csv(schedule_file_path, encoding='ISO-8859-1')  # 加載文件
    return schedule_df, mod_time

# 讀取 variable.csv 文件
def load_variables():
    return pd.read_csv(variable_file_path, usecols=['User', 'Time Zone', 'Address', 'Schedule'])

# 讀取 Account.csv 文件
def load_account():
    return pd.read_csv(account_file_path, usecols=['User', 'Account', 'Password'])

# 讀取 taskid.csv 文件，並將 Schedule_Date 列格式化為 'YYYY-MM-DD'
def load_taskid():
    taskid_df = pd.read_csv(taskid_file_path, usecols=['User', 'Task_ID', 'Schedule_Date', 'Original_Punch_In_Time', 'Original_Punch_Out_Time'])
    
    # 格式化 Schedule_Date 為 'YYYY-MM-DD'
    taskid_df['Schedule_Date'] = pd.to_datetime(taskid_df['Schedule_Date'], format='%Y-%m-%d', errors='coerce').dt.strftime('%Y-%m-%d')
    
    return taskid_df

# 格式化列名中的日期
def format_date_columns(df):
    new_columns = []
    for col in df.columns:
        if re.match(r'\d{4}/\d{1,2}/\d{1,2}', col):
            formatted_col = datetime.strptime(col, '%Y/%m/%d').strftime('%Y/%m/%d')
            new_columns.append(formatted_col)
        else:
            new_columns.append(col)
    df.columns = new_columns
    return df

# 清理時間範圍中的無效字符並去除多餘空格
def clean_time_string(time_str):
    return re.sub(r'[^\d,-]', '', time_str).strip()

# 將時間範圍拆分並轉換為整數，並且返回時間與用戶的序列
def parse_time_ranges(time_range_str, user, date_col, time_zone=None, address=None):
    if pd.isna(time_range_str):
        return []
    
    time_ranges = []
    time_range_str = clean_time_string(time_range_str)
    ranges = time_range_str.split(',')
    
    for time_range in ranges:
        time_range = time_range.strip()
        try:
            need_punch_in_day = datetime.strptime(date_col, '%Y/%m/%d')
            need_punch_out_day = need_punch_in_day
            start, end = map(int, time_range.split('-'))

            if start == 0:
                need_punch_in_day -= timedelta(days=1)
                start_hour = 23
                start_minute = 59
            else:
                start_hour = start
                start_minute = 0

            if end == 24 or end == 0:
                need_punch_out_day += timedelta(days=1)
                end_hour = 0
                end_minute = 0
            else:
                end_hour = end
                end_minute = 0

            shift = {
                'User': user,
                'Punch_In_Hour': start_hour,
                'Punch_In_Minute': start_minute,
                'Punch_Out_Hour': end_hour,
                'Punch_Out_Minute': end_minute,
                'need_punch_in_day': need_punch_in_day.strftime('%Y/%m/%d'),
                'need_punch_out_day': need_punch_out_day.strftime('%Y/%m/%d'),
                'Origin_Date': date_col,  # 新增原始日期
                'Time Zone': time_zone,  # 保留 Time Zone 信息
                'Address': address  # 保留 Address 信息
            }
            time_ranges.append(shift)

        except ValueError as e:
            print(f"無法解析時間範圍：{time_range}，錯誤：{e}，跳過該範圍")

    return time_ranges



# 加載所有班次，基於 schedule_df 的日期列來初始化
def load_all_shifts(schedule_df):
    # 過濾掉非日期列，只保留日期和時間範圍列
    date_columns = [col for col in schedule_df.columns if re.match(r'\d{4}/\d{1,2}/\d{1,2}', col)]
    all_shifts = []
    
    # 遍歷每個日期列
    for date_col in date_columns:
        # 保留日期列以及 Time Zone 和 Address 列
        day_schedule = schedule_df[['User', 'Time Zone', 'Address', date_col]].dropna(subset=[date_col])  # 只保留有時間範圍數據的行
        for index, row in day_schedule.iterrows():
            # 解析時間範圍，並初始化班次，傳遞 Time Zone 和 Address
            shifts = parse_time_ranges(row[date_col], row['User'], date_col, row['Time Zone'], row['Address'])
            all_shifts.extend(shifts)

    # 根據上班日期和上班時間排序
    sorted_shifts = sorted(all_shifts, key=lambda x: (x['need_punch_in_day'], x['Punch_In_Hour'], x['Punch_Out_Hour']))
    return sorted_shifts

# 合併 variable.csv 中的 Time Zone 和 Address，根據 User 和 schedule_df 中的日期列來匹配
def merge_schedule_with_variables(schedule_df, variables_df):
    # 創建一個空的列表來保存合併後的結果
    merged_results = []

    # 遍歷 Schedule.csv 中的每一列（班次日期），排除 'User' 列
    for date_col in schedule_df.columns:
        if date_col == 'User':
            continue  # 跳過 'User' 列

        # 提取當前日期的班次 (即該日期的列)
        day_schedule = schedule_df[['User', date_col]].dropna(subset=[date_col])

        # 添加一個 `Day` 變數作為上下班打卡日期
        day_schedule['Day'] = date_col

        # 使用 left join，這樣即使沒有匹配的 Time Zone 或 Address 也不會過濾掉
        merged_day = pd.merge(day_schedule, variables_df, how='left', left_on=['User', 'Day'], right_on=['User', 'Schedule'])

        # 刪除 'Schedule' 列（因為它是 variables_df 中的列，已無需保存）
        merged_day.drop(columns=['Schedule'], inplace=True)

        # 保存合併後的結果
        merged_results.append(merged_day)

    # 將所有合併結果拼接成一個 DataFrame
    merged_df = pd.concat(merged_results, ignore_index=True)

    # 刪除 'Day' 列，因為它只是臨時用來匹配日期的
    merged_df.drop(columns=['Day'], inplace=True)

    # 排序列，使日期按順序排列，User 列始終在最前
    date_columns = sorted([col for col in merged_df.columns if re.match(r'\d{4}/\d{1,2}/\d{1,2}', col)], key=lambda x: pd.to_datetime(x, format='%Y/%m/%d'))
    sorted_columns = ['User', 'Time Zone', 'Address'] + date_columns

    # 重新設置列的順序
    merged_df = merged_df[sorted_columns]

    return merged_df

def merge_accounts_to_shifts(shifts_df, accounts_df):
    # 合併帳號和密碼到打卡表中
    merged_df = pd.merge(shifts_df, accounts_df, how='left', on='User')
    return merged_df

# 在同一時間點，先進行上班打卡再進行下班打卡
def simulate_punch_in_out(shifts_df):
    actions = []
    
    # 遍歷每一行 (班次) 並生成打卡記錄
    for index, shift in shifts_df.iterrows():
        punch_in_day = shift['need_punch_in_day']
        punch_out_day = shift['need_punch_out_day']
        origin_date = shift['Origin_Date']  # 取得原始日期
        
        # 原生的上班打卡事件（不提前5分鐘）
        original_punch_in_time = datetime.strptime(f"{punch_in_day} {shift['Punch_In_Hour']:02d}:{shift['Punch_In_Minute']:02d}", "%Y/%m/%d %H:%M")
        punch_in_time = original_punch_in_time - timedelta(minutes=5)

        # 檢查是否是 23:59，如果是則強制轉換為 12:00AM
        if original_punch_in_time.hour == 23 and original_punch_in_time.minute == 59:
            formatted_punch_in_time = '12:00AM'
        else:
            formatted_punch_in_time = original_punch_in_time.strftime('%I:%M%p')

        # 新增上班打卡時間及 Origin_Date
        actions.append({
            'User': shift['User'],
            'Time': punch_in_time,
            'Original_Punch_In_Time': formatted_punch_in_time,
            'Original_Punch_Out_Time': pd.NaT,
            'Action': 'Punch In',
            'Time Zone': shift.get('Time Zone', 'NaN'),
            'Address': shift.get('Address', 'NaN'),
            'Account': shift.get('Account', 'NaN'),
            'Password': shift.get('Password', 'NaN'),
            'Origin_Date': datetime.strptime(shift['Origin_Date'], '%Y/%m/%d').strftime('%Y-%m-%d')  # 轉為 YYYY-MM-DD 格式
        })

        # 原生的下班打卡事件
        original_punch_out_time = datetime.strptime(f"{punch_out_day} {shift['Punch_Out_Hour']:02d}:{shift['Punch_Out_Minute']:02d}", "%Y/%m/%d %H:%M")

        # 下班打卡，將時間格式化為 12 小時制
        formatted_punch_out_time = original_punch_out_time.strftime('%I:%M%p')

        # 新增下班打卡時間及 Origin_Date
        actions.append({
            'User': shift['User'],
            'Time': original_punch_out_time,
            'Original_Punch_In_Time': pd.NaT,
            'Original_Punch_Out_Time': formatted_punch_out_time,
            'Action': 'Punch Out',
            'Time Zone': shift.get('Time Zone', 'NaN'),
            'Address': shift.get('Address', 'NaN'),
            'Account': shift.get('Account', 'NaN'),
            'Password': shift.get('Password', 'NaN'),
            'Origin_Date': datetime.strptime(shift['Origin_Date'], '%Y/%m/%d').strftime('%Y-%m-%d')  # 轉為 YYYY-MM-DD 格式
        })

    # 按時間排序
    actions = sorted(actions, key=lambda x: (x['Time'], x['Action']))
    
    # 轉換為 DataFrame
    actions_df = pd.DataFrame(actions)

    return actions_df

# 檢查是否有班次已經錯過，並剔除列表中已錯過的班次
def remove_missed_shifts(shifts_df):
    current_time = datetime.now()  # 獲取當前時間
    remaining_shifts = []

    for index, shift in shifts_df.iterrows():
        # 獲取打卡時間
        punch_in_time = shift['Time']
        user = shift['User']

        # 檢查是否是上班還是下班打卡
        if shift['Action'] == 'Punch In':
            if current_time > punch_in_time:
                # 如果當前時間已經超過了上班時間，這個班次可能錯過了
                print(f"已經錯過上班: {user} {punch_in_time.strftime('%Y-%m-%d %H:%M:%S')}")
                continue  # 略過該班次
            else:
                # 如果還未錯過上班，保留該班次
                remaining_shifts.append(shift)
        elif shift['Action'] == 'Punch Out':
            if current_time < punch_in_time:
                # 如果當前時間在下班時間之前，保留班次
                remaining_shifts.append(shift)
            else:
                print(f"已經錯過下班: {user} {punch_in_time.strftime('%Y-%m-%d %H:%M:%S')}")
                continue  # 略過該班次

    # 返回剩餘的班次
    remaining_shifts_df = pd.DataFrame(remaining_shifts)
    return remaining_shifts_df

def Insert_taskid(remaining_shifts, taskid_df):
    # 遍歷 remaining_shifts DataFrame 中的每一行
    for index, shift in remaining_shifts.iterrows():
        user = shift['User']
        origin_date = shift['Origin_Date']  # 格式為 'YYYY-MM-DD'
        punch_in_time = shift['Original_Punch_In_Time']
        punch_out_time = shift['Original_Punch_Out_Time']
        
        # 遍歷 taskid_df，查找匹配的 Task_ID
        for idx, task_row in taskid_df.iterrows():
            if task_row['User'] == user and task_row['Schedule_Date'] == origin_date:
                # 根據 Punch In 和 Punch Out 的時間進行匹配
                if not pd.isna(punch_in_time) and punch_in_time == task_row['Original_Punch_In_Time']:
                    remaining_shifts.at[index, 'Task_ID'] = task_row['Task_ID']
                elif not pd.isna(punch_out_time) and punch_out_time == task_row['Original_Punch_Out_Time']:
                    remaining_shifts.at[index, 'Task_ID'] = task_row['Task_ID']

    return remaining_shifts

    # 提供給主程式獲取新班表的涵式
def get_new_shifts():
    # 這裡的邏輯使用你提供的流程來生成新的班次數據
    schedule_df, _ = load_schedule_with_mod_time()  # 加載 Schedule.csv 文件
    variables_df = load_variables()  # 加載 variable.csv 文件

    # 合併 schedule_df 和 variables_df
    merged_df = merge_schedule_with_variables(schedule_df, variables_df)

    # 初始化班次
    sorted_shifts = load_all_shifts(merged_df)
    shifts_df = pd.DataFrame(sorted_shifts)

    # 加載 Account.csv 文件
    accounts_df = load_account()

    # 合併帳號密碼到打卡表
    final_df = merge_accounts_to_shifts(shifts_df, accounts_df)

    # 模擬打卡時間
    final_df = simulate_punch_in_out(final_df)

    # 檢查並剔除已經錯過的班次
    remaining_shifts = remove_missed_shifts(final_df)

    # 加載 taskid.csv 文件
    taskid_df = load_taskid()

    # 插入 Task_ID
    remaining_shifts = Insert_taskid(remaining_shifts, taskid_df)

    return remaining_shifts  # 返回新的班次 DataFrame


# 第一次執行獲取Action_Schedule.csv
if __name__ == "__main__":
    schedule_df, _ = load_schedule_with_mod_time()  # 加載 Schedule.csv 文件
    variables_df = load_variables()  # 加載 variable.csv 文件

    # 合併 schedule_df 和 variables_df
    merged_df = merge_schedule_with_variables(schedule_df, variables_df)

    # 初始化班次
    sorted_shifts = load_all_shifts(merged_df)
    shifts_df = pd.DataFrame(sorted_shifts)

    # 加載 Account.csv 文件
    accounts_df = load_account()

    # 合併帳號密碼到打卡表
    final_df = merge_accounts_to_shifts(shifts_df, accounts_df)

    # 模擬打卡時間
    final_df = simulate_punch_in_out(final_df)

    # 檢查並剔除已經錯過的班次
    remaining_shifts = remove_missed_shifts(final_df)

    # 加載 taskid.csv 文件
    taskid_df = load_taskid()

    # 插入 Task_ID
    remaining_shifts = Insert_taskid(remaining_shifts, taskid_df)
    if 'Task_ID' not in remaining_shifts.columns:
        remaining_shifts['Task_ID'] = ''

    # 保存最終的結果
    output_file_path = './Action_Schedule.csv'
    remaining_shifts.to_csv(output_file_path, index=False, encoding='utf-8-sig')

    print(f"已成功將剩餘的班次保存至 {output_file_path}")


    
