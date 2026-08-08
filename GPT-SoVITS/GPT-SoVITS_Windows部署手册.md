# GPT-SoVITS Windows 11 部署手册

> **适用环境：** Windows 11  
> **目标路径：** `D:\Program Files\AI\GPT-SoVITS`  
> **硬件配置：** RTX 4090 24G / AMD 9900X3D / 32G RAM / 6T SSD  
> **文档版本：** v1.1（基于 GPT-SoVITS 官方 main 分支，2026年8月）  
> **更新记录：** 2026-08-05 新增增强版启动脚本、附录 A（PowerShell 编码问题）  
> **官方仓库：** https://github.com/RVC-Boss/GPT-SoVITS

---

## ⚠️ 前置重要说明

### Python 3.13 兼容性警告

**你当前安装的 Python 3.13 不在 GPT-SoVITS 官方测试支持范围内。**

官方已验证的环境如下：

| Python 版本 | PyTorch 版本 | CUDA 版本 |
|------------|-------------|----------|
| Python 3.10 | PyTorch 2.5.1 | CUDA 12.4 |
| Python 3.11 | PyTorch 2.5.1 | CUDA 12.4 |
| **Python 3.11** | **PyTorch 2.7.0** | **CUDA 12.8** ⭐ |
| Python 3.9 | PyTorch 2.8.0dev | CUDA 12.8 |

> **原因：** GPT-SoVITS 依赖大量底层库（如 `numba`、`onnxruntime-gpu`、`gradio`、`transformers` 等），这些库对 Python 3.13 的支持尚不成熟，强行使用会导致安装失败或运行时崩溃。

**因此，本手册采用「Miniconda 创建独立 Python 3.11 环境」的方案，与你已有的 Python 3.13 互不冲突。**

---

## 一、环境准备

### 1.1 安装 Miniconda

Miniconda 用于创建隔离的 Python 环境，不影响系统已有的 Python 3.13。

**下载地址：** https://docs.conda.io/en/latest/miniconda.html

**Windows 推荐下载：** `Miniconda3-latest-Windows-x86_64.exe`

**安装步骤：**
1. 运行安装程序
2. **安装路径建议：** `C:\Users\jacky\miniconda3`（或默认路径）
3. ✅ **勾选** "Add Miniconda3 to my PATH environment variable"（添加到环境变量）
4. 其余保持默认，完成安装

**验证安装：**
```powershell
conda --version
```
应显示类似 `conda 24.x.x`

### 1.2 配置国内镜像（可选，加速下载）

如果你在国内，建议配置镜像源：

```powershell
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
conda config --set show_channel_urls yes
```

### 1.3 安装 Git for Windows

**下载地址：** https://git-scm.com/download/win

安装时保持默认选项即可，确保勾选 "Git from the command line and also from 3rd-party software"。

**验证安装：**
```powershell
git --version
```

---

## 二、创建 Python 3.11 虚拟环境

### 2.1 创建并激活 Conda 环境

打开 **PowerShell**（建议以管理员身份运行），执行：

```powershell
# 创建环境（指定 Python 3.11）
conda create -n GPTSoVits python=3.11 -y

# 激活环境
conda activate GPTSoVits
```

> 激活成功后，命令提示符前会出现 `(GPTSoVits)` 前缀。

### 2.2 验证 Python 版本

```powershell
python --version
```
应显示 `Python 3.11.x`

---

## 三、克隆 GPT-SoVITS 仓库

### 3.1 创建部署目录并克隆代码

```powershell
# 创建部署目录
mkdir "D:\Program Files\AI\GPT-SoVITS"

# 进入目录
cd "D:\Program Files\AI\GPT-SoVITS"

# 克隆仓库
git clone https://github.com/RVC-Boss/GPT-SoVITS.git .
```

> 如果 GitHub 访问较慢，可使用镜像：
> ```powershell
> git clone https://gh-proxy.com/https://github.com/RVC-Boss/GPT-SoVITS.git .
> ```

### 3.2 验证文件结构

克隆完成后，目录结构应包含：
```
D:\Program Files\AI\GPT-SoVITS
├── GPT_SoVITS\              # 核心代码
├── tools\                    # 工具脚本（UVR5、ASR 等）
├── docs\                     # 文档
├── webui.py                  # WebUI 入口
├── api.py / api_v2.py        # API 接口
├── install.ps1               # Windows 安装脚本
├── requirements.txt          # Python 依赖
├── extra-req.txt             # 额外依赖
├── go-webui.bat              # 一键启动脚本
└── go-webui.ps1              # PowerShell 启动脚本
```

---

## 四、安装依赖

### 4.1 安装系统级依赖（FFmpeg + CMake）

在 **已激活的 Conda 环境** 中执行：

```powershell
conda install ffmpeg cmake -c conda-forge -y
```

**验证 FFmpeg：**
```powershell
ffmpeg -version
```

### 4.2 安装 PyTorch（CUDA 12.8 版本）

由于你的显卡是 RTX 4090，且已配置 CUDA 12.8，安装对应版本的 PyTorch：

```powershell
# 第 1 步：先装 torch + torchaudio（CUDA 12.8 版本）
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu128

# 第 2 步：再单独装 torchcodec（从默认 PyPI 源装，它是 CPU-only 的）
pip install torchcodec
```

**验证 PyTorch + CUDA：**
```powershell
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA可用: {torch.cuda.is_available()}'); print(f'CUDA版本: {torch.version.cuda}'); print(f'GPU: {torch.cuda.get_device_name(0)}')"
```

预期输出：
```
PyTorch: 2.7.0+cu128
CUDA可用: True
CUDA版本: 12.8
GPU: NVIDIA GeForce RTX 4090
```

### 4.3 安装 Python 依赖包

继续在同一环境中执行：

```powershell
# 先安装 extra-req.txt（faster-whisper，不加依赖）
pip install -r extra-req.txt --no-deps

# 再安装主依赖
pip install -r requirements.txt
```

> 如果安装过程中出现 `jieba_fast` 编译失败，可跳过它（`jieba` 已包含在依赖中，功能相同但纯 Python 实现稍慢）。
>
> ```powershell
> pip install -r requirements.txt --no-deps
> pip install jieba  # 手动安装替代
> ```

---

## 五、下载预训练模型

预训练模型是 GPT-SoVITS 运行的必要条件。以下提供 **脚本自动下载** 和 **手动下载** 两种方式。

### 方案 A：使用官方 install.ps1 脚本自动下载（推荐）

在 **已激活的 Conda 环境** 中，进入项目目录执行：

```powershell
cd "D:\Program Files\AI\GPT-SoVITS"

# 使用官方脚本下载模型（HF-Mirror 适合国内，HF 适合海外）
pwsh -F install.ps1 --Device CU128 --Source HF-Mirror --DownloadUVR5
```

参数说明：
| 参数 | 说明 |
|-----|------|
| `--Device CU128` | 你的 CUDA 版本是 12.8 |
| `--Source HF` | 从 HuggingFace 下载 |
| `--Source HF-Mirror` | 从 HuggingFace 镜像站下载（国内推荐） |
| `--Source ModelScope` | 从魔搭社区下载（国内备用） |
| `--DownloadUVR5` | 同时下载 UVR5 人声分离模型（可选但推荐） |

> ⚠️ **注意：** 由于 install.ps1 会重新安装 PyTorch，如果第 4.2 步已成功安装，可跳过 PyTorch 安装步骤，或选择手动下载模型（方案 B）。

### 方案 B：手动下载模型（更可控）

#### 5.1 主预训练模型（必下）

**下载地址：** https://huggingface.co/lj1995/GPT-SoVITS

将以下文件放入 `GPT_SoVITS\pretrained_models\` 目录：

| 模型文件 | 说明 | 目标路径 |
|---------|------|---------|
| `s1bert.ckpt` | GPT 模型 (V1/V2) | `GPT_SoVITS\pretrained_models\` |
| `s2G.pth` | SoVITS 生成器 (V1/V2) | `GPT_SoVITS\pretrained_models\` |
| `s2D.pth` | SoVITS 判别器 (V1/V2) | `GPT_SoVITS\pretrained_models\` |
| `chinese-hubert-base` 文件夹 | 中文 HuBERT 特征提取 | `GPT_SoVITS\pretrained_models\` |
| `chinese-roberta-wwm-ext-large` 文件夹 | 中文文本编码 | `GPT_SoVITS\pretrained_models\` |

**V2 版本额外模型**（推荐下载，性能更好）：

从 https://huggingface.co/lj1995/GPT-SoVITS/tree/main/gsv-v2final-pretrained 下载：

| 模型文件 | 目标路径 |
|---------|---------|
| `s1v2.ckpt` | `GPT_SoVITS\pretrained_models\gsv-v2final-pretrained\` |
| `s2Gv2.pth` | `GPT_SoVITS\pretrained_models\gsv-v2final-pretrained\` |
| `s2Dv2.pth` | `GPT_SoVITS\pretrained_models\gsv-v2final-pretrained\` |

**V3 版本模型**（如需使用 V3）：

从 https://huggingface.co/lj1995/GPT-SoVITS/tree/main 下载：
- `s1v3.ckpt`
- `s2Gv3.pth`
- `s2Dv3.pth`
- `models--nvidia--bigvgan_v2_24khz_100band_256x` 文件夹

放入 `GPT_SoVITS\pretrained_models\`

**V4 版本模型**（修复 V3 金属音问题，推荐）：

- `gsv-v4-pretrained/s2v4.pth`
- `gsv-v4-pretrained/vocoder.pth`

放入 `GPT_SoVITS\pretrained_models\`

**V2Pro 版本模型**（性能优于 V4，速度同 V2）：

- `v2Pro/s2Dv2Pro.pth`
- `v2Pro/s2Gv2Pro.pth`
- `v2Pro/s2Dv2ProPlus.pth`
- `v2Pro/s2Gv2ProPlus.pth`
- `sv/pretrained_eres2netv2w24s4ep4.ckpt`

放入 `GPT_SoVITS\pretrained_models\`

#### 5.2 G2PW 模型（中文 TTS 必需）

**下载地址：**
- HuggingFace: https://huggingface.co/XXXXRT/GPT-SoVITS-Pretrained/resolve/main/G2PWModel.zip
- ModelScope: https://www.modelscope.cn/models/XXXXRT/GPT-SoVITS-Pretrained/resolve/master/G2PWModel.zip

**步骤：**
1. 下载 `G2PWModel.zip`
2. 解压并重命名为 `G2PWModel`
3. 放入 `GPT_SoVITS\text\G2PWModel\`

#### 5.3 UVR5 模型（人声分离，可选但推荐）

**下载地址：** https://huggingface.co/lj1995/VoiceConversionWebUI/tree/main/uvr5_weights

将模型文件放入 `tools\uvr5\uvr5_weights\`

#### 5.4 NLTK 数据

**下载地址：** https://huggingface.co/XXXXRT/GPT-SoVITS-Pretrained/resolve/main/nltk_data.zip

**步骤：**
1. 下载 `nltk_data.zip`
2. 解压到 Python 环境目录（可通过 `python -c "import sys; print(sys.prefix)"` 查看路径）

#### 5.5 OpenJTalk 字典（日语支持）

**下载地址：** https://huggingface.co/XXXXRT/GPT-SoVITS-Pretrained/resolve/main/open_jtalk_dic_utf_8-1.11.tar.gz

**步骤：**
```powershell
# 在 Conda 环境中执行
python -c "import os, pyopenjtalk; print(os.path.dirname(pyopenjtalk.__file__))"
# 将 tar.gz 解压到输出的目录中
```

#### 5.6 ASR 模型（可选，自动下载）

FunASR、SenseVoice 等模型会在首次使用时自动下载。如需离线使用，可手动下载到 `tools\asr\models\`。

---

## 六、安装 VC++ 运行库

如果系统未安装，需下载 **Visual C++ Redistributable**：

**下载地址：** https://aka.ms/vs/17/release/vc_redist.x64.exe

> 注意：官方文档写 x86，但你的系统是 64 位，应下载 **x64** 版本。

下载后双击安装即可。

---

## 七、启动 GPT-SoVITS

### 7.1 方式一：命令行启动（推荐）

打开 PowerShell，确保激活 Conda 环境：

```powershell
conda activate GPTSoVits
cd "D:\Program Files\AI\GPT-SoVITS"

# 启动 WebUI（中文界面）
python webui.py zh_CN

# 或使用默认语言
python webui.py
```

启动成功后，浏览器会自动打开 `http://127.0.0.1:9874`

### 7.2 方式二：创建快捷启动脚本

在项目根目录创建 `start-gpt-sovits.ps1`：

```powershell
# start-gpt-sovits.ps1
$ErrorActionPreference = "Stop"
chcp 65001 | Out-Null

# 激活 Conda 环境
& conda activate GPTSoVits

# 进入项目目录
Set-Location "D:\Program Files\AI\GPT-SoVITS"

# 启动 WebUI
python webui.py zh_CN

Write-Host "`n按任意键退出..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
```

以后双击运行此脚本即可启动。

### 7.3 方式三：增强版快速启动脚本（推荐）

> **⚠️ 血泪教训：** 本脚本在开发过程中遇到了 Windows PowerShell 中文编码的坑，详见下方「附录 A」。如果你在 Windows 上编写或修改 PowerShell 脚本，强烈建议阅读。

项目根目录已提供 **`start-gpt-sovits.bat`**（双击入口）和 **`start-gpt-sovits.ps1`**（核心脚本），功能如下：

| 功能 | 说明 |
|------|------|
| 📍 **自动定位项目目录** | 通过脚本所在路径自动确定项目根目录，不依赖固定路径 |
| 🔪 **进程检测与清理** | 启动前自动查找并结束已有的 GPT-SoVITS 进程，避免端口冲突 |
| 🐍 **自动激活 Conda 环境** | 初始化 Conda Hook 并激活 `GPTSoVits` 环境 |
| 🌐 **自动打开浏览器** | 启动后约 10 秒自动在浏览器打开 WebUI 地址 |
| 🛡️ **全局错误捕获** | 任何崩溃都会显示错误信息并暂停窗口，不再闪退 |
| 🔧 **参数化启动** | 支持 `-Version`、`-Language`、`-NoKill`、`-SkipCheck` 等参数 |

**使用方法：**

```powershell
# 方式 1：双击 start-gpt-sovits.bat（最方便）

# 方式 2：命令行运行（支持参数）
.\start-gpt-sovits.ps1                    # 默认：V2Pro + 中文
.\start-gpt-sovits.ps1 -Version v2Pro     # 显式指定版本
.\start-gpt-sovits.ps1 -Language en       # 切换英文界面
.\start-gpt-sovits.ps1 -NoKill            # 跳过进程检测
.\start-gpt-sovits.ps1 -SkipCheck         # 跳过环境检查，直接启动
```

**脚本核心逻辑：**

```powershell
# 1. 自动结束已有进程（避免 9874 端口冲突）
Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
    Where-Object { $_.CommandLine -match 'webui\.py|api.*\.py' } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force }

# 2. 激活 Conda 环境
$hook = (& conda shell.powershell hook) | Out-String
Invoke-Expression $hook
conda activate GPTSoVits

# 3. 设置环境变量（与官方启动脚本保持一致）
$env:TEMP      = "$ScriptDir\TEMP"
$env:no_proxy  = 'localhost, 127.0.0.1, ::1'
$env:PATH      = "$ScriptDir\runtime;$env:PATH"

# 4. 自动打开浏览器（后台延迟 10 秒）
Start-Job { Start-Sleep 10; Start-Process 'http://127.0.0.1:9874' }

# 5. 启动主程序
python webui.py zh_CN
```

---

### 7.4 启动参数说明

```bash
# 启动 V2 版本（默认）
python webui.py zh_CN

# 启动 V1 版本
python webui.py v1 zh_CN

# 启动 API 服务
python api.py

# 启动 API v2
python api_v2.py
```

---

## 八、功能验证

### 8.1 验证 GPU 是否正常工作

启动 WebUI 后，查看控制台输出是否包含：
```
Using GPU: NVIDIA GeForce RTX 4090
Half precision: True
```

### 8.2 快速测试语音合成

1. 打开 WebUI → **1-GPT-SoVITS-TTS** → **1C-推理**
2. 上传一段 5 秒以上的参考音频（wav 格式，16kHz 或更高）
3. 输入参考音频的文本
4. 在"需要合成的文本"框输入要合成的内容
5. 点击"合成语音"
6. 如果能正常输出音频，则部署成功！

### 8.3 检查 CUDA 占用

合成语音时，打开另一个终端运行：
```powershell
nvidia-smi
```
应能看到 `python.exe` 进程占用了显存（通常 4-8GB）。

---

## 九、模型训练快速入门

### 9.1 准备训练数据

**数据集格式要求：**
- 音频格式：WAV，单声道，采样率 22050Hz 或更高
- 音频时长：每条 3-15 秒
- 音频质量：清晰、无背景音乐、无混响
- 总时长：最少 1 分钟（推荐 5-30 分钟）

**标注文件格式（.list）：**
```
vocal_path|speaker_name|language|text
```

示例：
```
D:\GPT-SoVITS\dataset\audio_001.wav|speaker1|zh|你好，这是一段测试语音。
D:\GPT-SoVITS\dataset\audio_002.wav|speaker1|zh|今天天气真不错。
```

语言代码：
| 代码 | 语言 |
|-----|------|
| zh | 中文 |
| ja | 日语 |
| en | 英语 |
| ko | 韩语 |
| yue | 粤语 |

### 9.2 使用 WebUI 进行训练

1. **音频切片**：WebUI → **0-前置数据集获取工具** → **0a-UVR5人声伴奏分离&去混响**（如有背景音）
2. **ASR 识别**：WebUI → **0b-语音切割** → 切割音频 → **0c-中文批量ASR**
3. **校对标注**：打开生成的 `.list` 文件，检查文本识别是否正确
4. **微调训练**：WebUI → **1-GPT-SoVITS-TTS** → **1A-数据集格式化** → **1B-微调训练**
5. **推理**：训练完成后，进入 **1C-推理**，选择训练好的模型进行语音合成

---

## 十、常见问题排查

### Q1: `CondaToSNonInteractiveError: Terms of Service have not been accepted`

**现象：** 创建环境时出现此错误，提示需要接受渠道服务条款。

**解决：** 方式一（推荐）——直接接受 ToS：
```powershell
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/msys2
```

方式二——改用免费社区渠道：
```powershell
conda config --remove channels defaults
conda config --add channels conda-forge
conda config --set channel_priority strict
```

### Q2: 提示 "No module named 'xxx'"

**解决：** 确保在 Conda 环境中安装依赖
```powershell
conda activate GPTSoVits
pip install xxx
```

### Q3: `pyopenjtalk` 编译失败：`nmake` 或 `CMAKE_C_COMPILER not set`

**现象：** 安装 `requirements.txt` 时提示 `Failed to build 'pyopenjtalk'`、`nmake` 找不到、或 `CMAKE_C_COMPILER not set`。

**原因：** `pyopenjtalk` 需要从源码编译 C++ 扩展，但 Windows 缺少 C/C++ 编译器（MSVC）。

**解决：** 安装 Visual Studio Build Tools（推荐，一劳永逸）：

1. 下载：https://aka.ms/vs/17/release/vs_BuildTools.exe
2. 运行安装器，勾选 **"使用 C++ 的桌面开发"**
3. 在右侧详情中确保勾选：
   - **MSVC v143 - VS 2022 C++ x64/x86 生成工具**
   - **Windows 11 SDK**（或 Windows 10 SDK）
4. 点击安装（约 6-10GB）
5. **重启 PowerShell**，重新激活 Conda 环境后再次执行 `pip install`

> 如暂时不需要日语 TTS，也可直接从 `requirements.txt` 中删除 `pyopenjtalk>=0.4.1` 这一行，跳过安装。

### Q4: CUDA out of memory（显存不足）

**解决：** RTX 4090 24G 通常足够，但如果 batch size 设置过大：
- 在 WebUI 的训练参数中减小 batch size
- 或修改 `config.py` 中的 `is_half = True`（半精度，节省显存）

### Q5: 模型下载慢或失败

**解决：** 使用镜像源
- 在 `install.ps1` 中使用 `--Source HF-Mirror` 或 `--Source ModelScope`
- 或手动使用迅雷等工具下载后放入对应目录

### Q6: 启动时报 "FFmpeg not found"

**解决：**
```powershell
conda activate GPTSoVits
conda install ffmpeg -c conda-forge -y
```

### Q7: 提示 "无法加载 DLL" 或 "找不到指定模块"

**解决：** 安装 VC++ 运行库（见第六章）

### Q8: 合成语音有电流声/金属音

**解决：** 尝试使用 V4 或 V2Pro 模型，或检查参考音频质量

### Q9: 如何切换 V1/V2/V3/V4/V2Pro 版本？

**解决：**
- 启动时加参数：`python webui.py v1` 或 `python webui.py`
- 或在 WebUI 界面中手动切换版本
- 确保已下载对应版本的预训练模型

---

## 附录 A：PowerShell 脚本编码问题（血泪教训）

> **记录时间：** 2026-08-05  
> **问题性质：** Windows PowerShell 中文编码兼容性陷阱  
> **影响范围：** 所有在 Windows 上编写含中文注释/字符串的 PowerShell 脚本

### A.1 现象

双击 `start-gpt-sovits.bat` 后，黑色控制台窗口**一闪而过**，随后访问 `http://localhost:9874/` 发现 GPT-SoVITS 并未运行。

直接运行 PowerShell 脚本时，报错信息如下（注意中文乱码）：

```
所在位置 行:17 字符: 19
+     [ValidateSet("v1", "v2", "v3", "v4", "v2Pro", "v2ProPlus", "")]
+                   ~
表达式中缺少右")"。

所在位置 行:27 字符: 31
+     [Parameter(HelpMessage = "璺宠繃鐜妫€鏌ワ紝鐩存帴鍚姩銆?)]
+                               ~
表达式或语句中包含意外的标记"璺宠繃鐜妫€鏌ワ紝鐩存帴鍚姩銆?"
```

### A.2 根本原因

**Windows PowerShell 的编码自动检测机制存在缺陷：**

1. **写入端：** 使用某些编辑器/工具写入 `.ps1` 文件时，默认使用 **UTF-8 无 BOM** 格式
2. **读取端：** Windows PowerShell 默认以系统编码（中文 Windows 为 **GBK / CodePage 936**）打开脚本文件
3. **冲突：** 无 BOM 的 UTF-8 中文内容被 GBK 解码，导致乱码 → `param()` 块语法解析失败 → 脚本崩溃 → 窗口闪退

### A.3 为什么 `go-webui.ps1` 没有这个问题？

对比官方提供的 `go-webui.ps1`，发现它**不含任何中文字符**，全部是 ASCII 字符，因此不受编码问题影响。这进一步验证了问题的根因。

### A.4 解决方案

**方案 1：使用 UTF-8 BOM 编码（推荐）**

在保存 `.ps1` 文件时，显式使用 **UTF-8 with BOM**（即 `utf-8-sig`）编码。文件头会多出 3 个字节（`EF BB BF`），PowerShell 检测到 BOM 后会正确按 UTF-8 解析。

```python
# Python 示例
with open('script.ps1', 'w', encoding='utf-8-sig') as f:
    f.write(content)
```

```powershell
# PowerShell 示例
$content | Set-Content -Path 'script.ps1' -Encoding UTF8BOM
```

**方案 2：避免在脚本中使用中文**

将 HelpMessage、注释等全部改为英文，从根本上规避编码问题（如当前 `start-gpt-sovits.ps1` 的做法）。

**方案 3：修改系统默认编码（不推荐）**

```powershell
# 在脚本开头强制设置编码（对脚本解析本身无效，仅影响运行时输出）
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001 | Out-Null
```

> ⚠️ **注意：** 上述命令只能影响脚本**运行后**的输出编码，无法修复脚本**解析阶段**的编码问题。解析阶段的编码由文件格式决定。

### A.5 验证方法

**检查文件是否带 BOM：**

```powershell
# 查看文件前 3 个字节（BOM = EF BB BF）
$bytes = Get-Content -Path 'script.ps1' -Encoding Byte -TotalCount 3
$bytes | ForEach-Object { "0x{0:X2}" -f $_ }
# 正确输出: 0xEF 0xBB 0xBF
```

**PowerShell 语法检查：**

```powershell
$content = Get-Content -Path 'script.ps1' -Encoding UTF8 -Raw
$errors = @()
[void][System.Management.Automation.PSParser]::Tokenize($content, [ref]$errors)
if ($errors.Count -eq 0) { "Syntax OK" } else { $errors }
```

### A.6 经验总结

| 场景 | 建议 |
|------|------|
| 编写供他人使用的 PowerShell 脚本 | **必须使用 UTF-8 BOM**，或完全使用英文 |
| 脚本需包含中文输出 | 文件用 BOM，运行时再加 `chcp 65001` |
| 双击运行的 `.bat` 调用 `.ps1` | `.bat` 里加 `chcp 65001`，`.ps1` 文件用 BOM |
| 调试脚本时窗口闪退 | 先在命令行运行看错误信息，大概率是编码问题 |

---

## 十一、目录结构速查

```
D:\Program Files\AI\GPT-SoVITS
├── GPT_SoVITS\                      # 核心代码
│   ├── pretrained_models\            # 预训练模型
│   │   ├── s1bert.ckpt
│   │   ├── s2G.pth
│   │   ├── s2D.pth
│   │   ├── chinese-hubert-base\      # HuBERT 模型
│   │   ├── chinese-roberta-wwm-ext-large\  # RoBERTa 模型
│   │   ├── gsv-v2final-pretrained\   # V2 模型
│   │   ├── gsv-v4-pretrained\        # V4 模型
│   │   └── v2Pro\                    # V2Pro 模型
│   ├── text\                         # 文本处理
│   │   └── G2PWModel\                # G2PW 模型（中文必需）
│   └── inference_webui.py            # 推理入口
├── tools\                            # 工具脚本
│   ├── uvr5\                         # 人声分离
│   │   └── uvr5_weights\             # UVR5 模型
│   ├── asr\                          # 语音识别
│   │   └── models\                   # ASR 模型
│   └── ...
├── docs\                             # 文档
├── webui.py                          # 主入口
├── api.py / api_v2.py                # API 接口
├── requirements.txt                  # 依赖列表
├── extra-req.txt                     # 额外依赖
├── go-webui.bat                      # 批处理启动（官方）
├── go-webui.ps1                      # PowerShell 启动（官方）
├── start-gpt-sovits.bat              # 增强版启动入口（推荐）
├── start-gpt-sovits.ps1              # 增强版启动脚本（推荐）
└── config.py                         # 配置文件
```

---

## 十二、版本对照表

| 版本 | 特点 | 适用场景 |
|-----|------|---------|
| **V1** | 早期版本，稳定 | 基础语音合成 |
| **V2** | 支持多语言，2k→5k小时预训练 | 通用场景，推荐入门 |
| **V3** | 音色相似度更高，情感更丰富 | 高质量克隆 |
| **V4** | 修复 V3 金属音，原生 48k 输出 | 替代 V3 |
| **V2Pro** | 性能超越 V4，速度同 V2 | **最推荐** |

> **作者建议：** V2Pro 是作者目前最推荐的版本，兼顾质量和速度。

---

## 十三、更新 GPT-SoVITS

当官方发布更新时：

```powershell
conda activate GPTSoVits
cd "D:\Program Files\AI\GPT-SoVITS"

# 拉取最新代码
git pull

# 更新依赖
pip install -r requirements.txt --upgrade

# 如有新模型，按需下载
```

---

## 十四、相关资源

| 资源 | 链接 |
|-----|------|
| 官方仓库 | https://github.com/RVC-Boss/GPT-SoVITS |
| 中文使用文档 | https://www.yuque.com/baicaigongchang1145haoyuangong/ib3g1e |
| 预训练模型 | https://huggingface.co/lj1995/GPT-SoVITS |
| HuggingFace 镜像 | https://hf-mirror.com |
| 魔搭社区 | https://www.modelscope.cn |
| 在线体验 | https://lj1995-gpt-sovits-proplus.hf.space |

---

## 十五、你的主机配置评估

| 配置项 | 你的配置 | 评价 |
|-------|---------|------|
| GPU | RTX 4090 24G | ⭐⭐⭐ 顶级，训练/推理速度极快 |
| CPU | AMD 9900X3D | ⭐⭐⭐ 顶级，数据预处理很快 |
| 内存 | 32G | ⭐⭐⭐ 充足 |
| 硬盘 | 6T SSD | ⭐⭐⭐ 大量模型存储空间 |
| CUDA | 12.8 | ⭐⭐⭐ 最新，完美匹配 |

**结论：** 你的配置完全可以流畅运行 GPT-SoVITS 的所有功能，包括大 batch 训练、实时推理等。享受丝滑体验吧！

---

> **文档生成时间：** 2026-08-04  
> **最后更新：** 2026-08-05  
> **如有问题，可查看官方 Issues：** https://github.com/RVC-Boss/GPT-SoVITS/issues
