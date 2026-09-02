# 通用 HuggingFace 模型下载脚本

`hf_model_downloader.py` —— 从 `ComfyUI部署/_auto_download_bernini.py` 改造而来的通用 HuggingFace 模型下载器，不再绑定特定模型，适用于任意 HuggingFace 仓库（ComfyUI 模型、LLM 权重等）。

## 功能特性

- **可配置**：模型仓库 ID、保存路径、文件过滤规则均可在运行时输入，直接回车使用默认值
- **进度显示**：下载前统计文件总数和总大小，下载过程中以聚合总进度条实时显示百分比、速度和剩余时间
- **镜像自动切换**：网络原因导致下载中断时自动告警、重试，官方源多次失败后自动切换到国内镜像 `hf-mirror.com`
- **断点续传**：任何时候中断（网络故障、Ctrl+C），重新运行脚本会自动跳过已完成文件、续传未完成文件

## 环境依赖

```bash
pip install huggingface_hub tqdm
```

要求 Python 3.10+。

## 使用方式

### 交互式（推荐）

```bash
python hf_model_downloader.py
```

按提示逐项输入，**直接回车即使用默认值**：

```
请输入模型 Repo ID [默认: neuregex/Bernini-R-fp8]:
请输入模型保存路径 [默认: D:\Program Files\AI\ComfyUI\models\bernini\Bernini-R-fp8]:
文件过滤规则（可选，如 *.safetensors，直接回车下载整个仓库）:
```

默认值定义在脚本顶部的 `DEFAULT_REPO_ID` / `DEFAULT_LOCAL_DIR` 常量中，可按需修改。

### 命令行参数（适合脚本化调用）

```bash
# 下载指定模型到指定目录
python hf_model_downloader.py --repo-id black-forest-labs/FLUX.1-dev --local-dir ./models/flux

# 只下载 safetensors 权重文件
python hf_model_downloader.py --repo-id xxx/yyy --local-dir ./models/yyy --patterns "*.safetensors,*.json"

# 指定首选下载源（如直连官方源不通，可直接首选镜像）
python hf_model_downloader.py --repo-id xxx/yyy --endpoint https://hf-mirror.com
```

| 参数 | 说明 |
| --- | --- |
| `--repo-id` | 模型仓库 ID，如 `neuregex/Bernini-R-fp8` |
| `--local-dir` | 模型保存路径 |
| `--patterns` | 文件过滤规则，逗号分隔，如 `*.safetensors,*.json`；不填下载整个仓库 |
| `--endpoint` | 首选下载源；不填默认官方源优先 |

## 镜像切换机制

脚本内置下载源列表：`https://huggingface.co`（官方）→ `https://hf-mirror.com`（国内镜像）。

- 捕获到网络类异常（连接失败、超时、5xx 等）时，打印告警并在 5s / 15s / 30s 退避后重试，每个端点最多重试 3 次
- 当前端点重试耗尽后自动切换到下一个端点，已下载的部分会自动续传，不会重新下载
- 4xx 错误（仓库不存在、无权限）不属于网络问题，会直接报错退出，不做无谓重试
- 也可通过 `HF_ENDPOINT` 环境变量预先指定首选端点

**关于 Xet**：脚本默认设置 `HF_HUB_DISABLE_XET=1` 禁用 Xet 加速后端。原因是 Xet 会直连官方 CAS 服务器（`cas-server.xethub.hf.co`），镜像无法代理，经镜像下载时会报 `401 Unauthorized`。禁用后统一走普通 HTTP 下载，官方源和镜像均可正常工作。若你能直连官方源并希望启用 Xet 加速，可在运行前设置环境变量 `HF_HUB_DISABLE_XET=0`。

## 常见问题

**Q: 镜像也连不上怎么办？**
所有端点都失败后脚本会提示并退出。检查本机网络/代理设置后重新运行即可，已下载的文件不会丢失（断点续传）。若使用代理，可通过 `HTTPS_PROXY` 环境变量配置。

**Q: 之前遇到过 `CAS Client Error: 401 Unauthorized` 报错？**
这是 Xet 后端与镜像不兼容导致的（Xet 直连官方 CAS 服务器，镜像 token 无效）。脚本已默认禁用 Xet，升级到最新版脚本即可；重新运行会自动断点续传。

**Q: 只想下载仓库里的部分文件？**
使用文件过滤规则，如 `--patterns "*.safetensors"` 只下载权重文件，`--patterns "vae/*"` 只下载 vae 目录。

**Q: 私有或受限仓库（如 FLUX.1-dev）提示 401/403？**
先执行 `huggingface-cli login` 登录账号，并在 HuggingFace 网页上同意该仓库的使用协议。

**Q: 进度条显示的总量为什么和实际略有出入？**
个别仓库文件元数据缺少大小信息时按 0 计入总量，不影响实际下载完整性。
