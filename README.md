# 114-2 期中考
### Web 程式設計 <br><br><br>
# 進階會員系統

## 檔案結構說明 
* `app.py` : Flask 主程式，包含所有路由邏輯、註冊驗證及民國日期轉換功能。
* `users.json` : 本地資料儲存檔，記錄使用者帳號與個人資料。
* `templates/` : 包含所有的 HTML 網頁模板（登入、註冊、公告、個人資料, 等等）。
* `static/css/` : 網頁的樣子模板。
* `requirements.txt` : 專案所需的 Python 套件清單（由 pip freeze 產生）。

##  額外管理文件說明
* `.gitignore` : 設定排除上傳的檔案，避免將暫存檔或虛擬環境上傳到 GitHub。
* `README.md` : 專案的使用說明書與功能簡介。
* `LICENSE` : 採用 MIT 授權協議，開放且自由的程式碼授權。

## 如何執行本專案
1. 複製專案：使用 Git 將專案下載到你的電腦 <br>
`git clone https://github.com/seasalatte/1142midexam.git`
2. 安裝必要套件 ：使用專案提供的 requirements.txt 安裝 Flask <br>
`python -m pip install -r requirements.txt`
3. 啟動程式 ：執行主程式來啟動 Flask 伺服器 <br>
`flask --debug run`
4. 瀏覽網頁 ：在瀏覽器輸入網址 <br>
`http://127.0.0.1:5000`
