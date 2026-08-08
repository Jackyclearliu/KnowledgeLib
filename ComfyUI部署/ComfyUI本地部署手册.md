# ComfyUI 本地部署完整手册

> **目标机型**：Windows 11 ｜ RTX 4090 24GB ｜ AMD 9900X3D ｜ 32GB 内存 ｜ 6TB 硬盘
> **部署方式**：git clone 源码安装
> **模型清单**：文生图 FLUX.2 [dev] + SDXL ｜ 视频生成 Bernini ｜ 语音合成 Index-TTS
> 手册更新日期：2026-08-01

---

## 目录

- [一、部署前准备](#一部署前准备)
- [二、安装 ComfyUI 本体](#二安装-comfyui-本体)
- [三、安装 ComfyUI Manager（必装插件管理器）](#三安装-comfyui-manager必装插件管理器)
- [四、模型部署一：FLUX.2 [dev]（文生图主力）](#四模型部署一flux2-dev文生图主力)
- [五、模型部署二：SDXL（文生图 / LoRA 生态）](#五模型部署二sdxl文生图--lora-生态)
- [六、模型部署三：Bernini（视频生成）](#六模型部署三bernini视频生成)
- [七、模型部署四：Index-TTS（语音合成）](#七模型部署四index-tts语音合成)
- [八、目录结构总览与空间预算](#八目录结构总览与空间预算)
- [九、启动参数与性能优化建议](#九启动参数与性能优化建议)
- [十、常见问题排查](#十常见问题排查)
- [十一、资源链接汇总](#十一资源链接汇总)

---

## 一、部署前准备

### 1.1 必装软件

| 软件 | 版本要求 | 下载地址 | 验证命令 | 安装状态 |
|---|---|---|---|---|
| Git for Windows | 最新版 | https://git-scm.com/downloads/win | `git --version` | 已安装 |
| Python | **3.12**（兼容性最好）或 3.13 | https://www.python.org/downloads/ | `python --version` | 已安装 |
| NVIDIA 显卡驱动 | 最新 Game Ready / Studio 驱动 | https://www.nvidia.cn/drivers/ | `nvidia-smi` | 待验证 |

> ⚠️ **安装 Python 时务必勾选 "Add Python to PATH"**。
> ⚠️ 安装完 Git 后需要**重启终端**（或重启电脑）才能识别 `git` 命令。

### 1.2 安装位置

建议将 ComfyUI 安装在**非 C 盘的大容量分区**（如 `D:\Program Files\AI\`），后续模型会占用数百 GB：

```
D:\Program Files\AI\ComfyUI          ← 当前实际已安装位置
```

### 1.3 网络环境（国内用户重要）

HuggingFace 在国内访问不稳定，建议提前准备以下加速手段之一：

```powershell
# 方案 A：使用国内 HF 镜像（PowerShell 临时设置）
$env:HF_ENDPOINT = "https://hf-mirror.com"

# 方案 B：安装 ModelScope（魔搭）客户端，从国内源下载模型
pip install modelscope
```

> 后文每个模型都会同时给出 HuggingFace 和（可用的）ModelScope 下载方式。

---

## 二、安装 ComfyUI 本体（已完成）

### 2.1 克隆仓库

打开 PowerShell 或 CMD：

```powershell
cd D:\AI
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
```

> ComfyUI 官方仓库：https://github.com/comfyanonymous/ComfyUI
> （Comfy-Org 组织下的 https://github.com/Comfy-Org/ComfyUI 为同一项目的组织镜像，二者皆可，本手册以主仓库为准。）

### 2.2 创建虚拟环境（强烈建议，避免污染系统 Python）

```powershell
python -m venv venv
.\venv\Scripts\activate
```

> 后续**所有** pip 安装和启动操作都要先激活该环境（激活后命令行前缀会出现 `(venv)`）。

### 2.3 安装 PyTorch（RTX 4090 专用）

RTX 4090 为 Ada 架构（sm_89），安装 CUDA 12.8 版本的 PyTorch：

```powershell
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
```

验证 GPU 是否被识别：

```powershell
python -c "import torch; print(torch.__version__); print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0))"
```

预期输出：`True` + `NVIDIA GeForce RTX 4090`。

### 2.4 安装 ComfyUI 依赖

```powershell
pip install -r requirements.txt
```

### 2.5 首次启动测试

```powershell
python main.py
```

浏览器访问 **http://127.0.0.1:8188**，能看到节点界面即安装成功（此时还没装模型，暂不能出图）。按 `Ctrl+C` 关闭，继续下一步。

### 安装完成总结

ComfyUI 已经成功安装在 D:\Program Files\AI\ComfyUI

#### 安装结构

```
D:\Program Files\AI\
└── ComfyUI\              ← 主程序目录
    ├── venv\             ← Python 3.13 虚拟环境
    ├── models\           ← 模型存放目录（待补充）
    ├── custom_nodes\     ← 自定义节点
    ├── input\            ← 输入图片
    ├── output\           ← 输出结果
    ├── start.bat         ← 快速启动脚本（CMD）
    └── start.ps1         ← 快速启动脚本（PowerShell）
```

#### 启动方式

方式1：双击启动
直接双击 D:\Program Files\AI\ComfyUI\start.bat

方式2：命令行启动

```powershell
# CMD
D:\Program Files\AI\ComfyUI\start.bat

# PowerShell
& "D:\Program Files\AI\ComfyUI\start.ps1"
```

启动后会自动打开浏览器访问 http://127.0.0.1:8188

---

## 三、安装 ComfyUI Manager（必装插件管理器）（已完成）

后续自定义节点和模型下载都依赖它，务必安装：

```powershell
cd D:\Program Files\AI\ComfyUI\custom_nodes
git clone git@github.com:Comfy-Org/ComfyUI-Manager.git comfyui-manager
```

重启 ComfyUI 后，界面右上角出现 **Manager** 按钮即成功。

> 📌 Manager 官方仓库：[git@github.com:Comfy-Org/ComfyUI-Manager.git](https://github.com/Comfy-Org/ComfyUI-Manager.git)
> 📌 若安装节点时提示 "security level" 错误：设置 → Server Config → Security Level 改为 **Normal** 后重启。

---

## 四、模型部署一：FLUX.2 [dev]（文生图主力）

FLUX.2 [dev] 是 Black Forest Labs 开源的 32B 参数模型，当前开源画质天花板。它由 **3 个独立文件**组成，需分别下载放置。

> 📌 **许可注意**：FLUX.2 [dev] 采用 FLUX Non-Commercial License，生成内容可个人/商用，但需先在 HuggingFace 页面登录并同意协议才能下载：https://huggingface.co/black-forest-labs/FLUX.2-dev
> ⚠️ **32GB 内存警告**：FLUX.2 dev 的文本编码器（Mistral 3）体积很大，运行时需部分卸载到内存。你的 32GB 内存属于"刚好够用"，运行时请关闭浏览器等占内存程序。若频繁内存不足，改用 GGUF Q4 版模型。

### 4.1 需要下载的文件（3 个）

| 文件 | 作用 | 放置目录 | 大小（FP8） |
|---|---|---|---|
| `flux2_dev_fp8mixed.safetensors` | 扩散主模型 | `ComfyUI\models\diffusion_models\` | ~20 GB |
| `mistral_3_small_flux2_fp8.safetensors` | 文本编码器 | `ComfyUI\models\text_encoders\` | ~12 GB |
| `flux2-vae.safetensors` | VAE 解码器 | `ComfyUI\models\vae\` | ~350 MB |

### 4.2 下载地址

**官方原版（BF16，需同意协议，文件巨大，不推荐你的内存配置）：**
- https://huggingface.co/black-forest-labs/FLUX.2-dev

**ComfyUI 官方优化 FP8 版（推荐 ✅）：**
- https://huggingface.co/Comfy-Org/flux2-dev
  - 在该仓库的 Files 中下载 `flux2_dev_fp8mixed.safetensors`、`mistral_3_small_flux2_fp8.safetensors`、`flux2-vae.safetensors`

**GGUF 量化版（内存不足时备用，Q4/Q6/Q8 可选）：**
- https://huggingface.co/city96/FLUX.2-dev-gguf
  - 使用 GGUF 需额外安装自定义节点：`git clone https://github.com/city96/ComfyUI-GGUF.git` 到 `custom_nodes`

**命令行下载方式（在激活 venv 后执行）：**

```powershell
pip install -U "huggingface_hub[cli]"
# 国内先执行：$env:HF_ENDPOINT = "https://hf-mirror.com"
hf download Comfy-Org/flux2-dev flux2_dev_fp8mixed.safetensors --local-dir D:\Program Files\AI\ComfyUI\models\diffusion_models
hf download Comfy-Org/flux2-dev mistral_3_small_flux2_fp8.safetensors --local-dir D:\Program Files\AI\ComfyUI\models\text_encoders
hf download Comfy-Org/flux2-dev flux2-vae.safetensors --local-dir D:\Program Files\AI\ComfyUI\models\vae
```

### 4.3 使用方法

ComfyUI 已原生支持 FLUX.2：菜单 → **Workflow → Browse Templates → Flux**，选择 FLUX.2 Dev 模板，在加载节点中分别选择上述三个文件即可。推荐采样参数：Steps 28~50，CFG 4.0，Sampler euler（无需负面提示词）。

---

## 五、模型部署二：SDXL（文生图 / LoRA 生态）

SDXL 的价值在于**海量 LoRA 和最完整的 ControlNet 生态**，单文件 checkpoint 即可用，最简单。

### 5.1 需要下载的文件

| 文件 | 放置目录 | 说明 |
|---|---|---|
| SDXL checkpoint（.safetensors） | `ComfyUI\models\checkpoints\` | 主模型，下 1~2 个即可 |
| `sdxl_vae.safetensors`（可选） | `ComfyUI\models\vae\` | 大多数 checkpoint 已内置 VAE |
| ControlNet / LoRA（按需） | `models\controlnet\` / `models\loras\` | 生态扩展 |

### 5.2 推荐 checkpoint 及下载地址

| 模型 | 定位 | HuggingFace 地址 |
|---|---|---|
| **sd_xl_base_1.0** | 官方基础模型（部分工作流必需） | https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0 |
| **Juggernaut XL** | 写实/照片级，全能首选 | https://huggingface.co/RunDiffusion/Juggernaut-XL-v9 |
| **Illustrious XL** | 动漫/插画（LoRA 生态最大） | https://huggingface.co/OnomaAIResearch/Illustrious-XL-v1.0 |

> LoRA 和更多微调模型推荐到 **Civitai**（https://civitai.com，需网络工具）筛选 "SDXL" 类别下载，放入 `models\loras\`。

### 5.3 使用方法

ComfyUI 默认模板就是 SDXL 文生图流程：`Load Checkpoint` 节点选择模型 → 输入提示词 → `Queue` 运行。LoRA 使用方式：在 checkpoint 与 CLIP 编码之间插入 `Load LoRA` 节点。

---

## 六、模型部署三：Bernini（视频生成）

Bernini 是字节跳动 2026 年开源的视频生成/编辑框架，底层基于 Wan 2.2 A14B，支持文生视频（T2V）、视频编辑（V2V）、参考图生视频（R2V/RV2V）、素材植入等任务。原生输出 480p / 16fps。

> 📌 官方代码库：https://github.com/bytedance/Bernini
> 📌 官方权重：https://huggingface.co/ByteDance/Bernini
> ⚠️ 官方完整版（含 MLLM 规划器）面向 H100 级多卡，**不建议本地部署**；你的 4090 请使用社区 ComfyUI 移植版 + FP8 权重。

### 6.1 安装 ComfyUI 节点（二选一，推荐方案 A）

**方案 A：ComfyUI-BerniniR（推荐 ✅，支持自动下载权重、专为 24GB 显存优化）**

```powershell
cd D:\Program Files\AI\ComfyUI\custom_nodes
git clone https://github.com/neuregex/ComfyUI-BerniniR.git
cd ComfyUI-BerniniR
..\..\venv\Scripts\python.exe -m pip install -r requirements.txt
```

> 仓库地址：https://github.com/neuregex/ComfyUI-BerniniR
> 特性：FP8 自包含权重包 ~40GB，实测 24GB 显存可跑 81 帧 480p 完整流程；节点自带断点续传下载。

**方案 B：ComfyUI-RH-Bernini（配合你已有的 Wan 2.2 工作流加载器使用）**

```powershell
cd D:\Program Files\AI\ComfyUI\custom_nodes
git clone https://github.com/RH-RunningHub/ComfyUI-RH-Bernini.git
```

> 仓库地址：https://github.com/RH-RunningHub/ComfyUI-RH-Bernini
> 注意：该方案不自动下载模型，需手动准备权重（见 6.2）。

### 6.2 下载权重

**方案 A（自动）**：重启 ComfyUI 后，使用 `BerniniR · Load Model` 节点，`source` 保持默认 `neuregex/Bernini-R-fp8 (auto)`，`auto_download` 开启，首次运行自动下载 ~40GB 到 `ComfyUI\models\bernini\`。

**方案 A（手动命令行，国内可加镜像）：**

```powershell
# 国内先执行：$env:HF_ENDPOINT = "https://hf-mirror.com"
hf download neuregex/Bernini-R-fp8 --local-dir D:\Program Files\AI\ComfyUI\models\bernini\Bernini-R-fp8
```

**方案 B 所需权重来源：**
- 官方权重：https://huggingface.co/ByteDance/Bernini （bf16 ~126GB，需自行量化，不推荐）
- Kijai FP8 权重（推荐 ✅）：https://huggingface.co/Kijai/WanVideo_comfy_fp8_scaled/tree/main/Bernini
- Wan 2.2 基础模型（VAE / UMT5 文本编码器）：https://huggingface.co/Wan-AI/Wan2.2-T2V-A14B-Diffusers

### 6.3 使用要点（24GB 显存）

- 首次建议 **480p / 81 帧（约 5 秒）** 起步测试
- 节点参数 `fp8` 保持开启；`offload_experts=True`（官方 MoE 高低噪声专家切换卸载）
- 若 OOM：开启 `blocks_to_swap=20~30`，或降低帧数/分辨率
- 输出 480p 建议后续接放大节点（如 SeedVR2 / 4x-UltraSharp）提升到 1080p

---

## 七、模型部署四：Index-TTS（语音合成）

IndexTTS-2 是 B 站开源的零样本声音克隆 TTS，支持情感控制与**时长精准控制**（视频配音对口型利器）。

> 📌 官方代码库：https://github.com/index-tts/index-tts
> 📌 模型权重：https://huggingface.co/IndexTeam/IndexTTS-2

### 7.1 安装 ComfyUI 节点（推荐 chenpipi0807 版，中文支持好、自带一键下载脚本）

```powershell
cd D:\Program Files\AI\ComfyUI\custom_nodes
git clone https://github.com/chenpipi0807/ComfyUI-Index-TTS.git
cd ComfyUI-Index-TTS
..\..\venv\Scripts\python.exe -m pip install -r requirements.txt
```

> 仓库地址：https://github.com/chenpipi0807/ComfyUI-Index-TTS
> 备选节点（轻量封装版）：https://github.com/snicolast/ComfyUI-IndexTTS2

### 7.2 Windows 专属：安装文本正则化依赖（重要！）

Windows 上 `pynini` 无法正常 pip 安装，会导致 TTS 文本正则化被阉割（数字、标点读错）。使用社区预编译轮子修复：

1. 到 https://github.com/billwuhao/pynini-windows-wheels/releases 下载与你 Python 版本匹配的 `pynini-2.1.6.post1-cp3xx-cp3xx-win_amd64.whl`
2. 依次执行：

```powershell
D:\Program Files\AI\ComfyUI\venv\Scripts\python.exe -m pip install 下载路径\pynini-2.1.6.post1-cp312-cp312-win_amd64.whl
D:\Program Files\AI\ComfyUI\venv\Scripts\python.exe -m pip install importlib_resources
D:\Program Files\AI\ComfyUI\venv\Scripts\python.exe -m pip install "WeTextProcessing>=1.0.4" --no-deps
```

### 7.3 下载模型权重

**方式一：节点自带一键脚本（推荐 ✅，支持国内镜像与断点续传）**

```powershell
D:\Program Files\AI\ComfyUI\venv\Scripts\python.exe D:\Program Files\AI\ComfyUI\custom_nodes\ComfyUI-Index-TTS\TTS2_download.py
# 按提示选择 2（国内镜像 hf-mirror.com）或 1（官方源）
```

**方式二：手动下载**

```powershell
# HuggingFace：
hf download IndexTeam/IndexTTS-2 --local-dir D:\Program Files\AI\ComfyUI\models\IndexTTS-2

# ModelScope（国内推荐）：
modelscope download --model IndexTeam/IndexTTS-2 --local_dir D:\Program Files\AI\ComfyUI\models\IndexTTS-2
```

模型文件放置于 `ComfyUI\models\IndexTTS-2\`（或节点 README 指定的 `checkpoints/` 目录），缺失文件节点首次运行时也会自动从 HF 缓存补齐。

### 7.4 使用方法

工作流中最简链路：`Load Audio`（参考音色音频，3~10 秒清晰人声）→ `IndexTTS2 Simple`（输入要朗读的文本）→ `Save Audio`。进阶可用 `IndexTTS2 Emotion Vector`（8 维情绪滑杆）或情感参考音频控制语气。

---

## 八、目录结构总览与空间预算

### 8.1 最终目录结构

```
D:\Program Files\AI\ComfyUI\
├── main.py                     ← 启动入口
├── venv\                       ← Python 虚拟环境
├── custom_nodes\
│   ├── comfyui-manager\        ← Manager（必装）
│   ├── ComfyUI-BerniniR\       ← Bernini 视频节点
│   └── ComfyUI-Index-TTS\      ← Index-TTS 语音节点
├── models\
│   ├── diffusion_models\       ← flux2_dev_fp8mixed.safetensors（~20GB）
│   ├── text_encoders\          ← mistral_3_small_flux2_fp8.safetensors（~12GB）
│   ├── vae\                    ← flux2-vae.safetensors / sdxl_vae
│   ├── checkpoints\            ← SDXL 系列（每个 ~6.9GB）
│   ├── bernini\                ← Bernini-R FP8 权重包（~40GB）
│   ├── IndexTTS-2\             ← IndexTTS-2 权重（~5GB）
│   ├── loras\                  ← SDXL LoRA（按需）
│   └── controlnet\             ← SDXL ControlNet（按需）
├── output\                     ← 生成结果输出
└── input\                      ← 参考图/参考音频输入
```

### 8.2 磁盘空间预算

| 项目 | 占用 |
|---|---|
| ComfyUI 本体 + venv + PyTorch | ~15 GB |
| FLUX.2 dev（FP8 三件套） | ~33 GB |
| SDXL（2 个 checkpoint） | ~14 GB |
| Bernini-R（FP8 权重包） | ~40 GB |
| IndexTTS-2 | ~5 GB |
| LoRA / ControlNet / 输出缓存（预留） | ~100 GB |
| **合计（建议预留）** | **≥ 250 GB** |

你的 6TB 硬盘非常充裕。建议将 `models\` 放在 **SSD 分区**以加快模型加载（每次加载速度差 5~10 倍）。

---

## 九、启动参数与性能优化建议

### 9.1 推荐启动命令

新建 `start.bat`（放在 `D:\Program Files\AI\ComfyUI 下），内容：

### 9.2 针对 32GB 内存的注意事项

- **FLUX.2 dev 与 Bernini 不要同时加载跑图**：两者都会大量占用内存做模型卸载，建议分开使用
- 运行 FLUX.2 dev 时关闭 Chrome 等内存大户
- 若内存频繁爆满：FLUX.2 换 GGUF Q4 版（city96/FLUX.2-dev-gguf），Bernini 开启 `blocks_to_swap=30`
- 中长期建议：有条件可将内存升级到 64GB，体验会宽松很多

### 9.3 可选性能增强

- **SageAttention**（注意力加速，4090 可提速 20%~40%）：Windows 安装较折腾，建议通过 Manager 安装 `KJNodes`（https://github.com/kijai/ComfyUI-KJNodes），用 `PatchSageAttentionKJ` 节点按工作流局部启用，比全局 `--use-sage-attention` 更安全
- **ComfyUI-Crystools**：实时显存/内存监控条，Manager 内搜索安装，方便观察资源瓶颈
- 定期在 Manager 中执行 **Update All** 保持本体与节点为最新

---

## 十、常见问题排查

| 问题 | 排查方向 |
|---|---|
| `torch.cuda.is_available()` 返回 False | PyTorch 装错版本，重装 cu128 版；检查 `nvidia-smi` 驱动 |
| 节点出现 "import failed" | 未激活 venv 装的依赖 / 装完节点没完全重启 ComfyUI（任务管理器确认无残留 python.exe） |
| Manager 提示 security level 错误 | 设置 → Server Config → Security Level 改为 Normal |
| HuggingFace 下载卡住/超时 | 设置 `$env:HF_ENDPOINT = "https://hf-mirror.com"` 后重试；或改用 ModelScope |
| FLUX.2 出图全黑/花屏 | 文本编码器与 VAE 搭配错误，确认三个文件都来自同一版本源 |
| 视频生成 OOM | 降分辨率/帧数；开启 fp8 + blocks_to_swap；确认无其他程序占显存 |
| Index-TTS 数字/英文读错 | pynini 文本正则化没装上，回 7.2 节安装 Windows 轮子 |
| Git 命令不识别 | Git 未装或未重启终端 |

---

## 十一、资源链接汇总

### 软件与框架

| 名称 | 地址 |
|---|---|
| ComfyUI 主仓库 | https://github.com/comfyanonymous/ComfyUI |
| ComfyUI Manager | https://github.com/Comfy-Org/ComfyUI-Manager.git |
| PyTorch (cu128) | https://download.pytorch.org/whl/cu128 |

### 模型权重

| 模型 | HuggingFace | 备注 |
|---|---|---|
| FLUX.2 [dev] 官方 | https://huggingface.co/black-forest-labs/FLUX.2-dev | 需同意协议 |
| FLUX.2 dev FP8（推荐） | https://huggingface.co/Comfy-Org/flux2-dev | ComfyUI 优化版 |
| FLUX.2 dev GGUF | https://huggingface.co/city96/FLUX.2-dev-gguf | 低内存备用 |
| SDXL Base 1.0 | https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0 | 官方基础模型 |
| Juggernaut XL | https://huggingface.co/RunDiffusion/Juggernaut-XL-v9 | 写实首选 |
| Illustrious XL | https://huggingface.co/OnomaAIResearch/Illustrious-XL-v1.0 | 动漫首选 |
| Bernini 官方权重 | https://huggingface.co/ByteDance/Bernini | bf16 原版 |
| Bernini-R FP8（推荐） | https://huggingface.co/neuregex/Bernini-R-fp8 | 24GB 可跑 |
| Bernini Kijai FP8 | https://huggingface.co/Kijai/WanVideo_comfy_fp8_scaled/tree/main/Bernini | 备选 |
| Wan 2.2 基础模型 | https://huggingface.co/Wan-AI/Wan2.2-T2V-A14B-Diffusers | VAE/编码器 |
| IndexTTS-2 | https://huggingface.co/IndexTeam/IndexTTS-2 | 声音克隆 |

### 自定义节点

| 节点 | GitHub 地址 |
|---|---|
| ComfyUI-BerniniR | https://github.com/neuregex/ComfyUI-BerniniR |
| ComfyUI-RH-Bernini（备选） | https://github.com/RH-RunningHub/ComfyUI-RH-Bernini |
| ComfyUI-Index-TTS | https://github.com/chenpipi0807/ComfyUI-Index-TTS |
| ComfyUI-IndexTTS2（备选） | https://github.com/snicolast/ComfyUI-IndexTTS2 |
| ComfyUI-GGUF | https://github.com/city96/ComfyUI-GGUF |
| KJNodes（性能补丁） | https://github.com/kijai/ComfyUI-KJNodes |
| pynini Windows 轮子 | https://github.com/billwuhao/pynini-windows-wheels |

### 模型项目主页

| 项目 | 地址 |
|---|---|
| Bernini 官方仓库 | https://github.com/bytedance/Bernini |
| Index-TTS 官方仓库 | https://github.com/index-tts/index-tts |
| Civitai（LoRA 社区） | https://civitai.com |
| ModelScope（国内模型源） | https://modelscope.cn |

---

> ✅ **部署完成检查清单**
> - [ ] `python main.py` 启动无报错，http://127.0.0.1:8188 可访问
> - [ ] Manager 按钮可见
> - [ ] FLUX.2 模板工作流出图成功
> - [ ] SDXL 默认工作流出图成功
> - [ ] Bernini 生成 480p 测试视频成功
> - [ ] Index-TTS 克隆一段参考音频成功
>
> 全部勾选即部署完成，祝玩得愉快 🎉
