# 交通感知综合实训课设备份

此仓库保存桌面 `课设` 文件夹在 2026-11-06 的完整文件快照，包括源代码、数据集、输出、原视频、模型、安装包和旧虚拟环境。`backup-manifest.jsonl` 记录每个原始文件的大小及 SHA-256。额外的 README、恢复脚本和分卷文件用于从 GitHub 还原。

## 取回并校验原始文件

在 Windows 上安装 Git、Git LFS 和 Python 3.11，然后执行：

```powershell
git clone https://github.com/shaoyuancheng05-maker/s-y-s.git
cd s-y-s
git lfs pull
python restore.py
```

`restore.py` 会将所有超过 10 MB 的原始文件从分卷（如 `.part0001`）合并，再对原始文件逐项计算 SHA-256。出现缺失或不一致时会报错；全部通过后才可将克隆目录视为原文件夹的完整副本。

## 运行环境

- 原始项目针对 Windows；随附的 PyTorch 与 torchvision 安装包分别是 `2.0.1+cu118`、`0.15.2+cu118`，适用于 Python 3.11、Windows x64。CUDA 11.8 对应版本的 NVIDIA 驱动是 GPU 运行前提。
- 原始 `yolov5-7-tracker/yolov5-7.0/venv` 记录的是 Python 3.10.11 和已不存在的 `D:\Python`，不能直接作为可移植环境使用。它仍被完整保存，用于文件快照。`environment-snapshot.txt` 列出其中的包元数据供参考。
- 建议新建 Python 3.11 虚拟环境，再安装仓库中的两个 wheel 和 YOLOv5 依赖；原 `requirements.txt` 使用版本下限，不能单独充当精确锁文件。

```powershell
python -m venv .venv-repro
.\.venv-repro\Scripts\python.exe -m pip install --upgrade pip
.\.venv-repro\Scripts\python.exe -m pip install "numpy<2"
.\.venv-repro\Scripts\python.exe -m pip install .\wheels\torch-2.0.1+cu118-cp311-cp311-win_amd64.whl .\wheels\torchvision-0.15.2+cu118-cp311-cp311-win_amd64.whl
.\.venv-repro\Scripts\python.exe -m pip install -r .\yolov5-7-tracker\yolov5-7.0\requirements.txt
```

主要入口：`1_视频分帧.py` 从根目录原视频生成 `frames/`；`2_划分数据集.py` 固定随机种子 42 划分图片；`yolov5-7-tracker/my_tracker.py` 使用本地 `yolov5s.pt` 对原视频检测并跟踪。运行跟踪脚本需要图形桌面，因为它会打开 OpenCV 窗口。请在 Python 3.11 环境中运行，避免直接使用归档的旧虚拟环境。
