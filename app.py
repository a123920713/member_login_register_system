import sqlite3
from flask import Flask, render_template, request

app = Flask(__name__) # __name__ 代表目前執行的模組

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
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/welcome')
def register():
    return render_template('welcome.html')

def main():
    check_db()

if __name__ == "__main__":
    main()