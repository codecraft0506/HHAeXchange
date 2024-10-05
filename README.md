# 自動打卡專案說明書

---

#### 目錄
1. **系統需求**
2. **專案安裝步驟**
3. **環境變數配置**
4. **Android Studio 與模擬器設置**
5. **打卡應用安裝與執行**
6. **Alpha.py 配置**
7. **問題排查**

---

### 1. 系統需求

在開始安裝和配置專案之前，請確保您的系統符合以下需求：

- **操作系統**：Windows 10 或更高版本
- **軟體需求**：
  - **[Android Studio](https://developer.android.com/studio?hl=zh-tw)**
  - **[Java JDK](https://www.oracle.com/java/technologies/downloads/#jdk23-windows)**
  - **[Python 3.x](https://www.python.org/)**
  - **Git**
- **硬體需求**：
  - 至少 8GB RAM
  - 10GB 可用磁碟空間

---

### 2. 專案安裝步驟

#### 2.1 克隆 GitHub 專案

在命令提示字元或終端中執行以下命令來克隆您的專案：

```bash
git clone https://github.com/codecraft0506/HHAeXchange.git
```

進入專案目錄：

```bash
cd HHAeXchange
```

#### 2.2 安裝 Python 依賴

專案根目錄應該包含 `requirements.txt` 文件。執行以下命令來安裝所需的依賴：

```bash
pip install -r requirements.txt
```

---

### 3. 環境變數配置

為了讓 Android Studio 和其他工具運行正常，請配置以下環境變數。

#### 3.1 Android SDK 路徑

將以下路徑加入系統環境變數 `Path`：

- `C:\Users\{使用者名稱}\AppData\Local\Android\Sdk\platform-tools`
- `C:\Users\{使用者名稱}\AppData\Local\Android\Sdk\emulator`

#### 3.2 Java 路徑

Java 通常會自動配置環境變數。如果需要手動設置，請確保以下路徑在 `Path` 中：

- `C:\Program Files\Common Files\Oracle\Java\javapath`

---

### 4. Android Studio 與模擬器設置

#### 4.1 安裝 Android Studio SDK

1. 打開 **Android Studio**，前往 `SDK Manager`。
2. 下載以下內容：
   - **SDK Platforms**：Android API 35
   - **SDK Tools**：
     - Android Emulator
     - Android Platform-tools

#### 4.2 創建 Android 模擬器

1. 打開 **AVD Manager**，點擊 `Create Virtual Device`。
2. 設定以下內容：
   - **設備型號**：Pixel 4
   - **API 版本**：API 35
   - **系統映像**：Google APIs (Play Store 支援)
   - **頁面大小**：16KB

3. 完成後，啟動模擬器。

---

### 5. 打卡應用安裝與執行

1. 啟動 Android 模擬器，並登入 **Google Play** 帳戶。
2. 如有需要，可以通過 VPN 設置模擬器的網絡來下載打卡應用（如 HHAeXchange）。
3. 安裝完成後，確認應用可以正常運行。

---

### 6. Alpha.py 配置

#### 6.1 OpenCageGeocode 金鑰申請

1. 前往 [OpenCage Geocoder](https://opencagedata.com/) 註冊帳號並獲取 API 金鑰。
2. 將獲得的 API 金鑰添加到 `Alpha.py` 中。

修改 `Alpha.py` 代碼如下：

```python
from opencage.geocoder import OpenCageGeocode

# 替換為你的 OpenCageGeocode API 金鑰
API_KEY = '你的 API 金鑰'
geocoder = OpenCageGeocode(API_KEY)

# 其他腳本操作...
```

#### 6.2 執行 Alpha.py

確保 Android 模擬器已啟動並且打卡應用已安裝，然後執行 `Alpha.py`：

```bash
python Alpha.py
```

---

### 7. 問題排查

#### 7.1 Google Play 無法下載應用
- 嘗試使用 VPN 切換至其他地區進行下載。

#### 7.2 GPS 定位不準
- 確保模擬器設置了虛擬 GPS 定位。
- 檢查模擬器 API 是否支援 Google Play Services。

#### 7.3 Python 依賴問題
- 如果安裝依賴時出現錯誤，請確認 `requirements.txt` 中的版本是否與當前系統相容，並手動安裝相應版本的依賴。

---
