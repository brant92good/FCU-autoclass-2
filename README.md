# 逢甲大學自動搶課機器人

## 🎯 介紹

### [ 2024/9/4 - 強化版本! ]
這是基於原版 FCU-AutoClass 的增強版本，具備更完善的功能和穩定性。

### ✨ 新功能
- 🔄 **智能重試機制**: 登入失敗時自動重試，提升成功率
- 📋 **詳細日誌記錄**: 完整記錄所有操作過程，便於追蹤和除錯
- 🪟 **自動彈窗處理**: 自動關閉登入後的調查彈窗
- 🛡️ **錯誤處理優化**: 更優雅的錯誤處理和程序清理
- ⚡ **效能提升**: 優化了元素定位和等待機制


## 🚀 快速開始

### 方法一：使用 Mamba/Conda (推薦)

1. **下載程式**
   ```bash
   git clone https://github.com/HappyGroupHub/FCU-AutoClass.git
   cd FCU-AutoClass
   ```

2. **安裝環境**
   ```bash
   # 使用 mamba (推薦，更快)
   mamba env create -f requirements.yaml
   
   # 或使用 conda
   conda env create -f requirements.yaml
   ```

3. **設定帳號資訊**
   - 打開 `config.yml`
   - 填入你的學號、密碼和目標課程代碼

4. **執行程式**
   ```bash
   # 激活環境
   mamba activate FCUbot  # 或 conda activate FCUbot
   
   # 執行程式
   python app.py
   ```

### 方法二：使用 pip

1. **下載程式並安裝依賴**
   ```bash
   git clone https://github.com/HappyGroupHub/FCU-AutoClass.git
   cd FCU-AutoClass
   pip install selenium==4.11.2 webdriver-manager ddddocr~=1.4.7 pyyaml==6.0 pillow==9.5.0
   ```

2. **設定並執行**（同上方法一的步驟 3-4）

## ⚙️ 設定檔範例 (config.yml)

```yaml
# ++--------------------------------++
# | FCU-AutoClass                    |
# | Made by LD (MIT License)         |
# ++--------------------------------++

# FCU Account
username: ''   # 你的學號
password: ''   # 你的密碼

# Class to join
# 多個課程請用空格分隔
# 例如: class_id: '1234 5678'
class_id: ''

# Headless mode
# true: 背景執行 (看不到瀏覽器視窗)
# false: 顯示瀏覽器視窗 (除錯時建議使用)
headless: false
```

### 設定參數說明

| 參數 | 說明 | 範例 |
|------|------|------|
| `username` | 逢甲大學學號 | `'D1285001'` |
| `password` | 選課系統密碼 | `'your_password'` |
| `class_id` | 目標課程代碼，多個用空格分隔 | `'3227 3218 3082'` |
| `headless` | 是否在背景執行 | `true` 或 `false` |

## 📊 日誌功能

程式會自動在 `logs/` 資料夾中生成詳細的執行日誌，包含：

- 📝 **程式啟動和設定載入**
- 🔐 **登入過程詳細記錄**
- 🤖 **OCR 驗證碼辨識結果**
- 🎯 **每個課程的查詢和加選狀態**
- ❌ **錯誤和警告訊息**
- 🔄 **重試和恢復過程**

範例日誌：
```
2025-09-04 17:40:44,172 - INFO - === FCU AutoClass 程式啟動 ===
2025-09-04 17:40:44,172 - INFO - 設定檔讀取完成 - 使用者: D1285001, 課程數量: 8
2025-09-04 17:40:46,433 - INFO - OCR 辨識驗證碼: 9368
2025-09-04 17:40:48,132 - INFO - 登入成功！開始自動加課...
2025-09-04 17:40:48,918 - INFO - 課程 3227: 剩餘名額/開放名額：0  /75 
```

## 🔧 進階功能

### 自動彈窗處理
程式會自動檢測並關閉登入後出現的調查彈窗，無需手動干預。

### 智能重試機制
- 登入失敗時自動重試（最多3次）
- 發生錯誤時自動重啟瀏覽器
- 網頁元素失效時自動恢復

### 優雅的程序管理
- 支援 Ctrl+C 快速退出
- 自動清理瀏覽器進程
- 防止殘留進程占用資源


### 除錯模式

如遇問題，建議：
1. 將 `headless` 設為 `false` 以觀察瀏覽器行為
2. 查看 `logs/` 資料夾中的最新日誌檔案
3. 在 Issues 中回報問題時請附上日誌檔案

## 📋 系統需求

- **作業系統**: Windows 10/11, macOS, Linux
- **Python**: 3.10 或以上版本
- **瀏覽器**: Google Chrome (最新版本)
- **網路**: 穩定的網路連線

## 🤝 貢獻

歡迎提交 Pull Request 或在 Issues 中回報問題！

回報問題時請盡可能提供：
- 詳細的錯誤描述
- 系統環境資訊
- 相關的日誌檔案 (`logs/` 資料夾中的最新檔案)

## � 致謝與來源

此專案基於 [HappyGroupHub/FCU-AutoClass](https://github.com/HappyGroupHub/FCU-AutoClass.git) 進行增強和改進。

感謝原作者提供的優秀基礎框架，讓這個專案得以在原有功能上進一步發展。

### 主要改進項目
- 增加詳細的日誌記錄系統
- 改善錯誤處理和重試機制
- 添加自動彈窗處理功能
- 優化程序清理和資源管理

## �📄 版權聲明

此專案採用 **MIT License** - 詳見 [LICENSE](LICENSE) 檔案

---

> ⚠️ **免責聲明**: 此工具僅供學習和研究用途，使用者需自行承擔使用風險。請遵守學校相關規定。

> 💡 **提醒**: 建議在選課高峰期適度使用，避免對學校伺服器造成過大負擔。