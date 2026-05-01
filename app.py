import json
import os
from flask import Flask, session, render_template, request, redirect, url_for

app = Flask(__name__)
JSON_FILE = "users.json"
app.secret_key = 'admin'

def init_json_file(file_path: str) -> None:
    if not os.path.exists(file_path):
        save_users(file_path, _default_data())

def _default_data() -> dict:
    return {
        "users": [{
            "username": "admin",
            "email": "admin@example.com",
            "password": "admin123",
            "phone": "0912345678",
            "birthdate": "1990-01-01"
        }]
    }

def read_users(file_path: str) -> dict:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return _default_data()

def save_users(file_path: str, data: dict) -> bool:
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

def validate_register(form_data: dict, users: list) -> dict:
    username = form_data.get("username", "").strip()
    email = form_data.get("email", "").strip()
    password = form_data.get("password", "").strip()
    phone = form_data.get("phone", "").strip()
    birthdate = form_data.get("birthdate", "").strip()

    if not username or not email or not password or not birthdate:
        return {"success": False, "error": "帳號、Email、密碼與出生日期為必填欄位"}

    if "@" not in email or "." not in email.split("@")[-1]:
        return {"success": False, "error": "Email 格式錯誤"}

    if not (6 <= len(password) <= 16):
        return {"success": False, "error": "密碼長度需為 6~16 字元"}

    if phone and (not phone.isdigit() or len(phone) != 10 or not phone.startswith("09")):
        return {"success": False, "error": "電話需為 10 碼數字且以 09 開頭"}

    for u in users:
        if u["username"] == username:
            return {"success": False, "error": "該帳號已被註冊"}
        if u["email"] == email:
            return {"success": False, "error": "該 Email 已被註冊"}

    return {"success": True, "data": {
        "username": username, "email": email, "password": password,
        "phone": phone, "birthdate": birthdate
    }}

def verify_login(email: str, password: str, users: list) -> dict:
    if not email or not password:
        return {"success": False, "error": "請輸入 Email 與密碼"}

    for user in users:
        if user["email"] == email and user["password"] == password:
            return {"success": True, "data": user}

    return {"success": False, "error": "Email 或密碼錯誤"}

@app.template_filter('mask_phone')
def mask_phone(phone: str) -> str:
    if not phone or len(phone) != 10 or not phone.startswith("09"):
        return phone or "未填寫"
    return phone[:4] + "****" + phone[-2:]

@app.template_filter('format_tw_date')
def format_tw_date(date_str: str) -> str:
    try:
        y, m, d = date_str.split("-")
        return f"民國{int(y) - 1911}年{m}月{d}日"
    except:
        return date_str

@app.route('/')
def index():
    return render_template('index.html', title='進階會員系統')

@app.route('/register', methods=['GET', 'POST'])
def register_route():
    if request.method == 'POST':
        form_data = {}
        for field in ["username", "email", "password", "phone", "birthdate"]:
            form_data[field] = request.form.get(field, "").strip()

        data = read_users(JSON_FILE)
        result = validate_register(form_data, data["users"])

        if not result["success"]:
            return redirect(url_for('error_route', message=result["error"]))

        data["users"].append(result["data"])
        if not save_users(JSON_FILE, data):
            return redirect(url_for('error_route', message='寫入失敗'))
        return redirect(url_for('login_route'))

    return render_template('register.html', title='會員註冊')

@app.route('/login', methods=['GET', 'POST'])
def login_route():
    if request.method == 'POST': 
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        result = verify_login(email, password, read_users(JSON_FILE)["users"])
        if result["success"]:
            session['username'] = result["data"]["username"]
            session['is_admin'] = (result["data"]["username"] == 'admin')
            return redirect(url_for('announcement'))
        return redirect(url_for('error_route', message=result["error"]))

    return render_template('login.html', title='會員登入')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/announcement')
def announcement():
    if 'username' not in session:
        return redirect(url_for('login_route'))
    return render_template('announcement.html', title='系統公告', username=session['username'])

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'username' not in session:
        return redirect(url_for('login_route'))
    data = read_users(JSON_FILE)
    user_info = next((u for u in data["users"] if u["username"] == session['username']), None)
    if not user_info:
        return redirect(url_for('error_route', message='使用者資料不存在'))
    if request.method == 'POST':
        new_email = request.form.get("email", "").strip()
        new_phone = request.form.get("phone", "").strip()
        new_birthdate = request.form.get("birthdate", "").strip()
        new_password = request.form.get("password", "").strip()

        for u in data["users"]:
            if "@" not in new_email or "." not in new_email.split("@")[-1]:
                return redirect(url_for('error_route', message="Email 格式錯誤"))
            if u['email'] == new_email and u['username'] != session['username']:
                return redirect(url_for('error_route', message='Email 已被其他會員使用'))
        if new_phone and (not new_phone.isdigit() or len(new_phone) != 10 or not new_phone.startswith("09")):
            return redirect(url_for('error_route', message="電話需為 10 碼數字且以 09 開頭"))
        if new_password and not (6 <= len(new_password) <= 16):
            return redirect(url_for('error_route', message="密碼長度需為 6~16 字元"))
        
        user_info['email'] = new_email
        user_info['password'] = new_password
        user_info['phone'] = new_phone
        user_info['birthdate'] = new_birthdate
        save_users(JSON_FILE, data)
        return redirect(url_for('announcement'))

    return render_template('profile.html', title='個人資料', user=user_info)

@app.route('/users')
def users_list_route():
    if 'username' not in session:
        return redirect(url_for('login_route'))
    if not session.get('is_admin'):
        return redirect(url_for('error_route', message='無權限訪問'))
    
    return render_template('users.html', title='會員管理', users=read_users(JSON_FILE)["users"])

@app.route('/users/<username>/edit', methods=['GET', 'POST'])
def edit_user_route(username):
    if 'username' not in session:
        return redirect(url_for('login_route'))
    if not session.get('is_admin'):
        return redirect(url_for('error_route', message='無權限訪問'))
    data = read_users(JSON_FILE)
    user_info = next((u for u in data["users"] if u["username"] == username), None)
    if not user_info:
        return redirect(url_for('error_route', message='使用者資料不存在'))
    if request.method == 'POST':
        new_phone = request.form.get("phone", "").strip()
        new_birthdate = request.form.get("birthdate", "").strip()
        new_password = request.form.get("password", "").strip()

        if new_phone and (not new_phone.isdigit() or len(new_phone) != 10 or not new_phone.startswith("09")):
            return redirect(url_for('error_route', message="電話需為 10 碼數字且以 09 開頭"))
        if new_password and not (6 <= len(new_password) <= 16):
            return redirect(url_for('error_route', message="密碼長度需為 6~16 字元"))
        
        user_info['phone'] = new_phone
        user_info['birthdate'] = new_birthdate
        user_info['password'] = new_password

        save_users(JSON_FILE, data)
        return redirect(url_for('users_list_route'))

    return render_template('edit_user.html', title='編輯會員資料', user=user_info)

@app.route('/users/<username>/delete', methods=['POST'])
def delete_user_route(username):
    if 'username' not in session:
        return redirect(url_for('login_route'))
    if not session.get('is_admin'):
        return redirect(url_for('error_route', message='無權限訪問'))
    data = read_users(JSON_FILE)
    user_info = next((u for u in data["users"] if u["username"] == username), None)
    if not user_info:
        return redirect(url_for('error_route', message='使用者資料不存在'))
    data["users"].remove(user_info)
    save_users(JSON_FILE, data)
    return redirect(url_for('users_list_route'))

@app.route('/error')
def error_route():
    message = request.args.get('message', '發生未知錯誤')
    return render_template('error.html', title='系統錯誤', message=message)

init_json_file(JSON_FILE)