import cv2
import torch
from tracker import *
from pathlib import Path

# print(cv2.__version__)
import numpy as np

# read image
# img2 = cv2.imread('767.jpg')[..., ::-1]  # OpenCV image (BGR to RGB)
# img3 = cv2.imread('767.jpg')
# img2 = cv2.resize(img2, (640, 480))
# read video
ROOT = Path(__file__).resolve().parent
YOLO_ROOT = ROOT / 'yolov5-7.0'
videoCapture = cv2.VideoCapture(str(ROOT.parent / 'VID_20251028_083623.mp4'))

count=0
tracker = Tracker()

def POINTS(event, x, y, flags, param):
    if event == cv2.EVENT_MOUSEMOVE:
        colorsBGR = [x, y]
        print(colorsBGR)

cv2.namedWindow('FRAME')
cv2.setMouseCallback('FRAME', POINTS)

area1 = [(311, 174),(344, 173),(343, 135),(306, 123)]
area_1 = set()

# write video
fourcc = cv2.VideoWriter_fourcc(*'XVID')
fps = videoCapture.get(cv2.CAP_PROP_FPS)
size = (int(videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH)), int(videoCapture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
output_dir = ROOT / 'output'
output_dir.mkdir(exist_ok=True)
out = cv2.VideoWriter(str(output_dir / 'outVideo_2.mp4'), fourcc, fps, size)

# model
model = torch.hub.load(str(YOLO_ROOT), 'custom', path=str(YOLO_ROOT / 'yolov5s.pt'), source='local')

success, frame = videoCapture.read()
while success:
    results = model(frame[..., ::-1])
    points = results.pandas().xyxy[0]
    # print(points)
    list = []
    for index, row in points.iterrows():
        # cv2.rectangle(frame, (int(row['xmin']), int(row['ymax'])), (int(row['xmax']), int(row['ymin'])), (0, 255, 0), 2)
        x = int(row[0])
        y = int(row[1])
        x1 = int(row[2])
        y1 = int(row[3])
        b = str(row['name'])
        # cv2.rectangle(frame, (x, y), (x1, y1), (0, 0, 255), 2)
        list.append([x, y, x1, y1])
    idx_bbox = tracker.update(list)
    for bbox in idx_bbox:
        x2, y2, x3, y3, id = bbox
        # print(id)
        # 在帧上绘制矩形框
        cv2.rectangle(frame, (x2, y2), (x3, y3), (0, 0, 255), 1)
        # 在帧上绘制文本标签
        cv2.putText(frame, str(id), (x2, y2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
        # 在帧上绘制圆形
        cv2.circle(frame, (x3, y3), 3, (0, 255, 0), -1)
        result = cv2.pointPolygonTest(np.array(area1, np.int32), (x3, y3), False)
        if result > 0:
            area_1.add(id)

    cv2.polylines(frame, [np.array(area1, np.int32)], True, (0, 255, 255), 3)
    a1 = len(area_1)
    print(a1)
    cv2.putText(frame, "The number of cars:"+str(a1), (20, 20), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 255), 3)

    out.write(frame)  # 写入视频对象
    cv2.imshow('FRAME', frame)
    cv2.moveWindow('FRAME', 0, 0)

    success, frame = videoCapture.read()  # 获取下一帧

    if cv2.waitKey(1) == ord('q'):
        break

videoCapture.release()
out.release()
cv2.destroyAllWindows()

print("Finishied!")
