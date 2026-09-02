#!/usr/bin/env python3
"""
Index-TTS-2 模型自动下载脚本
支持断点续传，从 HuggingFace 官方源下载
"""
import os
import sys

# 模型保存路径
# LOCAL_DIR = r"D:\Program Files\AI\ComfyUI\models\IndexTTS-2.5"
LOCAL_DIR = r"D:\Program Files\AI\index-tts\checkpoints"
REPO_ID = "IndexTeam/IndexTTS-2.5"

def main():
    try:
        from huggingface_hub import snapshot_download
    except ImportError:
        print("错误: huggingface_hub 未安装")
        print("请先执行: pip install huggingface_hub")
        sys.exit(1)

    print(f"开始下载: {REPO_ID}")
    print(f"保存位置: {LOCAL_DIR}")
    print("模型大小约 5GB，请耐心等待...")
    print("-" * 50)

    os.makedirs(LOCAL_DIR, exist_ok=True)

    snapshot_download(
        repo_id=REPO_ID,
        local_dir=LOCAL_DIR,
        resume_download=True,
    )

    print("-" * 50)
    print("✅ IndexTTS-2.5 模型下载完成!")
    print(f"保存位置: {LOCAL_DIR}")

if __name__ == "__main__":
    main()
