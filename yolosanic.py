import io
import cv2
import numpy as np
import torch
from PIL import Image
from sanic import Sanic
from sanic.exceptions import ServerError
from sanic.log import logger
from sanic.request import Request
from sanic.response import HTTPResponse, html
from torchvision import transforms
app = Sanic(__name__)
import torch
import numpy as np
import cv2
import torch
import numpy as np
import torch
import numpy as np
import base64
from sanic.response import html, HTTPResponse
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

@app.route('/', methods=['GET'])
async def index(request: Request) -> HTTPResponse:
    """显示首页"""
    return html('<html><body><form action="/" method="post" enctype="multipart/form-data"><input type="file" name="file"><br><br><input type="submit" value="Upload"></form></body></html>')

@app.route('/', methods=['POST'])
async def upload_file(request: Request) -> HTTPResponse:
    """处理上传文件"""
    try:
        # 获取上传的图片文件
        file = request.files.get('file')
        file_type = file.type.split('/')[-1]
        if file_type not in ['jpeg', 'jpg', 'png']:
            raise ServerError("File type not supported.")
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

        # 返回HTML响应
        return HTTPResponse(
            body=f'<html><body><img src="data:image/png;base64,{img_data.decode()}"><br><br>Number of people: {num_people}</body></html>',
            content_type='text/html'
        )

        # return html(f'<html><body><img src="data:image/png;base64,{img_data.decode()}"><br><br>Number of people: {num_people}</body></html>')
    except Exception as e:
        logger.error(str(e))
        raise ServerError("Failed to process file.")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
