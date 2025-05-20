import sqlite3
from flask import Flask, render_template, request,redirect

app = Flask(__name__)

DB_NAME = 'D:/Web程式設計/member_login_register_system/membership.db'

def check_db()->None:
    """檢查資料表是否存在，若不存在則新增資料表。"""
    try:
        print(create_db(DB_NAME))
    except sqlite3.IntegrityError :
        print("")
        print("資料表初始化成功")
        print("")

def create_db(db_name: str)-> str:

    """建立一個新的資料表"""

    with sqlite3.connect(db_name) as conn:
        conn.row_factory = sqlite3.Row  # 使查詢結果可以用欄位名稱存取
        cursor = conn.cursor()

        # 建立資料表
        cursor.executescript('''
        CREATE TABLE IF NOT EXISTS members (
            iid INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            phone TEXT,
            birthdate TEXT
        );
    ''')
        # 插入會員資料
        cursor.execute(
            "INSERT OR IGNORE INTO members (username, email, password, phone, birthdate) VALUES (?, ?, ?, ?, ?)",
            ('admin', 'admin@example.com', 'admin123', '0912345678', '1990-01-01')
        )
        conn.commit()
    return f'資料表初始化成功'

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/login',methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        if not email or not password:
            return render_template('error.html', message="請輸入電子郵件和密碼")

        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM members WHERE email = ? AND password = ?", (email, password))
            user = cursor.fetchone()
            if not user:
                return render_template('error.html', message="電子郵件或密碼錯誤")
            else:
                username = user[1]
                iid = user[0]
                return redirect(f'/welcome/{iid}')

    return render_template('login.html')

@app.route('/register',methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        phone = request.form.get('phone', '').strip()
        birthdate = request.form.get('birthdate', '').strip()

        # 檢查是否有空值
        if not username or not email or not password:
            return render_template('error.html', message="請輸入用戶名、電子郵件和密碼")

        # 檢查用戶名是否已存在
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM members WHERE username = ?", (username,))
            existing_user = cursor.fetchone()
            if existing_user:
                return render_template('error.html', message="用戶名已存在")

            # 新增會員資料
            cursor.execute("""
                INSERT INTO members (username, email, password, phone, birthdate)
                VALUES (?, ?, ?, ?, ?)
            """, (username, email, password, phone, birthdate))
            conn.commit()

        return redirect('/login')

    return render_template('register.html')


@app.route('/error')
def error():
    message = request.args.get('message', '發生錯誤')
    return render_template('error.html', message=message)


@app.route('/welcome/<int:iid>')
def welcome(iid):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM members WHERE iid = ?", (iid,))
        result = cursor.fetchone()

    if result:
        username = result[0]
        return render_template('welcome.html',iid=iid,username = username)
    else:
        return render_template('error.html', message="找不到使用者")

@app.route('/delete/<int:iid>')
def delete_user(iid):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        # 刪除該會員
        cursor.execute("DELETE FROM members WHERE iid = ?", (iid,))
        conn.commit()
    return redirect('/')

@app.route('/edit_profile/<int:iid>', methods=['GET', 'POST'])
def edit_profile(iid):
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        phone = request.form.get('phone', '').strip()
        birthdate = request.form.get('birthdate', '').strip()

        # 檢查空值
        if not email or not password:
            return render_template('error.html', message="請輸入電子郵件和密碼")

        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()

            # 檢查 email 是否被其他用戶使用
            cursor.execute("SELECT * FROM members WHERE email = ? AND iid != ?", (email, iid))
            email_in_use = cursor.fetchone()
            if email_in_use:
                return render_template('error.html', message="電子郵件已被使用")

            # 更新使用者資料
            cursor.execute('''
                UPDATE members
                SET email = ?, password = ?, phone = ?, birthdate = ?
                WHERE iid = ?
            ''', (email, password, phone, birthdate, iid))
            conn.commit()

        # 查出使用者名稱以便顯示歡迎頁
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT username FROM members WHERE iid = ?", (iid,))
            username = cursor.fetchone()[0]

        return render_template('welcome.html', username=f"★{username}★", iid=iid)

    # GET 方法，查詢使用者資料顯示表單
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM members WHERE iid = ?", (iid,))
        user = cursor.fetchone()

    return render_template('edit_profile.html', user=user)

@app.template_filter('add_stars')
def add_stars(s):
    return f'★{s}★'

def main():
    check_db()

if __name__ == "__main__":
    main()