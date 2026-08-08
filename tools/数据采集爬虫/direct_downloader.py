#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直链视频文件下载器
==================
用于下载非 M3U8 的直链视频文件（mp4 / flv / mkv 等）。
支持断点续传：未完成的文件保存在片段目录的 .part 文件中。

作者: Lily
"""

import sys
import time
import urllib.request
from pathlib import Path

CHUNK_SIZE = 64 * 1024

# 可按直链处理的视频后缀
VIDEO_SUFFIXES = {".mp4", ".flv", ".ts", ".mkv", ".webm", ".mov", ".avi"}


class DirectDownloader:
    """直链文件下载器（单连接流式下载，支持断点续传）"""

    def __init__(self, referer=None, user_agent=None, timeout=30):
        self.referer = referer or "https://www.yhdm28.com/"
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/126.0.0.0 Safari/537.36"
        )
        self.timeout = timeout

    def _log(self, msg):
        print(msg)

    @staticmethod
    def _fmt_size(num):
        """格式化字节数为易读单位"""
        for unit in ("B", "KB", "MB", "GB"):
            if num < 1024 or unit == "GB":
                return "%.1f %s" % (num, unit)
            num /= 1024

    @staticmethod
    def _fmt_time(seconds):
        """格式化秒数为 mm:ss"""
        seconds = max(0, int(seconds))
        return "%02d:%02d" % (seconds // 60, seconds % 60)

    def download(self, url, output_path, part_dir=None):
        """
        下载直链视频文件

        Args:
            url: 视频文件直链地址
            output_path: 最终输出文件路径
            part_dir: 未完成文件（.part）存放目录（默认输出文件同级目录）
        """
        output_path = Path(output_path).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if part_dir is None:
            part_dir = output_path.parent
        part_dir = Path(part_dir).resolve()
        part_dir.mkdir(parents=True, exist_ok=True)
        part_path = part_dir / (output_path.name + ".part")

        downloaded = part_path.stat().st_size if part_path.exists() else 0

        req = urllib.request.Request(url)
        req.add_header("Referer", self.referer)
        req.add_header("User-Agent", self.user_agent)
        req.add_header("Accept", "*/*")
        if downloaded > 0:
            req.add_header("Range", "bytes=%d-" % downloaded)
            self._log("[RESUME] 检测到未完成文件，从 %s 处断点续传"
                      % self._fmt_size(downloaded))

        self._log("[URL] 文件地址: " + url)
        self._log("[OUT] 输出文件: " + str(output_path))

        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            # 服务器忽略 Range 返回 200 时，只能从头下载
            if downloaded > 0 and resp.status == 200:
                self._log("[WARN] 服务器不支持断点续传，从头重新下载")
                downloaded = 0

            total = None
            content_length = resp.headers.get("Content-Length")
            if content_length is not None:
                total = downloaded + int(content_length)
                self._log("[SIZE] 文件大小: " + self._fmt_size(total))
            self._log("")

            start = time.time()
            run_bytes = 0
            mode = "ab" if downloaded > 0 else "wb"
            with open(part_path, mode) as f:
                while True:
                    chunk = resp.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    run_bytes += len(chunk)

                    # 实时进度：进度条 / 百分比 / 大小 / 速度 / 预计剩余时间
                    elapsed = time.time() - start
                    speed = run_bytes / elapsed if elapsed > 0 else 0
                    if total:
                        progress = downloaded / total * 100
                        bar_len = 30
                        filled = int(bar_len * downloaded / total)
                        bar = "#" * filled + "-" * (bar_len - filled)
                        eta = (elapsed * (total - downloaded) / run_bytes
                               if run_bytes > 0 else 0)
                        line = ("\r   [%s] %5.1f%% | %s/%s | %s/s | 剩余 %s"
                                % (bar, progress,
                                   self._fmt_size(downloaded),
                                   self._fmt_size(total),
                                   self._fmt_size(speed),
                                   self._fmt_time(eta)))
                    else:
                        line = ("\r   已下载 %s | %s/s"
                                % (self._fmt_size(downloaded),
                                   self._fmt_size(speed)))
                    sys.stdout.write(line)
                    sys.stdout.flush()

        self._log("")
        part_path.replace(output_path)
        self._log("")
        self._log("[DONE] 下载完成！输出文件: " + str(output_path))
        self._log("   文件大小: %.2f MB"
                  % (output_path.stat().st_size / 1024 / 1024))
        return output_path
