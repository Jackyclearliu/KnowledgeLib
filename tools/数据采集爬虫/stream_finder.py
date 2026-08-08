#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
页面视频流地址自动提取
======================
从视频播放页面 HTML 中提取视频流地址（m3u8 / mp4 等）。

提取策略（按优先级）:
    1. <video ... src="..."> 标签的 src 属性
    2. 页面源码（含内嵌 player JSON 配置）中的直链 URL 正则匹配

作者: Lily
"""

import re
import urllib.request
from urllib.parse import urljoin

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/126.0.0.0 Safari/537.36"
)

VIDEO_TAG_RE = re.compile(
    r'<video[^>]+src=["\']([^"\']+)["\']', re.IGNORECASE
)

STREAM_URL_RE = re.compile(
    r'https?://[^"\'\s<>\\]+?\.(?:m3u8|mp4|flv|ts|mkv|webm|mov|avi)'
    r'(?:\?[^"\'\s<>\\]*)?',
    re.IGNORECASE
)


def _fetch_html(url, referer=None, timeout=30, user_agent=None):
    """抓取页面 HTML 文本"""
    req = urllib.request.Request(url)
    req.add_header("User-Agent", user_agent or DEFAULT_USER_AGENT)
    req.add_header("Accept-Language", "zh-CN,zh;q=0.9")
    if referer:
        req.add_header("Referer", referer)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        charset = resp.headers.get_content_charset() or "utf-8"
        return resp.read().decode(charset, errors="replace")


def find_stream_urls(page_url, referer=None, timeout=30):
    """
    从播放页提取候选视频流地址

    返回: 去重后的候选 URL 列表（保持出现顺序），可能为空
    """
    html = _fetch_html(page_url, referer=referer, timeout=timeout)

    candidates = []

    def _add(url):
        url = url.strip()
        if not url:
            return
        url = urljoin(page_url, url)
        if url not in candidates:
            candidates.append(url)

    # 1. <video> 标签 src 属性
    for m in VIDEO_TAG_RE.finditer(html):
        _add(m.group(1))

    # 2. 通用直链正则（先将 JSON 中的 \/ 反转义，覆盖 player_aaaa 这类内嵌配置）
    unescaped = html.replace("\\/", "/")
    for m in STREAM_URL_RE.finditer(unescaped):
        _add(m.group(0))

    return candidates
