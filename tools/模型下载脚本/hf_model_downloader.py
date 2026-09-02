#!/usr/bin/env python3
"""
通用 HuggingFace 模型下载脚本

功能特性：
- 交互式配置模型 Repo 与保存路径（直接回车使用默认值）
- 聚合总进度条，实时感知整体下载进度
- 网络失败自动告警并切换镜像（huggingface.co -> hf-mirror.com）
- 断点续传：中断后重新运行会自动跳过已完成文件、续传未完成文件

用法：
    python hf_model_downloader.py                     # 交互式
    python hf_model_downloader.py --repo-id xxx/yyy --local-dir ./models/yyy
"""
import argparse
import fnmatch
import os
import sys
import time

# 禁用 Xet 后端，强制走普通 HTTP 下载：
# hf-mirror 等镜像无法代理 Xet 的 CAS 服务器（cas-server.xethub.hf.co），
# 启用 Xet 时经镜像下载会出现 401 Unauthorized。
# 如需重新启用（直连官方源且追求极致速度），可在运行前设置 HF_HUB_DISABLE_XET=0。
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")

# ---------------- 默认配置（按需修改） ----------------
DEFAULT_REPO_ID = "neuregex/Bernini-R-fp8"
DEFAULT_LOCAL_DIR = r"D:\Program Files\AI\ComfyUI\models\bernini\Bernini-R-fp8"

# 下载源列表：官方源优先，失败后自动切换到国内镜像
ENDPOINTS = [
    "https://huggingface.co",
    "https://hf-mirror.com",
]
MAX_RETRIES_PER_ENDPOINT = 3          # 每个端点最大重试次数
RETRY_BACKOFF_SECONDS = [5, 15, 30]   # 重试间隔（逐次加长）

# ---------------- 依赖检查 ----------------
try:
    from huggingface_hub import HfApi
    from huggingface_hub.utils import HfHubHTTPError, LocalEntryNotFoundError
except ImportError:
    print("错误: huggingface_hub 未安装")
    print("请先执行: pip install huggingface_hub")
    sys.exit(1)

try:
    from tqdm import tqdm
except ImportError:
    print("错误: tqdm 未安装")
    print("请先执行: pip install tqdm")
    sys.exit(1)

# 网络异常类型：huggingface_hub 不同版本底层用 httpx 或 requests，两者都要覆盖
NETWORK_EXCEPTIONS = [ConnectionError, TimeoutError, OSError]
try:
    from requests.exceptions import RequestException
    NETWORK_EXCEPTIONS.append(RequestException)
except ImportError:
    pass
try:
    import httpx
    NETWORK_EXCEPTIONS.append(httpx.HTTPError)  # 含 ConnectError/ReadTimeout 等
except ImportError:
    pass
NETWORK_EXCEPTIONS = tuple(NETWORK_EXCEPTIONS)


class AggregatedProgressTqdm(tqdm):
    """聚合所有下载进度到一个总进度条的 tqdm 子类。

    snapshot_download 内部的进度条（按字节下载的进度、"Fetching N files"
    计数条等）都会创建本类实例；这些子进度条不显示，字节进度统一聚合到
    全局总进度条上。
    """

    _overall = None

    @classmethod
    def start_overall(cls, total_bytes):
        cls._overall = tqdm(
            total=total_bytes,
            desc="总进度",
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            dynamic_ncols=True,
        )

    @classmethod
    def finish_overall(cls):
        """下载成功时把总进度条补齐到 100% 并关闭。"""
        if cls._overall is not None:
            cls._overall.n = cls._overall.total
            cls._overall.refresh()
            cls._overall.close()
            cls._overall = None

    @classmethod
    def close_overall(cls):
        if cls._overall is not None:
            cls._overall.close()
            cls._overall = None

    def __init__(self, *args, **kwargs):
        # disable=True 时 tqdm 不初始化 unit 等属性，需自行记录
        self._is_byte_progress = kwargs.get("unit") == "B"
        kwargs["disable"] = True  # 子进度条不显示
        super().__init__(*args, **kwargs)

    def update(self, n=1):
        super().update(n)
        # 只聚合按字节下载的进度，忽略 "Fetching N files" 之类的计数条
        if self._is_byte_progress and type(self)._overall is not None:
            type(self)._overall.update(n)


def is_network_error(exc):
    """判断异常是否由网络问题引起（决定是否重试/切换镜像）。"""
    if isinstance(exc, LocalEntryNotFoundError):
        # 无法连接到 Hub 且本地无缓存时抛出
        return True
    if isinstance(exc, HfHubHTTPError):
        # 4xx（仓库不存在、无权限等）不是网络问题，重试无意义
        status = getattr(exc.response, "status_code", None)
        return status is None or status >= 500 or status in (408, 429)
    return isinstance(exc, NETWORK_EXCEPTIONS)


def build_endpoint_order(preferred_endpoint=None):
    """把用户指定的首选端点排在最前，其余端点作为后备。"""
    endpoints = list(ENDPOINTS)
    if preferred_endpoint and preferred_endpoint not in endpoints:
        endpoints.insert(0, preferred_endpoint)
    elif preferred_endpoint:
        endpoints.remove(preferred_endpoint)
        endpoints.insert(0, preferred_endpoint)
    return endpoints


def get_repo_files(api, repo_id, allow_patterns):
    """获取仓库文件清单及总大小（用于进度条总量预估）。"""
    info = api.repo_info(repo_id=repo_id, repo_type="model", files_metadata=True)
    files = [(s.rfilename, s.size or 0) for s in info.siblings]
    if allow_patterns:
        files = [
            (name, size) for name, size in files
            if any(fnmatch.fnmatch(name, p) for p in allow_patterns)
        ]
    return files


def format_size(num_bytes):
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if num_bytes < 1024 or unit == "TB":
            return f"{num_bytes:.2f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.2f} TB"


def download_with_failover(repo_id, local_dir, allow_patterns, preferred_endpoint=None):
    """带端点自动切换的下载主循环。"""
    endpoints = build_endpoint_order(preferred_endpoint)

    for idx, endpoint in enumerate(endpoints):
        is_last_endpoint = idx == len(endpoints) - 1

        for attempt in range(1, MAX_RETRIES_PER_ENDPOINT + 1):
            try:
                api = HfApi(endpoint=endpoint)

                # 仅在首次尝试时打印文件清单信息
                files = get_repo_files(api, repo_id, allow_patterns)
                total_bytes = sum(size for _, size in files)
                if endpoint == endpoints[0] and attempt == 1:
                    print(f"共 {len(files)} 个文件，总计约 {format_size(total_bytes)}")
                    print("-" * 50)

                AggregatedProgressTqdm.start_overall(total_bytes)
                try:
                    api.snapshot_download(
                        repo_id=repo_id,
                        repo_type="model",
                        local_dir=local_dir,
                        allow_patterns=allow_patterns,
                        tqdm_class=AggregatedProgressTqdm,
                    )
                except Exception:
                    AggregatedProgressTqdm.close_overall()
                    raise

                AggregatedProgressTqdm.finish_overall()
                return  # 下载成功

            except Exception as exc:
                if not is_network_error(exc):
                    raise

                if attempt < MAX_RETRIES_PER_ENDPOINT:
                    wait = RETRY_BACKOFF_SECONDS[attempt - 1]
                    print(f"\n⚠️  下载中断（{endpoint}）: {type(exc).__name__}: {exc}")
                    print(f"    {wait} 秒后重试（第 {attempt + 1}/{MAX_RETRIES_PER_ENDPOINT} 次，已下载部分自动续传）...")
                    time.sleep(wait)
                else:
                    print(f"\n⚠️  端点 {endpoint} 重试 {MAX_RETRIES_PER_ENDPOINT} 次均失败")

        if not is_last_endpoint:
            print(f"🔄 切换下载源: {endpoint} -> {endpoints[idx + 1]}")
            print("-" * 50)

    print("❌ 所有下载源均连接失败，请检查网络后重试（重新运行会自动续传）")
    sys.exit(1)


def parse_args():
    parser = argparse.ArgumentParser(
        description="通用 HuggingFace 模型下载脚本（支持进度显示与镜像自动切换）"
    )
    parser.add_argument("--repo-id", help="模型仓库 ID，如 neuregex/Bernini-R-fp8")
    parser.add_argument("--local-dir", help="模型保存路径")
    parser.add_argument(
        "--patterns",
        help='文件过滤规则，逗号分隔，如 "*.safetensors,*.json"（默认下载整个仓库）',
    )
    parser.add_argument("--endpoint", help="首选下载源（默认官方源，失败后自动切换镜像）")
    return parser.parse_args()


def prompt_if_missing(cli_value, prompt_text, default):
    """命令行未提供时交互式询问，直接回车使用默认值。"""
    if cli_value:
        return cli_value
    answer = input(f"{prompt_text} [默认: {default}]: ").strip()
    return answer or default


def main():
    # Windows 控制台 UTF-8 输出，避免中文/emoji 乱码（tqdm 进度条写到 stderr）
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass

    args = parse_args()

    repo_id = prompt_if_missing(args.repo_id, "请输入模型 Repo ID", DEFAULT_REPO_ID)
    local_dir = prompt_if_missing(args.local_dir, "请输入模型保存路径", DEFAULT_LOCAL_DIR)

    patterns_raw = args.patterns
    if patterns_raw is None:
        patterns_raw = input("文件过滤规则（可选，如 *.safetensors，直接回车下载整个仓库）: ").strip()
    allow_patterns = [p.strip() for p in patterns_raw.split(",") if p.strip()] or None

    print("-" * 50)
    print(f"模型仓库: {repo_id}")
    print(f"保存路径: {local_dir}")
    print(f"文件过滤: {', '.join(allow_patterns) if allow_patterns else '无（下载整个仓库）'}")

    os.makedirs(local_dir, exist_ok=True)

    try:
        download_with_failover(
            repo_id=repo_id,
            local_dir=local_dir,
            allow_patterns=allow_patterns,
            preferred_endpoint=args.endpoint,
        )
    except HfHubHTTPError as exc:
        status = getattr(exc.response, "status_code", None)
        if status == 404:
            print(f"❌ 仓库不存在或无权访问: {repo_id}")
        elif status in (401, 403):
            print(f"❌ 无权限访问: {repo_id}（若是私有/受限仓库，请先 huggingface-cli login）")
        else:
            print(f"❌ 下载失败: {exc}")
        sys.exit(1)

    print("-" * 50)
    print("✅ 模型下载完成!")
    print(f"保存位置: {local_dir}")


if __name__ == "__main__":
    main()
