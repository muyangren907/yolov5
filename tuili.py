import torch

# Model
model = torch.hub.load("ultralytics/yolov5", "yolov5s")  # or yolov5n - yolov5x6, custom

# Images
# img = "https://ultralytics.com/images/zidane.jpg"  # or file, Path, PIL, OpenCV, numpy, list

# # Images
# img = "duoren.jpg"  # or file, Path, PIL, OpenCV, numpy, list

# Images
img = "dr2.jpg"  # or file, Path, PIL, OpenCV, numpy, list

# Inference
results = model(img)
print('结果{}类型{}'.format(results,type(results)))
num_people = len(results.pred[0][results.pred[0][:, -1] == 0])
print('人数统计 {}'.format(num_people))

# Results
results.print()  # or .show(), .save(), .crop(), .pandas(), etc.
results.save()