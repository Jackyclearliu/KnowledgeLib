# GPT-SoVITS 运行时问题记录与排查

> **记录时间**：2026-08-06  
> **适用版本**：GPT-SoVITS v2Pro（WebUI）  
> **运行环境**：Windows 11 + RTX 4090 24GB + Miniconda (GPTSoVits env) + PyTorch (CUDA)

---

## 一、数据集准备阶段

### 1.1 数据集现状

- **来源**：星穹铁道（开拓者女中）游戏语音提取
- **原始数据量**：1600 对（`.wav` + `.lab`）
- **音频时长**：0-14s 为主，少量约 18s
- **音频质量**：绝大部分纯净人声，少量带轻微混响/回音
- **已有标注**：`.lab` 文本标注文件（UTF-8 编码，中文）

### 1.2 是否需要走标准音频处理流程？

**结论：不需要完全从头走标准流程。**

| 标准流程步骤 | 是否需要 | 原因 |
|-----------|---------|------|
| 音频切片 | ❌ 不需要 | 音频已经是短片段，无需再切 |
| ASR 语音识别 | ❌ 不需要 | 已有 `.lab` 标注文件 |
| UVR5 去混响/降噪 | ⚠️ 可选 | 仅少量有混响，绝大部分已是纯净人声，非必须 |
| 格式转换（.lab → .list） | ✅ 必须 | GPT-SoVITS 训练需要 `.list` 格式 |

### 1.3 训练集音频目录下 `.lab` 文件是否需要删除？

**结论：不需要删除，留在目录下完全不影响预处理。**

预处理脚本（`1-get-text.py`、`2-get-hubert-wav32k.py`、`3-get-semantic.py`）**只读取 `.list` 文件中指定的音频路径**，不会扫描目录。`.lab` 文件不在 `.list` 中，因此脚本根本不会处理它们。

### 1.4 `.lab` → `.list` 格式转换脚本

```python
import os
import re

dataset_dir = r"D:\Program Files\AI\GPT-SoVITS\dataset\pioneer_female"
output_file = os.path.join(dataset_dir, "pioneer_female.list")
speaker = "pioneer_female"
language = "zh"
min_text_length = 4

lines = []
skipped = 0
converted = 0

for fname in sorted(os.listdir(dataset_dir)):
    if not fname.endswith(".lab"):
        continue
    base_name = fname[:-4]
    wav_path = os.path.join(dataset_dir, base_name + ".wav")
    
    if not os.path.exists(wav_path):
        print(f"[WARN] Missing wav for: {fname}")
        continue
    
    lab_path = os.path.join(dataset_dir, fname)
    with open(lab_path, "r", encoding="utf-8") as f:
        text = f.read().strip().replace("\r", "").replace("\n", "")
    
    # 过滤掉过短的无效标注（如"谁？"、"唔……"等）
    effective_text = re.sub(r"[\s….,!?\-—\\'\";:\(\)\[\]\{\}、，。！？；：（）【】《》~～·`•]", "", text)
    if len(effective_text) < min_text_length:
        print(f"[SKIP] Too short ({len(effective_text)} chars): {fname} -> '{text}'")
        skipped += 1
        continue
    
    wav_path_forward = wav_path.replace("\\", "/")
    line = f"{wav_path_forward}|{speaker}|{language}|{text}"
    lines.append(line)
    converted += 1

with open(output_file, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"\n✅ Conversion complete!")
print(f"   Converted: {converted} entries")
print(f"   Skipped:   {skipped} entries (too short)")
```

**转换结果**：1600 条 → 有效 1507 条，跳过 93 条（过短标注）。

---

## 二、预处理阶段（1A）

### 2.1 正常现象：ComplexHalf 警告

```
UserWarning: ComplexHalf support is experimental and many operators don't support it yet.
  spectrum = torch.fft.rfft(strided_input).abs()
```

**结论：无害警告，可忽略。**

这是 PyTorch 在半精度（fp16）模式下对 `torch.fft.rfft()` 的兼容性提示。计算结果完全正确，不影响模型质量和训练收敛。

### 2.2 正常现象：_IncompatibleKeys 提示

```
_IncompatibleKeys(missing_keys=[], unexpected_keys=['sv_emb.weight', 'sv_emb.bias', ...])
```

**结论：正常加载报告，可忽略。**

关键点：`missing_keys=[]` 表示所有必需参数都已加载成功。`unexpected_keys` 是预训练模型（v2Pro）中多出来的模块参数（如 `sv_emb`、`ge_to512` 等），当前训练配置用不到，会被安全忽略。

---

## 三、SoVITS 微调训练阶段（1B）—— 核心问题

### 3.1 问题：训练立即崩溃（exit code 3221225477）

**现象：**

```
start training from epoch 1
  0%| | 0/155 [00:00<?, ?it/s]
[rank0]: ... Warning: find_unused_parameters=True was specified in DDP constructor ...
Traceback ...
torch.multiprocessing.spawn.ProcessExitedException: process 0 terminated with exit code 3221225477
```

**WebUI 表现**：显示"训练已完成"，但用时极短（仅几秒），实际未开始训练。

**错误码含义**：`3221225477`（即 `0xC0000005`）= Windows 内存访问冲突 / 段错误。

**根本原因**：**Windows 上 PyTorch `mp.spawn` 启动 DDP 子进程极不稳定**。  
即使配置远低于官方推荐（RTX 4090 24GB，bs=8，total_epoch=10），与显存无关。

### 3.2 第一次修复尝试：修改 DataLoader（部分有效）

修改 `GPT_SoVITS/s2_train.py` 中的 DataLoader：

```python
train_loader = DataLoader(
    train_dataset,
    num_workers=0,          # 原为 5
    shuffle=False,
    pin_memory=True,
    collate_fn=collate_fn,
    batch_sampler=train_sampler,
    persistent_workers=False,  # 原为 True
)
```

**结果**：`mp.spawn` 的崩溃概率降低，但 DDP 初始化仍然不稳定，最终仍会报 `3221225477`。

### 3.3 第二次修复尝试：绕过 mp.spawn（仍有 DDP 问题）

修改 `main()` 函数，Windows 单卡时直接调用 `run()`：

```python
def main():
    n_gpus = torch.cuda.device_count() if torch.cuda.is_available() else 1
    os.environ["MASTER_ADDR"] = "localhost"
    os.environ["MASTER_PORT"] = str(randint(20000, 55555))

    # Windows 单卡：绕过 mp.spawn
    if os.name == "nt" and n_gpus == 1:
        run(0, 1, hps)
    else:
        mp.spawn(run, nprocs=n_gpus, args=(n_gpus, hps))
```

**结果**：虽然绕过了 `mp.spawn`，但 `run()` 内部仍然调用了 `dist.init_process_group()` 和 `DDP()`，DDP 警告仍然存在，训练仍可能在 forward 阶段崩溃。

### 3.4 第三次修复尝试：错误！net_g.module = net_g 导致 RecursionError

试图在不使用 DDP 的情况下兼容 `.module` 访问：

```python
# ❌ 错误代码！会导致无限递归
net_g.module = net_g
net_d.module = net_d
```

**问题**：`net_g` 的 `.module` 属性指向了自己。当 PyTorch 的 `load_state_dict()` 递归遍历模型子模块时，发现 `.module` 就是模型本身，形成自引用循环，最终爆栈：

```
RecursionError: maximum recursion depth exceeded while calling a Python object
```

### 3.5 ✅ 最终修复方案：单进程模式（完全绕过 DDP）

**修改文件**：`GPT_SoVITS/s2_train.py`

**步骤 1**：`main()` 中 Windows 单卡直接调用 `run()`（同 3.3）

```python
def main():
    n_gpus = torch.cuda.device_count() if torch.cuda.is_available() else 1
    os.environ["MASTER_ADDR"] = "localhost"
    os.environ["MASTER_PORT"] = str(randint(20000, 55555))

    if os.name == "nt" and n_gpus == 1:
        run(0, 1, hps)
    else:
        mp.spawn(run, nprocs=n_gpus, args=(n_gpus, hps))
```

**步骤 2**：`run()` 中单进程模式跳过分布式初始化

```python
def run(rank, n_gpus, hps):
    global global_step
    is_single = (n_gpus == 1)

    if rank == 0:
        logger = utils.get_logger(hps.data.exp_dir)
        logger.info(hps)
        writer = SummaryWriter(log_dir=hps.s2_ckpt_dir)
        writer_eval = SummaryWriter(log_dir=os.path.join(hps.s2_ckpt_dir, "eval"))

    # 单进程模式下跳过分布式初始化
    if not is_single:
        dist.init_process_group(
            backend="gloo" if os.name == "nt" or not torch.cuda.is_available() else "nccl",
            init_method="env://?use_libuv=False",
            world_size=n_gpus,
            rank=rank,
        )

    torch.manual_seed(hps.train.seed)
    if torch.cuda.is_available():
        torch.cuda.set_device(rank)
    
    # ... DataLoader 定义（num_workers=0, persistent_workers=False）...
    
    # 步骤 3：单进程模式下用包装器替代 DDP
    if torch.cuda.is_available():
        if not is_single:
            net_g = DDP(net_g, device_ids=[rank], find_unused_parameters=True)
            net_d = DDP(net_d, device_ids=[rank], find_unused_parameters=True)
        else:
            class _SingleGPUWrapper:
                def __init__(self, module):
                    self.module = module
                def __call__(self, *args, **kwargs):
                    return self.module(*args, **kwargs)
                def __getattr__(self, name):
                    return getattr(self.module, name)
            net_g = _SingleGPUWrapper(net_g)
            net_d = _SingleGPUWrapper(net_d)
```

**_SingleGPUWrapper 的作用**：

| 功能 | 实现 | 兼容性 |
|------|------|--------|
| `.module` 访问 | `self.module = module` | ✅ 兼容所有 `net_g.module.xxx` |
| 前向调用 | `__call__` 转发 | ✅ 兼容 `net_g(...)` |
| 属性访问 | `__getattr__` 转发 | ✅ 兼容其他属性访问 |
| 非 nn.Module | 不继承 Module | ✅ `load_state_dict` 不会递归遍历它 |

**结果**：训练成功完成 12 个 epoch，无任何崩溃。

---

## 四、GPT 微调训练阶段（1B）

### 4.1 问题：训练启动后立即退出，无进度输出

**现象：**

```
semantic_data_len: 1507
phoneme_data_len: 1507
...
Trainable params: 77.6 M
...
```

随后控制台**无任何 epoch 进度输出**，WebUI 显示"已完成"，但 `GPT_weights_v2Pro/` 目录为空。

**根本原因**：与 SoVITS 相同——**Windows 上 PyTorch Lightning 的 DDP + DataLoader 多进程 worker 不稳定**。

- `s1_train.py` 中 `strategy=DDPStrategy(...)` 在 Windows 单卡下不必要
- `data_module.py` 中 `num_workers=4` + `persistent_workers=True` 导致 spawn 崩溃
- `bucket_sampler.py` 中 `dist.get_world_size()` 在单进程模式下因未初始化进程组而报错

### 4.2 修复方案

**修改 1：`GPT_SoVITS/s1_train.py`**

```python
# 原来
strategy=DDPStrategy(process_group_backend="nccl" if platform.system() != "Windows" else "gloo")
    if torch.cuda.is_available()
    else "auto",

# 改为
strategy="auto"
    if (platform.system() == "Windows" or not torch.cuda.is_available())
    else DDPStrategy(process_group_backend="nccl"),
```

**修改 2：`GPT_SoVITS/AR/data/data_module.py`**

```python
import os

# Windows 下禁用多进程 worker
if os.name == "nt":
    self.num_workers = 0
else:
    self.num_workers = self.config["data"]["num_workers"]

# DataLoader 中
return DataLoader(
    self._train_dataset,
    batch_size=batch_size,
    sampler=sampler,
    collate_fn=self._train_dataset.collate,
    num_workers=self.num_workers,
    persistent_workers=False if os.name == "nt" else True,
    prefetch_factor=None if os.name == "nt" else 16,
)
```

**修改 3：`GPT_SoVITS/AR/data/bucket_sampler.py`**

```python
# 原来（无条件调用，单进程下进程组未初始化会报错）
num_replicas = dist.get_world_size() if torch.cuda.is_available() else 1
rank = dist.get_rank() if torch.cuda.is_available() else 0

# 改为（先检查分布式是否已初始化）
if dist.is_initialized():
    num_replicas = dist.get_world_size() if torch.cuda.is_available() else 1
    rank = dist.get_rank() if torch.cuda.is_available() else 0
else:
    num_replicas = 1
    rank = 0
```

### 4.3 成功日志参考

```
Epoch 14/14 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 124/124 0:00:06 • 0:00:00 18.52it/s
  total_loss_step: 502.067 lr_step: 0.002
  top_3_acc_step: 0.741
  total_loss_epoch: 3179.324 lr_epoch: 0.002 top_3_acc_epoch: 0.662
```

- 每 epoch 约 **6 秒**
- 15 epoch 总计约 **1-2 分钟**
- 按 `save_every_n_epoch=5` 保存：`e5`、`e10`、`e15`

---

## 五、训练成功后的日志参考

### SoVITS 训练成功日志
```
phoneme_data_len: 1507
wav_data_len: 1507
...
loaded pretrained .../s2Gv2Pro.pth <All keys matched successfully>
loaded pretrained .../s2Dv2Pro.pth <All keys matched successfully>
start training from epoch 1
  0%| | 0/155 [00:00<?, ?it/s]INFO:开拓者女中:Train Epoch: 1 [0%]
...
100%|████████████████████████████████| 155/155 [01:28<00:00, 1.75it/s]
INFO:开拓者女中:====> Epoch: 1
...
INFO:开拓者女中:saving ckpt 开拓者女中_e12:Success.
INFO:开拓者女中:====> Epoch: 12
training done
```

- 每 epoch 约 **1分28秒**
- 12 epoch 总计约 **17-18分钟**
- 每 4 epoch 自动保存 checkpoint

### GPT 训练成功日志
```
Epoch 14/14 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 124/124 0:00:06 • 0:00:00 18.52it/s
  total_loss_step: 502.067 lr_step: 0.002
  top_3_acc_step: 0.741
  total_loss_epoch: 3179.324 lr_epoch: 0.002 top_3_acc_epoch: 0.662
```

- 每 epoch 约 **6 秒**
- 15 epoch 总计约 **1-2 分钟**
- 按 `save_every_n_epoch=5` 保存：`e5`、`e10`、`e15`

---

## 六、保存的模型位置

### SoVITS 模型
```
logs/开拓者女中/logs_s2_v2Pro/
├── G_233333333333.pth      ← 生成器最终权重
├── D_233333333333.pth      ← 判别器最终权重
└── ...

SoVITS_weights_v2Pro/
└── 开拓者女中_e12_s1860    ← 导出的推理用模型
```

### GPT 模型
```
GPT_weights_v2Pro/
├── 开拓者女中-e5.ckpt      ← 第 5 epoch 模型
├── 开拓者女中-e10.ckpt     ← 第 10 epoch 模型
└── 开拓者女中-e15.ckpt     ← 第 15 epoch 模型（最终）
```

---

## 七、关键经验总结

| 问题 | 根因 | 解决方案 |
|------|------|---------|
| SoVITS 崩溃 `3221225477` | Windows `mp.spawn` + DDP 不稳定 | 单进程模式，绕过 `mp.spawn` |
| GPT 启动后无进度退出 | PyTorch Lightning DDP + Windows worker 不稳定 | `strategy="auto"` + 关闭 worker |
| `ValueError: Default process group has not been initialized` | `bucket_sampler` 单进程下调用 `dist.get_world_size()` | 检查 `dist.is_initialized()` |
| DDP 警告 + 崩溃 | `dist.init_process_group` 在单卡下不必要 | 单卡时跳过分布式初始化 |
| `RecursionError` | `net_g.module = net_g` 自引用循环 | 使用 `_SingleGPUWrapper` 包装器 |
| DataLoader 崩溃（SoVITS） | `num_workers > 0` + `persistent_workers=True` | 设为 `num_workers=0`, `persistent_workers=False` |
| DataLoader 崩溃（GPT） | `num_workers=4` + `persistent_workers=True` | Windows 下设为 `num_workers=0` |
| 是否需要删 `.lab` | 不影响训练 | 不需要删除 |
| 是否需要 ASR | 已有标注 | 不需要 |
| ComplexHalf 警告 | PyTorch fp16 兼容性提示 | 忽略 |
| `_IncompatibleKeys` | 预训练模型多出来的参数 | `missing_keys=[]` 即正常，忽略 |

---

## 八、修改过的文件清单

| 文件 | 修改内容 |
|------|---------|
| `GPT_SoVITS/s2_train.py` | `main()` 绕过 `mp.spawn`；`run()` 跳过 DDP 初始化；`_SingleGPUWrapper` 替代 DDP；`num_workers=0` |
| `GPT_SoVITS/s1_train.py` | Windows 下单卡使用 `strategy="auto"` 替代 `DDPStrategy` |
| `GPT_SoVITS/AR/data/data_module.py` | Windows 下 `num_workers=0`，`persistent_workers=False` |
| `GPT_SoVITS/AR/data/bucket_sampler.py` | `dist.is_initialized()` 检查后再调用 `get_world_size()` |

---

## 九、后续建议

1. **推理测试**：进入 WebUI 的 **1C-inference**，选择 `GPT_weights_v2Pro/开拓者女中-e15.ckpt` 和 `SoVITS_weights_v2Pro/开拓者女中_e12_sxxxx.pth` 进行合成测试
2. **效果调优**：如果某些句子不稳定，可尝试：
   - 测试不同 epoch 的 GPT 模型（e5 / e10 / e15）哪个效果最好
   - 增加 SoVITS 训练轮数至 15-20
3. **备份修改**：建议备份以上 4 个修改后的文件，以便后续升级代码时参考
