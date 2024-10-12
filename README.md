# 自動打卡系統

此專案透過 Python、Appium 和 Android Studio 模擬器來實現自動化任務執行。

## 目錄
1. [安裝需求](#安裝需求)
2. [環境設定](#環境設定)
3. [檔案準備](#檔案準備)
4. [操作流程](#操作流程)
5. [資料格式](#資料格式)
6. [注意事項](#注意事項)
7. [問題排除](#問題排除)

---

### 1. 安裝需求

#### 基本軟體
- **[Python](https://www.python.org/downloads/)**：3.8 或以上版本
- **[Android Studio](https://developer.android.com/studio?hl=zh-tw)**：安裝並建立 Android 模擬器
- **[Java Development Kit (JDK)](https://www.oracle.com/java/technologies/downloads/#jdk23-windows)**：21 或以上版本
- **[Node.js](https://nodejs.org/zh-tw)**：最新穩定版

#### Python 套件安裝
使用以下指令安裝專案所需套件：
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

#### 其他工具
- **Appium**：
  ```bash
  npm install -g appium
  ```
- **UIAutomator2**：
  ```bash
  appium driver install uiautomator2
  ```

### 2. 環境設定

#### Android Studio 設定
1. 開啟 SDK Manager > 選擇 `Android API 35` 和 `Android SDK Platform Tools`。
2. 使用 AVD 管理器建立模擬裝置 (如 Pixel 4)。

#### 環境變數設定
1. 設定 `ANDROID_HOME` 環境變數（Windows 預設路徑為 `C:\Users\您的用戶名\AppData\Local\Android\Sdk`）。
2. 將以下路徑加入 `Path` 變數：
   ```plaintext
   %ANDROID_HOME%\platform-tools
   %ANDROID_HOME%\tools
   %ANDROID_HOME%\emulator
   ```

### 3. 檔案準備
請準備以下 CSV 檔案：
- **`virable.csv`**：參數設定
- **`taskid.csv`**：任務 ID
- **`Account.csv`**：帳號資訊
- **`schedule.csv`**：排程任務

> **備註**：確保 `schedule.csv` 最後更新，以利判斷排程。

### 4. 操作流程

1. **安裝 HHAEXCHANGE 應用程式**：在 Android Studio 模擬器中安裝。
2. **執行 Schedule_Function.py**：產生排程檔案。
   ```bash
   python Schedule_Function.py
   ```
3. **啟動模擬器與 Appium**：開啟 Android 模擬器並啟動 Appium 伺服器。
4. **執行 main.py**：啟動自動化流程。
   ```bash
   python main.py
   ```

### 5. 資料格式

- **時區**：若時區為空，預設為美東時間（Eastern Time）。
- **任務 ID**：若無指定，預設使用 `"20, 22, 40, 47, 50"`。

### 6. 注意事項
- **排程提醒**：當排程少於 3 項時，系統會提醒新增排程。
- **檔案更新無須重啟**：直接更新 CSV 檔案即可，無須重啟程式。

### 7. 問題排除

- **Appium 無法連接**：確認 Android 模擬器已啟動。
- **環境變數錯誤**：檢查 `ANDROID_HOME` 設定。
- **排程問題**：確認 CSV 檔案格式正確，特別是 `schedule.csv`。
