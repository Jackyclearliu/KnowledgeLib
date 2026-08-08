#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一键下载入口（交互式配置）
==========================
双击 "下载视频.bat" 即运行本脚本。
运行时逐项提示配置，直接回车使用默认值（默认值见下方配置区）。

支持格式:
    - M3U8 流媒体（.m3u8）     → 多线程分片下载 + 合并
    - 直链视频文件（mp4/flv/mkv 等）→ 单连接下载，支持断点续传

作者: Lily
"""

import sys
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

from m3u8_downloader import M3U8Downloader
from direct_downloader import DirectDownloader, VIDEO_SUFFIXES
from stream_finder import find_stream_urls

# ==================== 默认配置区（直接回车即应用） ====================
DEFAULT_PAGE_URL = "https://www.yhdm28.com/index.php/vod/play/id/31458/sid/3/nid/1.html"
DEFAULT_STREAM_URL = ""              # 留空 = 自动从页面提取
DEFAULT_OUTPUT_NAME = "anime_video"  # 扩展名按流格式自动添加
DEFAULT_THREADS = 16                 # M3U8 并发下载线程数
# ======================================================================


def _ask(prompt, default, hint=None):
    """交互式询问一项配置；输入为空（或 stdin 关闭）时使用默认值"""
    if hint is None:
        hint = "默认: %s" % default if default else "自动从页面提取"
    try:
        text = input("%s [直接回车=%s]\n> " % (prompt, hint))
    except EOFError:
        text = ""
    text = text.strip()
    if not text:
        print("  → 使用默认值: %s" % (default if default else "(自动提取)"))
        return default
    return text


def _ask_int(prompt, default):
    """询问正整数配置，非法输入回退默认值"""
    raw = _ask(prompt, str(default))
    try:
        value = int(raw)
        if value <= 0:
            raise ValueError
        return value
    except ValueError:
        print("  → 输入无效，使用默认值 %d" % default)
        return default


def _make_referer(page_url):
    """从页面地址推导防盗链 Referer（源站根地址）"""
    parsed = urlparse(page_url)
    if parsed.scheme and parsed.netloc:
        return "%s://%s/" % (parsed.scheme, parsed.netloc)
    return "https://www.yhdm28.com/"


def _pick_stream(page_url, referer):
    """自动从页面提取视频流地址；多个候选时让用户选择"""
    print("\n正在从页面提取视频流地址...")
    print("  页面: " + page_url)
    try:
        candidates = find_stream_urls(page_url, referer=referer)
    except Exception as e:
        print("[ERROR] 页面抓取失败: %s" % e)
        return None

    if not candidates:
        print("[ERROR] 未能从页面中提取到视频流地址。")
        print("        该页面可能通过接口动态加载视频流，")
        print("        请用浏览器开发者工具（F12 → 网络）找到地址后手动填写。")
        return None

    if len(candidates) == 1:
        print("已提取到视频流地址:\n  " + candidates[0])
        return candidates[0]

    print("共找到 %d 个候选视频流地址:" % len(candidates))
    for i, url in enumerate(candidates, 1):
        print("  [%d] %s" % (i, url))
    choice = _ask("请选择要下载的编号", "1")
    try:
        idx = int(choice)
        if not 1 <= idx <= len(candidates):
            raise ValueError
    except ValueError:
        print("  → 输入无效，使用第 1 个候选")
        idx = 1
    selected = candidates[idx - 1]
    print("已选择: " + selected)
    return selected


def _detect_kind(stream_url, referer):
    """
    根据流地址判断处理方式

    返回: ("m3u8" | "direct", 输出文件扩展名)
    """
    suffix = Path(urlparse(stream_url).path).suffix.lower()
    if suffix == ".m3u8":
        return "m3u8", ".ts"
    if suffix in VIDEO_SUFFIXES:
        return "direct", suffix

    # 无/未知后缀：HEAD 探测 Content-Type
    print("流地址无明确后缀，正在探测类型...")
    try:
        req = urllib.request.Request(stream_url, method="HEAD")
        req.add_header("Referer", referer)
        with urllib.request.urlopen(req, timeout=30) as resp:
            ctype = (resp.headers.get("Content-Type") or "").lower()
        if "mpegurl" in ctype or "m3u8" in ctype:
            print("  → 探测结果: M3U8 流媒体")
            return "m3u8", ".ts"
    except Exception as e:
        print("  → 探测失败(%s)，按直链视频处理" % e)
    print("  → 探测结果: 直链视频文件")
    return "direct", ".mp4"


def main():
    print("=" * 56)
    print("  视频下载爬虫 - by Lily")
    print("=" * 56)
    print("请依次完成以下配置（每项输入后回车确认，直接回车使用默认值）")
    print()

    page_url = _ask(
        "[1/4] 页面地址（用于防盗链 Referer 和自动提取视频流）",
        DEFAULT_PAGE_URL)
    stream_url = _ask(
        "[2/4] 视频流地址（m3u8 或 mp4 等直链）",
        DEFAULT_STREAM_URL)
    output_name = _ask(
        "[3/4] 输出文件名（无需扩展名，按流格式自动添加）",
        DEFAULT_OUTPUT_NAME)
    threads = _ask_int(
        "[4/4] 并发下载线程数（仅 M3U8 生效）",
        DEFAULT_THREADS)

    referer = _make_referer(page_url)

    # 视频流地址留空时自动从页面提取
    if not stream_url:
        stream_url = _pick_stream(page_url, referer)
        if not stream_url:
            return 1

    # 按流地址后缀选择处理方式
    kind, ext = _detect_kind(stream_url, referer)
    if not output_name.lower().endswith(ext):
        output_name += ext

    base = Path(__file__).resolve().parent
    slice_dir = base / "slice"     # 下载中的临时数据（支持断点续传）
    result_dir = base / "result"   # 下载完成后的完整视频
    slice_dir.mkdir(exist_ok=True)
    result_dir.mkdir(exist_ok=True)
    output = result_dir / output_name

    print()
    print("-" * 56)
    print("配置汇总:")
    print("  视频流地址: " + stream_url)
    print("  Referer:    " + referer)
    print("  处理方式:   " + ("M3U8 分片下载" if kind == "m3u8" else "直链文件下载"))
    print("  输出文件:   " + str(output))
    if kind == "m3u8":
        print("  并发线程:   %d" % threads)
    print("-" * 56)
    print()

    try:
        if kind == "m3u8":
            dl = M3U8Downloader(referer=referer, workers=threads)
            dl.download(stream_url, str(output), str(slice_dir))
        else:
            dl = DirectDownloader(referer=referer)
            dl.download(stream_url, str(output), str(slice_dir))
    except KeyboardInterrupt:
        print("\n\n[STOP] 下载已被中断！")
        print("已下载的数据保留在 slice 目录中，重新运行本脚本即可断点续传。")
        return 1
    except Exception as e:
        print("\n\n[ERROR] 下载失败: %s" % e)
        print("已下载的数据保留在 slice 目录中，重新运行可断点续传。")
        return 1

    print()
    print("下载完成！视频已保存到 result 目录。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
