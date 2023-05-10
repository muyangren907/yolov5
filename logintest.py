from sanic_auth import Auth, User
from sanic import Sanic, response
from sanic.response import text, json
import pymysql
import sqlite3
app = Sanic(__name__)
app.config.AUTH_LOGIN_ENDPOINT = 'login'

auth = Auth(app)
# session字典
session = {}

# # 存入session
@app.middleware('request')
async def add_session(request):
    request.ctx.session = session

auth = Auth(app)
def get_database_conn():
    conn = sqlite3.connect('20230510.db')
    return conn


def update_db(author_id, author_nickname, video_id, video_title, video_url):
    conn = get_database_conn()
    cursor = conn.cursor()
    sql = 'INSERT OR IGNORE INTO "main"."KwaiVideos"("author_id", "author_nickname", "video_id", "video_title", "video_url") VALUES ("{}", "{}", "{}", "{}", "{}")'.format(
        author_id, author_nickname, video_id, video_title, video_url)

    cursor.execute(sql)
    # # 关闭Cursor:
    cursor.close()
    # 提交事务:
    conn.commit()
    # 关闭Connection:
    conn.close()


def check_user_db(username,password):
    conn = get_database_conn()
    cursor = conn.cursor()
    # type_, nickname_ = get_type_and_nickname()
    sql = "SELECT * FROM user WHERE username='{}' and password='{}'".format(username,password)
    print(sql)
    cursor.execute(sql)
    values = cursor.fetchall()
    if len(values)<1:
        return False
    else:
        return True
    vks = [vk[2] for vk in values]
    # # 关闭Cursor:
    cursor.close()
    # 提交事务:
    conn.commit()
    # 关闭Connection:
    conn.close()
    return vks

# db = pymysql.connect(host='localhost',
#                      user='username',
#                      passwd='password',
#                      database='database_name',
#                      charset="utf8")


# 定义登录函数
@app.route('/login', methods=['GET', 'POST'])
async def login(request):
    message = ''
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        cheret = check_user_db(username,password)
        if cheret:
            user = User(id=username, name=username)
            auth.login_user(request, user)
            return response.redirect('/profile')
        else:
            return text('帐号或密码错误')

    elif request.method == 'GET':
        return await response.file('./login.html')

# 调用内置的登出函数，清除session
@app.route('/logout')
@auth.login_required
async def logout(request):
    auth.logout_user(request)
    return response.redirect('/login')


@app.route('/profile')
@auth.login_required(user_keyword='user')
async def profile(request, user):
    return response.json({'user': user})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
