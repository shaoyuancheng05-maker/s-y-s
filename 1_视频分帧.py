# -*- coding: utf-8 -*-
# 交通感知综合实训 - 视频分帧脚本
# 默认读取课设目录中的路口实拍视频
# 分帧规则: 每隔7帧抽取1帧
import cv2
import os
from pathlib import Path

# ===== 路径配置（按实际情况修改）=====
project_root = Path(__file__).resolve().parent
video_path = str(project_root / 'VID_20251028_083623.mp4')
out_dir = str(project_root / 'frames')
interval = 7                       # 每7帧取1帧

os.makedirs(out_dir, exist_ok=True)

cap = cv2.VideoCapture(video_path)
total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
frame_idx = 0
saved = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break
    if frame_idx % interval == 0:
        saved += 1
        cv2.imwrite(os.path.join(out_dir, f'{saved:04d}.jpg'), frame)
    frame_idx += 1

cap.release()
print(f'视频总帧数: {total}')
print(f'实际读取帧数: {frame_idx}')
print(f'分帧间隔: 每{interval}帧取1帧')
print(f'共保存图片: {saved} 张')
print(f'输出目录: {out_dir}')
