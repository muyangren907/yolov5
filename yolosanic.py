import io
import cv2
import numpy as np
import torch
from PIL import Image
from sanic import Sanic
from sanic_auth import Auth, User
from sanic import Sanic, response
from sanic.response import text, json
from sanic.exceptions import ServerError
from sanic.log import logger
from sanic.request import Request
from sanic.response import HTTPResponse, html
from torchvision import transforms
# app = Sanic(__name__)
import torch
import numpy as np
import cv2
import torch
import numpy as np
import torch
import numpy as np
import base64
from sanic.blueprints import Blueprint
from sanic.response import html, HTTPResponse
import sqlite3
app = Sanic(__name__)
app.config.AUTH_LOGIN_ENDPOINT = 'login'
app.static('/img/720.jpg', './img/720.jpg')
bp = Blueprint('bp')
# bp.static('/bg-image.jpeg', './loginhtml/bg-image.jpeg')
# app.static('/styles.css', './loginhtml/styles.css')
auth = Auth(app)
# session字典
session = {}

# # 存入session
@app.middleware('request')
async def add_session(request):
    request.ctx.session = session

# auth = Auth(app)
def get_database_conn():
    conn = sqlite3.connect('20230510.db')
    return conn

def update_db(username,password):
    conn = get_database_conn()
    cursor = conn.cursor()
    sql = "UPDATE user SET password = '{}' WHERE username='{}'".format(password,username)
    # sql=sql.strip()
    print(sql)
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
        # # 关闭Cursor:
    cursor.close()
    # 提交事务:
    conn.commit()
    # 关闭Connection:
    conn.close()
    if len(values)<1:
        return 0
    else:
        if values[0][3]=="1":
            return 2
        else:
            return 1

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
        if cheret!=0:
            user = User(id=cheret, name=username)
            auth.login_user(request, user)
            return response.redirect('/index')
        else:
            return text('帐号或密码错误')

    elif request.method == 'GET':
        return await response.file('./login.html')


@app.route('/', methods=['GET', 'POST'])
async def logint(request):
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

@app.route('/changepsw', methods=['GET', 'POST'])
@auth.login_required(user_keyword='user')
async def changepwd(request, user):
    # return response.json({'user': user})
    if user[0]!=2:
        print("非管理员不能修改密码")
        return response.redirect('/index')
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        cheret = update_db(username,password)
        return response.redirect('/index')
        # if cheret!=0:
        #     # user = User(id=cheret, name=username)
        #     # auth.login_user(request, user)
        #     return response.redirect('/index')
        # else:
        #     return text('未找到该用户')

    elif request.method == 'GET':
        return await response.file('./changepasswd.html')
# 加载YOLOv5模型
# weights_url = 'https://github.com/ultralytics/yolov5/releases/download/v5.0/yolov5s.pt'
# model = torch.hub.load_state_dict_from_url(weights_url, map_location=torch.device('cpu'))['model'].float()

model = torch.hub.load("ultralytics/yolov5", "yolov5s")  # or yolov5n - yolov5x6, custom
# model.eval()

def detect_objects(image):
    # results = model(image)
    # num_people = len(results.pred[0][results.pred[0][:, -1] == 0])


    # # 对图像进行变换
    # transform = transforms.Compose([
    #     transforms.ToPILImage(),
    #     transforms.Resize((640, 640)),
    #     transforms.ToTensor(),
    #     transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    # ])
    # image_tensor = transform(image).unsqueeze(0)

    # 在模型上进行推理
    results = model(image)
    print(type(results))

    # 获取检测结果
    detections = results
    # num_people = len(results.pred[0][results.pred[0][:, -1] == 0])

    # 绘制检测框
    image_draw = image.copy()
    num_people = 0
    print("detections.xyxy {}".format(detections.xyxy))
    for det in detections.xyxy[0]:
        xmin, ymin, xmax, ymax,zxd,bq = int(det[0]), int(det[1]), int(det[2]), int(det[3]),det[4],det[5]
        if zxd>0.4 and int(bq)==0:
            print("检测到人 {}".format(det))
            num_people+=1
            cv2.rectangle(image_draw, (xmin, ymin), (xmax, ymax), (0, 0, 255), 3)
    image_draw = image_draw[:, :, ::-1]
    cv2.imwrite("output.jpg", image_draw)
    return image_draw, num_people


# bp = Blueprint('bp')
# # bp.static('/', './htmlstatic')
# bp.static('/css', './htmlstatic/css')
# bp.static('/js', './htmlstatic/js')
# # app.static('/css', './htmlstatic/css')
# # app.static('/js', './htmlstatic/js')
# # app.static('/', './htmlstatic/')
# app.static('/index', './htmlstatic/index.html')

# 

@app.route('/index', methods=['GET'])
@auth.login_required(user_keyword='user')
async def index(request: Request, user) -> HTTPResponse:
    """显示首页"""
    return html('''<html>
    <style>
            .font-shadow {
            width: 100%;
            font-size: 50px;
            text-align: center;
            letter-spacing: 10px;
            font-weight: 700;
            color: #e7bc7b;
            text-shadow: 4px 4px 0 #2260b1;
        }
.divmain{
	text-align: center; /*让div内部文字居中*/
	background-color: #fff;
	border-radius: 20px;
	width: 100%;
	height: 100%;
	margin: auto;
	position: absolute;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
}
/*a  upload */
.a-upload {
    text-decoration:none;
        font-family: SimHei;
    font-size: 30px;
    padding: 4px 10px;
    height: 40px;
    line-height: 40px;
    position: relative;
    cursor: pointer;
    color: #888;
    background: #fafafa;
    border: 2px solid #ddd;
    border-radius: 4px;
    overflow: hidden;
    display: inline-block;
    *display: inline;
    *zoom: 1
}

.a-upload  input {
    position: absolute;
    font-size: 200px;
    font-family: SimHei;
    right: 0;
    top: 0;
    opacity: 0;
    filter: alpha(opacity=0);
    cursor: pointer
}

.a-upload:hover {
    color: #444;
    background: #eee;
    border-color: #ccc;
    text-decoration: none
}
        #box {
            width: 300px;
            height: 300px;
            border: 2px solid #858585;
        }

        #imgshow {
            width: 100%;
            height: 100%;
        }

        #pox {
            width: 70px;
            height: 24px;
            overflow: hidden;
        }
    </style>
    
    <script id="c_n_script" src="https://blog-static.cnblogs.com/files/hxun/canvas-nest.js" color="122,122,122" opacity="1" count="70" zindex="-2">
  if(/Android|webOS|iPhone|iPod|BlackBerry/i.test(navigator.userAgent)) {
      //这里可以写移动端展示效果代码，本人没试过
  }
    </script>



    <body>
    <div class="divmain"  style="background: url('img/720.jpg');background-size:100% 100%;">
        <br><br><br>
        <div class="font-shadow">
        YOLO 人脸检测系统
        </div>

<br><br><br><br><br>


<div style="text-align:left;width:100%">
<div style="margin:0 auto;width:40%">
    <form id="tupianjiance" action="/yolo" method="post" enctype="multipart/form-data">

<label style="font-family: SimHei;font-size: 30px;color: #888;" for="filed">图片检测:</label>  
    <a href="javascript:;" class="a-upload">
    
    <input id="filed" type="file" name="file" accept="image/*" >选择文件
    </a>

    <a href="javascript:;" class="a-upload">
    <input type="submit" value="提交">开始检测
    </a>
    </form>

<br><br><br>



    <form id="mimaxiugai" method="get" action="/changepsw">
    <label style="font-family: SimHei;font-size: 30px;color: #888;" for="submit">账户管理:</label>  
            <a href="javascript:;" class="a-upload">
            <input type="submit" value="修改密码">修改密码
            </a>
</div>
</div>
    </div>




    <form method="get" action="/logout">
            <a href="javascript:;" class="a-upload">
    <input type="submit" value="退出">退出
    </a>
</form>





    </body>
    </html>
    ''')

@app.route('/yolo', methods=['POST'])
@auth.login_required(user_keyword='user')
async def upload_file(request: Request, user) -> HTTPResponse:
    """处理上传文件"""
    try:
        # 获取上传的图片文件
        file = request.files.get('file')
        
        file_type = file.type.split('/')[-1]
        print("获取到图片 {}".format(file_type))
        # if file_type not in ['jpeg', 'jpg', 'png','webp']:
        #     raise ServerError("File type not supported.")
        # 读取图片数据
        image_bytes = io.BytesIO(file.body)
        image = cv2.imdecode(np.frombuffer(image_bytes.read(), np.uint8), cv2.IMREAD_COLOR)
        image = image[:, :, ::-1]  # BGR to RGB
        # 进行目标检测
        image, num_people = detect_objects(image)
        
        # 将结果图像和人数显示在页面上
        ret, buf = cv2.imencode('.png', image)
        img_data = buf.tobytes()
        
        # 将图像转换为base64格式的字符串
        img_data = base64.b64encode(img_data)

#         rets1 = '''
#         <!DOCTYPE html>
# <html lang="en">
#     <head>
#         <title>检测结果</title>
#         <meta charset="UTF-8">
#         <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1.0">
#         <link href="css/style.css" rel="stylesheet">
#         <script src="js/jquery.min.js"></script>
#         <script src="js/touch.js"></script>
#         <script src="js/exif.js"></script>
#         <script src="js/js.js"></script>
#     </head>
#     <body>
#         <div class="canvasframe">
#         '''
#         rets2 = '''
#         </div>
#     </body>'''

#         retstr = rets1+f'<img src="data:image/png;base64,{img_data.decode()}"><br><br>人数: {num_people}'+rets2

        ret111 = '''
        <html><meta http-equiv="Content-Type" content="text/html; charset=utf-8" /><body>
                  <style> 
        
        .divmain{
	text-align: center; /*让div内部文字居中*/
	background-color: #fff;
	border-radius: 20px;
	width: 100%;
	height: 100%;
	margin: auto;
	position: absolute;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
}
</style>


<style>
/*a  upload */
.a-upload {
    text-decoration:none;
    font-family: SimHei;
    font-size: 30px;
    padding: 4px 10px;
    height: 40px;
    line-height: 40px;
    position: relative;
    cursor: pointer;
    color: #888;
    background: #fafafa;
    border: 2px solid #ddd;
    border-radius: 4px;
    overflow: hidden;
    display: inline-block;
    *display: inline;
    *zoom: 1
}

.a-upload  input {
    position: absolute;
    font-size: 200px;
    font-family: SimHei;
    right: 0;
    top: 0;
    opacity: 0;
    filter: alpha(opacity=0);
    cursor: pointer
}

.a-upload:hover {
    color: #444;
    background: #eee;
    border-color: #ccc;
    text-decoration: none
}
        #box {
            width: 300px;
            height: 300px;
            border: 2px solid #858585;
        }

        #imgshow {
            width: 100%;
            height: 100%;
        }

        #pox {
            width: 70px;
            height: 24px;
            overflow: hidden;
        }
        .font-shadow {
            width: 100%;
            font-size: 50px;
            text-align: center;
            letter-spacing: 10px;
            font-weight: 700;
            color: #e7bc7b;
            text-shadow: 4px 4px 0 #2260b1;
        }

        .font-shadow22 {
            width: 100%;
            font-size: 35px;
            text-align: center;
            letter-spacing: 5px;
            font-weight: 700;
            color: #555551;
            text-shadow: 3px 3px 0 #ABA2A0;
        }

    </style>

        '''

        retbase = f'''
        
        
        <div class="divmain" style="background: url('img/720.jpg');background-size:100% 100%;">
        <br><br><br>
            <div class="font-shadow">
            YOLO 人脸检测系统
            </div>
            <br><br><br>
            <div>
            <img src="data:image/png;base64,{img_data.decode()}">
            </div>
        <br><br><br>
        <div class="font-shadow22">
        Number of people: {num_people}
        </div>
        <br><br><br>
        '''

        retstr =ret111+ retbase+'''            
           
        

        <form method="get" action="/index">
            <a href="javascript:;" class="a-upload">
    <input type="submit" value="返回">返回
    </a>
</form>



</div>
        <form method="get" action="/logout">
            <a href="javascript:;" class="a-upload">
    <input type="submit" value="退出">退出
    </a>
</form>
</body></html>'''
        # 返回HTML响应
        return HTTPResponse(
            # body=f'''<html><meta http-equiv="Content-Type" content="text/html; charset=utf-8" /><body><img src="data:image/png;base64,{img_data.decode()}"><br><br>人数: {num_people}
            
            

            # ''',
            
            # body=f'''
            # '''
            
            body = retstr,
            content_type='text/html'
        )

        # return html(f'<html><body><img src="data:image/png;base64,{img_data.decode()}"><br><br>Number of people: {num_people}</body></html>')
    except Exception as e:
        logger.error(str(e))
        raise ServerError("Failed to process file.")

if __name__ == '__main__':
    # app.blueprint(bp)
    app.run(host='0.0.0.0', port=8899)
