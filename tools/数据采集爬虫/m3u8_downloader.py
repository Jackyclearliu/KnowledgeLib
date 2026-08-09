#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
M3U8 视频下载爬虫
================
用于下载基于 M3U8 流媒体协议的视频文件。

使用示例:
    python m3u8_downloader.py --url "https://cdn.xxx.com/xxx/index.m3u8" --output "video.mp4"

作者: Lily
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from threading import Lock
from urllib.parse import urljoin, urlparse


class M3U8Downloader:
    """M3U8 视频流下载器"""

    def __init__(self, referer=None, user_agent=None, workers=8, timeout=30):
        self.referer = referer or "https://www.yhdm28.com/"
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/126.0.0.0 Safari/537.36"
        )
        self.workers = workers
        self.timeout = timeout
        self.print_lock = Lock()

    def _make_request(self, url):
        """创建带请求头的 HTTP 请求"""
        req = urllib.request.Request(url)
        req.add_header("Referer", self.referer)
        req.add_header("User-Agent", self.user_agent)
        req.add_header("Accept", "*/*")
        req.add_header("Accept-Language", "zh-CN,zh;q=0.9")
        return req

    def _fetch_text(self, url):
        """获取文本内容"""
        req = self._make_request(url)
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            return resp.read().decode("utf-8")

    def _fetch_binary(self, url):
        """获取二进制内容"""
        req = self._make_request(url)
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            return resp.read()

    def _log(self, msg):
        """线程安全的日志输出"""
        with self.print_lock:
            print(msg)

    def parse_m3u8(self, content, base_url):
        """
        解析 M3U8 文件内容
        返回: (segments列表, 是否为多层m3u8)
        """
        lines = content.strip().splitlines()
        segments = []
        is_master = False

        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                # 检测是否是主索引文件（多层m3u8）
                if line.startswith("#EXT-X-STREAM-INF"):
                    is_master = True
                continue
            # 这是一个URL或相对路径
            full_url = urljoin(base_url, line)
            segments.append(full_url)

        return segments, is_master

    def select_best_stream(self, master_url):
        """
        从主 M3U8 中选择最高码率的子流
        返回: 选中的子m3u8 URL
        """
        content = self._fetch_text(master_url)
        lines = content.strip().splitlines()

        streams = []
        current_info = {}

        for line in lines:
            line = line.strip()
            if line.startswith("#EXT-X-STREAM-INF"):
                # 解析 BANDWIDTH 和 RESOLUTION
                bw_match = re.search(r'BANDWIDTH=(\d+)', line)
                res_match = re.search(r'RESOLUTION=(\d+)x(\d+)', line)
                current_info = {
                    'bandwidth': int(bw_match.group(1)) if bw_match else 0,
                    'width': int(res_match.group(1)) if res_match else 0,
                    'height': int(res_match.group(2)) if res_match else 0,
                }
            elif line and not line.startswith("#"):
                full_url = urljoin(master_url, line)
                current_info['url'] = full_url
                streams.append(current_info)
                current_info = {}

        if not streams:
            raise ValueError("主 M3U8 中未找到任何子流")

        # 按带宽降序排序，选择最高码率
        streams.sort(key=lambda x: x['bandwidth'], reverse=True)
        best = streams[0]
        self._log("[VIDEO] 选中最高质量流: %sx%s | 码率: %.0f kbps" % (
            best.get('width', '?'), best.get('height', '?'),
            best['bandwidth'] / 1000))
        return best['url']

    def download_segment(self, args):
        """下载单个 TS 片段"""
        idx, total, url, temp_dir = args
        seg_path = temp_dir / ("%06d.ts" % idx)

        # 如果已存在则跳过
        if seg_path.exists() and seg_path.stat().st_size > 0:
            return idx, True, seg_path, "已缓存", seg_path.stat().st_size

        try:
            data = self._fetch_binary(url)
            seg_path.write_bytes(data)
            return idx, True, seg_path, "OK (%d bytes)" % len(data), len(data)
        except Exception as e:
            return idx, False, None, str(e), 0

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

    def download(self, m3u8_url, output_path, temp_dir=None):
        """
        下载 M3U8 视频

        Args:
            m3u8_url: M3U8 索引文件地址
            output_path: 最终输出文件路径
            temp_dir: 临时文件目录（默认在输出文件同级目录创建）
        """
        output_path = Path(output_path).resolve()
        if temp_dir is None:
            temp_dir = output_path.parent / (".temp_" + output_path.stem)
        else:
            temp_dir = Path(temp_dir).resolve()

        temp_dir.mkdir(parents=True, exist_ok=True)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        self._log("[URL] M3U8 地址: " + m3u8_url)
        self._log("[DIR] 临时目录: " + str(temp_dir))
        self._log("[OUT] 输出文件: " + str(output_path))
        if not shutil.which("ffmpeg"):
            self._log("[WARN] 未检测到 ffmpeg，合并时将回退为二进制拼接，"
                      "输出视频的时长元数据可能异常！")
        self._log("")

        # Step 1: 获取并解析主 M3U8
        self._log("[STEP 1/4] 解析 M3U8 索引...")
        master_content = self._fetch_text(m3u8_url)
        _, is_master = self.parse_m3u8(master_content, m3u8_url)

        if is_master:
            self._log("   检测到多层 M3U8，选择最高码率流...")
            stream_url = self.select_best_stream(m3u8_url)
        else:
            stream_url = m3u8_url

        # Step 2: 获取子 M3U8 的片段列表
        self._log("[STEP 2/4] 获取片段列表...")
        stream_content = self._fetch_text(stream_url)
        segments, _ = self.parse_m3u8(stream_content, stream_url)

        if not segments:
            raise ValueError("未找到任何 TS 片段")

        self._log("   共发现 %d 个 TS 片段" % len(segments))
        self._log("")

        # Step 3: 并发下载所有片段
        self._log("[STEP 3/4] 开始下载片段...")
        args_list = [(i, len(segments), url, temp_dir)
                     for i, url in enumerate(segments)]

        success_count = 0
        fail_count = 0
        failed_indices = []
        downloaded_bytes = 0
        download_start = time.time()
        total = len(segments)

        executor = ThreadPoolExecutor(max_workers=self.workers)
        try:
            futures = {executor.submit(self.download_segment, a): a[0]
                       for a in args_list}

            for future in as_completed(futures):
                idx, ok, path, msg, size = future.result()
                if ok:
                    success_count += 1
                    downloaded_bytes += size
                else:
                    fail_count += 1
                    failed_indices.append(idx)
                    self._log("   [WARN] 片段 %d 失败: %s" % (idx, msg))

                # 实时进度：进度条 / 百分比 / 数量 / 已下载大小 / 速度 / 预计剩余时间
                done = success_count + fail_count
                progress = done / total * 100
                bar_len = 30
                filled = int(bar_len * done / total)
                bar = "#" * filled + "-" * (bar_len - filled)
                elapsed = time.time() - download_start
                speed = downloaded_bytes / elapsed if elapsed > 0 else 0
                eta = elapsed * (total - done) / done if done > 0 else 0
                sys.stdout.write(
                    "\r   [%s] %5.1f%% | %d/%d 片段 | %s | %s/s | 剩余 %s | 失败 %d" %
                    (bar, progress, done, total,
                     self._fmt_size(downloaded_bytes), self._fmt_size(speed),
                     self._fmt_time(eta), fail_count)
                )
                sys.stdout.flush()
        except KeyboardInterrupt:
            # 中断时取消排队中的任务，让 Ctrl+C 立即生效
            executor.shutdown(wait=False, cancel_futures=True)
            self._log("")
            raise
        executor.shutdown(wait=True)

        self._log("")
        self._log("")

        if fail_count > 0:
            self._log("[WARN] 共有 %d 个片段下载失败" % fail_count)
            # 简单重试一次失败的片段
            if failed_indices:
                self._log("[RETRY] 尝试重试失败的片段...")
                retry_args = [(i, len(segments), segments[i], temp_dir)
                              for i in failed_indices]
                with ThreadPoolExecutor(max_workers=self.workers) as executor:
                    for future in as_completed(
                        executor.submit(self.download_segment, a)
                        for a in retry_args
                    ):
                        idx, ok, path, msg, size = future.result()
                        if ok:
                            success_count += 1
                            fail_count -= 1
                            downloaded_bytes += size
                        self._log("   [RETRY] 片段 %d: %s" %
                                  (idx, "成功" if ok else ("仍失败: " + msg)))

        if success_count == 0:
            raise RuntimeError("所有片段下载失败！")

        # Step 4: 合并片段
        self._log("[STEP 4/4] 合并视频片段...")
        self.merge_segments(temp_dir, output_path, len(segments))

        self._log("")
        self._log("[DONE] 下载完成！输出文件: " + str(output_path))
        self._log("   文件大小: %.2f MB" % (output_path.stat().st_size / 1024 / 1024))

        # 清理临时片段
        self._log("[CLEAN] 清理临时片段...")
        self._clean_temp(temp_dir)

        return output_path

    def merge_segments(self, temp_dir, output_path, total_count):
        """按顺序合并 TS 片段为最终视频文件"""
        output_path = Path(output_path).resolve()
        seg_paths = [temp_dir / ("%06d.ts" % i) for i in range(total_count)]
        seg_paths = [p for p in seg_paths if p.exists()]

        ffmpeg = shutil.which("ffmpeg")
        if not ffmpeg:
            # 无 ffmpeg 时只能直接二进制拼接：时间戳不连续、无正确时长元数据，
            # 播放器和剪辑软件可能无法识别完整时长，故给出明确警告
            self._log("   [WARN] 未检测到 ffmpeg，回退为直接二进制拼接。")
            self._log("   [WARN] 合并结果可能存在时长显示异常，建议安装 ffmpeg 后重试。")
            with open(output_path, "wb") as outf:
                for seg_path in seg_paths:
                    with open(seg_path, "rb") as segf:
                        outf.write(segf.read())
            return

        self._merge_with_ffmpeg(ffmpeg, seg_paths, temp_dir, output_path)

    def _merge_with_ffmpeg(self, ffmpeg, seg_paths, temp_dir, output_path):
        """
        使用 ffmpeg concat demuxer 合并片段并重新封装。
        不重编码（-c copy），仅重建连续时间戳并写入正确的容器元数据，
        避免直接二进制拼接导致的时长显示异常 / 剪辑软件无法识别问题。
        """
        list_path = temp_dir / "_concat_list.txt"
        with open(list_path, "w", encoding="utf-8") as f:
            for seg_path in seg_paths:
                # 使用片段文件名（相对列表文件所在目录解析）
                f.write("file '%s'\n" % seg_path.name)

        cmd = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
               "-f", "concat", "-safe", "0", "-i", list_path.name,
               "-c", "copy"]
        if output_path.suffix.lower() == ".mp4":
            # TS 中的 AAC 为 ADTS 格式，封装进 MP4 需转换；faststart 便于流式播放
            cmd += ["-bsf:a", "aac_adtstoasc", "-movflags", "+faststart"]
        cmd.append(str(output_path))

        try:
            subprocess.run(cmd, cwd=str(temp_dir), check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError("ffmpeg 合并失败（退出码 %d）" % e.returncode)
        finally:
            try:
                list_path.unlink()
            except OSError:
                pass

    def _clean_temp(self, temp_dir):
        """清理临时片段文件（保留目录本身，便于断点续传时复用）"""
        for f in temp_dir.glob("*.ts"):
            try:
                f.unlink()
            except Exception:
                pass


def main():
    parser = argparse.ArgumentParser(
        description="M3U8 视频下载爬虫 - by Lily",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python m3u8_downloader.py -u "https://cdn.xxx.com/video/index.m3u8" -o "output.mp4"
  python m3u8_downloader.py -u "URL" -o "video.ts" -w 16

注意事项:
  - 如果 M3U8 需要 Referer，请使用 -r 参数指定
  - 默认使用 8 线程下载，可通过 -w 调整
  - 输出格式建议 .ts 或 .mp4，剪映均可导入
        """
    )
    parser.add_argument(
        "-u", "--url", required=True,
        help="M3U8 索引文件 URL"
    )
    parser.add_argument(
        "-o", "--output", required=True,
        help="输出视频文件路径（如 output.ts / output.mp4）"
    )
    parser.add_argument(
        "-r", "--referer",
        default="https://www.yhdm28.com/",
        help="HTTP Referer 头（防盗链用，默认: yhdm28）"
    )
    parser.add_argument(
        "-w", "--workers", type=int, default=8,
        help="并发下载线程数（默认: 8）"
    )
    parser.add_argument(
        "-t", "--timeout", type=int, default=30,
        help="HTTP 请求超时秒数（默认: 30）"
    )
    parser.add_argument(
        "--temp-dir",
        help="临时文件存放目录（默认: 输出文件同级目录的 .temp_xxx 文件夹）"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("  M3U8 视频下载爬虫 - by Lily")
    print("=" * 60)
    print()

    dl = M3U8Downloader(
        referer=args.referer,
        workers=args.workers,
        timeout=args.timeout
    )

    start_time = time.time()
    try:
        dl.download(args.url, args.output, args.temp_dir)
    except KeyboardInterrupt:
        print("\n\n[STOP] 下载已被中断！")
        print("       已下载的片段保留在片段目录（默认 slice/）中，")
        print("       重新运行相同命令即可断点续传，无需从头下载。")
        sys.exit(1)
    except Exception as e:
        print("\n\n[ERROR] 下载失败: %s" % e)
        print("        已下载的片段保留在片段目录中，重新运行可断点续传。")
        sys.exit(1)

    elapsed = time.time() - start_time
    print()
    print("[TIME] 总耗时: %.1f 秒" % elapsed)
    print("=" * 60)


if __name__ == "__main__":
    main()
