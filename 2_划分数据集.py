# -*- coding: utf-8 -*-
# 交通感知综合实训 - 数据集划分脚本
# 将 frames 中的图片按 8:2 随机划分为训练集和测试集
# 固定随机种子 42, 保证结果可复现
import os
import shutil
import random
from pathlib import Path

# ===== 路径配置（按实际情况修改）=====
project_root = Path(__file__).resolve().parent
src_dir = str(project_root / 'frames')
root = str(project_root / 'dataset')
train_dir = os.path.join(root, 'train')
test_dir = os.path.join(root, 'test')

os.makedirs(train_dir, exist_ok=True)
os.makedirs(test_dir, exist_ok=True)

images = sorted(f for f in os.listdir(src_dir) if f.lower().endswith('.jpg'))
print(f'原始图片总数: {len(images)}')

# 固定随机种子，保证每次划分结果一致
random.seed(42)
random.shuffle(images)

n_train = round(len(images) * 0.8)
train_list = images[:n_train]
test_list = images[n_train:]

# 复制图片到对应目录
for f in train_list:
    shutil.copy(os.path.join(src_dir, f), os.path.join(train_dir, f))
for f in test_list:
    shutil.copy(os.path.join(src_dir, f), os.path.join(test_dir, f))

# 保存划分清单，便于核对
with open(os.path.join(root, 'train_list.txt'), 'w', encoding='utf-8') as fp:
    fp.write('\n'.join(train_list))
with open(os.path.join(root, 'test_list.txt'), 'w', encoding='utf-8') as fp:
    fp.write('\n'.join(test_list))

print(f'训练集: {len(train_list)} 张 -> {train_dir}')
print(f'测试集: {len(test_list)} 张 -> {test_dir}')
print(f'划分比例: {len(train_list)/len(images)*100:.1f}% : {len(test_list)/len(images)*100:.1f}%')
