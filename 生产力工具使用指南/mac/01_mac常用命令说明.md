# macOS 常用命令手册

> 本手册面向 macOS 用户，整理了日常开发及系统操作中高频使用的终端命令。所有命令均在 macOS（基于 Unix/BSD）环境下测试可用。

---

## 目录

- [1. 文件与目录操作](#1-文件与目录操作)
- [2. 查找与搜索](#2-查找与搜索)
- [3. 文本与文件内容处理](#3-文本与文件内容处理)
- [4. 删除操作（文件/目录/批量）](#4-删除操作文件目录批量)
- [5. VS Code 命令行操作](#5-vs-code-命令行操作)
- [6. 系统与进程管理](#6-系统与进程管理)
- [7. 网络相关命令](#7-网络相关命令)
- [8. 权限与用户管理](#8-权限与用户管理)
- [9. 压缩与解压](#9-压缩与解压)
- [10. 环境变量配置](#10-环境变量配置)
- [11. 磁盘与存储](#11-磁盘与存储)
- [12. 实用小技巧](#12-实用小技巧)

---

## 1. 文件与目录操作

### 1.1 查看当前位置与切换目录

| 命令 | 说明 |
|------|------|
| `pwd` | 显示当前所在目录的完整路径 |
| `cd 目录名` | 进入指定目录 |
| `cd ~` 或 `cd` | 回到用户主目录（Home） |
| `cd ..` | 返回上一级目录 |
| `cd -` | 回到刚才所在的目录 |
| `cd /` | 进入系统根目录 |

### 1.2 查看目录内容

| 命令 | 说明 |
|------|------|
| `ls` | 列出当前目录下的文件和文件夹 |
| `ls -l` | 以列表形式显示，包含权限、大小、修改时间等 |
| `ls -la` | 显示所有文件（包括隐藏文件，以 `.` 开头的文件） |
| `ls -lh` | 以人类可读格式显示文件大小（如 1.5K、20M） |
| `ls -ltr` | 按修改时间倒序排列，最新的在最后 |
| `ls 目录名` | 列出指定目录的内容 |

### 1.3 创建文件与目录

| 命令 | 说明 |
|------|------|
| `mkdir 目录名` | 创建新目录 |
| `mkdir -p a/b/c` | 递归创建多层目录（即使父目录不存在） |
| `touch 文件名` | 创建空文件，或更新已有文件的时间戳 |
| `touch file{1..5}.txt` | 批量创建 file1.txt 到 file5.txt |

### 1.4 复制文件与目录

| 命令 | 说明 |
|------|------|
| `cp 源文件 目标路径` | 复制文件到目标路径 |
| `cp file.txt /Users/xxx/Desktop/` | 将 file.txt 复制到桌面 |
| `cp file.txt newname.txt` | 复制文件并重命名 |
| `cp -r 源目录 目标目录` | **递归复制目录**（包括子目录和文件） |
| `cp -i 源文件 目标` | 覆盖前提示确认 |
| `cp -v 源文件 目标` | 显示详细复制过程 |

**示例：**

```bash
# 将项目文件夹复制到备份目录
cp -r ~/projects/myapp ~/backups/myapp_backup

# 复制并保留文件属性
cp -a 源目录 目标目录
```

### 1.5 移动与重命名文件/目录（剪切）

> macOS 中没有单独的"剪切"命令，移动操作即剪切。

| 命令 | 说明 |
|------|------|
| `mv 源文件 目标路径` | 移动文件到目标路径 |
| `mv 旧文件名 新文件名` | 重命名文件 |
| `mv 源目录 目标目录` | 移动整个目录 |
| `mv -i 源 目标` | 覆盖前提示确认 |

**示例：**

```bash
# 将文件从下载目录移动到文档目录
mv ~/Downloads/report.pdf ~/Documents/

# 将文件移动并重命名
mv ~/Downloads/data.csv ~/Documents/backup_data.csv

# 移动整个项目文件夹
mv ~/Desktop/old_project ~/Documents/projects/
```

### 1.6 创建与删除链接

| 命令 | 说明 |
|------|------|
| `ln 源文件 硬链接` | 创建硬链接 |
| `ln -s 源文件/目录 软链接` | 创建软链接（符号链接） |

```bash
# 创建软链接示例
ln -s /Applications/Sublime\ Text.app ~/Desktop/Sublime
```

---

## 2. 查找与搜索

### 2.1 find 命令 — 文件查找

| 命令 | 说明 |
|------|------|
| `find . -name "文件名"` | 在当前目录及子目录中查找指定文件 |
| `find / -name "文件名"` | 在整个系统中查找（较慢，可能需要 sudo） |
| `find . -type f` | 查找所有文件（不包括目录） |
| `find . -type d` | 查找所有目录 |
| `find . -name "*.txt"` | 查找所有 .txt 文件 |
| `find . -name "*.bak.*"` | 查找类似 file.bak.1 的文件 |
| `find . -mtime -7` | 查找 7 天内修改过的文件 |
| `find . -size +10M` | 查找大于 10MB 的文件 |
| `find . -empty` | 查找空文件或空目录 |
| `find . -name "*.log" -delete` | 查找并删除所有 .log 文件 |
| `find . -name "*.tmp" -exec rm {} \;` | 查找并删除所有 .tmp 文件 |

**常用参数说明：**

- `-name`：按文件名查找（区分大小写）
- `-iname`：按文件名查找（不区分大小写）
- `-type f`：只查找文件
- `-type d`：只查找目录
- `-mtime n`：n 天前修改的文件（-n 表示 n 天内，+n 表示 n 天前）
- `-size n`：按文件大小查找（+ 大于，- 小于）
- `-maxdepth n`：限制查找深度为 n 层
- `-exec 命令 {} \;`：对找到的文件执行命令

**示例：**

```bash
# 查找并删除所有 .bak.数字 后缀的文件
find . -name "*.bak.[0-9]*" -delete

# 查找并删除所有 .bak 文件（交互式确认）
find . -name "*.bak" -exec rm -i {} \;

# 查找最近 3 天修改的 .py 文件
find . -name "*.py" -mtime -3

# 在当前目录下 2 层深度内查找
find . -maxdepth 2 -name "*.json"

# 查找大于 100MB 的文件并按大小排序
find . -size +100M -exec ls -lh {} \;
```

### 2.2 grep 命令 — 文本内容搜索

| 命令 | 说明 |
|------|------|
| `grep "关键词" 文件名` | 在文件中搜索包含关键词的行 |
| `grep -r "关键词" 目录/` | 递归搜索目录中所有文件 |
| `grep -i "关键词" 文件` | 忽略大小写搜索 |
| `grep -n "关键词" 文件` | 显示匹配行的行号 |
| `grep -v "关键词" 文件` | 显示**不包含**关键词的行 |
| `grep -l "关键词" *.txt` | 只显示包含匹配内容的文件名 |
| `grep "^hello" 文件` | 搜索以 hello 开头的行 |
| `grep "world$" 文件` | 搜索以 world 结尾的行 |

**示例：**

```bash
# 在所有配置文件中搜索 database 配置
grep -r "database" /etc/

# 在代码中搜索函数定义
grep -rn "def calculate" ./src

# 结合 find 和 grep
grep -r "TODO" . --include="*.py"
```

### 2.3 which / whereis — 查找命令位置

| 命令 | 说明 |
|------|------|
| `which 命令名` | 查找可执行命令的路径 |
| `whereis 命令名` | 查找命令的二进制、源文件和手册页位置 |

```bash
which python3
# 输出：/usr/local/bin/python3

whereis git
# 输出：/usr/bin/git
```

### 2.4 mdfind — Spotlight 命令行搜索

| 命令 | 说明 |
|------|------|
| `mdfind 关键词` | 使用 Spotlight 搜索 |
| `mdfind -name "文件名"` | 按文件名搜索 |
| `mdfind -onlyin ~/Documents 关键词` | 只在指定目录搜索 |

```bash
# 搜索包含"财务报表"的所有文件
mdfind "财务报表"

# 只搜索文件名
mdfind -name "report.pdf"
```

---

## 3. 文本与文件内容处理

### 3.1 cat — 查看文件内容

| 命令 | 说明 |
|------|------|
| `cat 文件` | 显示整个文件内容 |
| `cat -n 文件` | 显示内容并带行号 |
| `cat 文件1 文件2 > 合并文件` | 合并多个文件 |

### 3.2 less / more — 分页查看

| 命令 | 说明 |
|------|------|
| `less 文件` | 分页查看，支持上下滚动（推荐） |
| `more 文件` | 分页查看，只能向下翻页 |

**less 中常用按键：**

- `空格` / `f`：向下翻页
- `b`：向上翻页
- `j` / `↓`：向下滚动一行
- `k` / `↑`：向上滚动一行
- `/关键词`：向下搜索
- `?关键词`：向上搜索
- `n`：下一个匹配
- `N`：上一个匹配
- `q`：退出

### 3.3 head / tail — 查看开头/结尾

| 命令 | 说明 |
|------|------|
| `head 文件` | 查看前 10 行 |
| `head -n 20 文件` | 查看前 20 行 |
| `tail 文件` | 查看最后 10 行 |
| `tail -n 20 文件` | 查看最后 20 行 |
| `tail -f 文件` | **实时追踪文件末尾**（常用于看日志） |
| `tail -f /var/log/system.log` | 实时查看系统日志 |

### 3.4 echo — 输出文本

| 命令 | 说明 |
|------|------|
| `echo "内容"` | 输出文本到终端 |
| `echo "内容" > 文件` | 将内容写入文件（覆盖） |
| `echo "内容" >> 文件` | 将内容追加到文件末尾 |

```bash
# 创建配置文件并写入内容
echo "API_KEY=123456" > .env

# 追加内容
echo "DEBUG=true" >> .env
```

### 3.5 sed — 流编辑器（文本替换）

| 命令 | 说明 |
|------|------|
| `sed 's/旧/新/' 文件` | 替换每行第一个匹配 |
| `sed 's/旧/新/g' 文件` | 替换所有匹配 |
| `sed -i '.bak' 's/旧/新/g' 文件` | 直接修改文件并备份 |
| `sed -n '5,10p' 文件` | 只显示第 5-10 行 |
| `sed '3d' 文件` | 删除第 3 行 |

```bash
# 将文件中所有 localhost 替换为 127.0.0.1
sed -i '' 's/localhost/127.0.0.1/g' config.txt

# 删除文件中的空行
sed -i '' '/^$/d' file.txt
```

> **注意：** macOS 的 `sed` 与 Linux 略有不同，`-i` 参数需要指定备份后缀（空字符串表示不备份）。

### 3.6 awk — 文本处理利器

| 命令 | 说明 |
|------|------|
| `awk '{print $1}' 文件` | 打印每行第一列 |
| `awk '{print $NF}' 文件` | 打印每行最后一列 |
| `awk -F',' '{print $2}' 文件` | 以逗号分隔，打印第二列 |
| `awk 'NR==5' 文件` | 打印第 5 行 |

```bash
# 查看进程列表，只打印进程名和 PID
ps aux | awk '{print $2, $11}'

# 统计文件行数
awk 'END{print NR}' 文件
```

---

## 4. 删除操作（文件/目录/批量）

### 4.1 rm — 删除文件与目录

| 命令 | 说明 |
|------|------|
| `rm 文件名` | 删除文件 |
| `rm -i 文件名` | 删除前确认 |
| `rm -f 文件名` | 强制删除，不提示 |
| `rm -r 目录名` | **递归删除目录及其内容** |
| `rm -rf 目录名` | **强制递归删除（慎用！）** |
| `rm -v 文件名` | 显示删除过程 |

**⚠️ 危险警告：**

- `rm -rf /` 会删除整个系统，**绝对不要执行！**
- `rm -rf ~` 会删除用户主目录下所有内容
- 删除后文件**无法从回收站恢复**（与图形界面不同）

### 4.2 批量删除特定文件

```bash
# 删除当前目录下所有 .bak 文件
rm *.bak

# 删除当前目录及子目录中所有 .tmp 文件
find . -name "*.tmp" -type f -delete

# 删除所有 .bak.数字 格式的文件（如 file.bak.1, file.bak.2）
find . -name "*.bak.[0-9]*" -type f -delete

# 删除 30 天前的日志文件
find . -name "*.log" -mtime +30 -delete

# 交互式删除（每个都确认）
find . -name "*.bak" -exec rm -i {} \;

# 清空当前目录下所有内容（保留目录本身）
rm -rf *
```

### 4.3 rmdir — 删除空目录

| 命令 | 说明 |
|------|------|
| `rmdir 目录名` | 删除空目录 |
| `rmdir -p a/b/c` | 递归删除空目录（如果删除后父目录也空了，一并删除） |

### 4.4 安全删除 — 移至回收站

如果不想永久删除，可以使用以下方法移到回收站：

```bash
# 使用 osascript（AppleScript）将文件移到回收站
osascript -e 'tell application "Finder" to delete POSIX file "/path/to/file"'

# 或者安装 trash 命令
brew install trash

# 然后使用
trash 文件名
```

---

## 5. VS Code 命令行操作

### 5.1 安装 code 命令

VS Code 安装后，需要将 `code` 命令添加到 PATH：

1. 打开 VS Code
2. 按 `Cmd+Shift+P` 打开命令面板
3. 输入 `Shell Command: Install 'code' command in PATH`
4. 回车确认

### 5.2 常用 code 命令

| 命令 | 说明 |
|------|------|
| `code` | 打开 VS Code |
| `code .` | 在当前目录打开 VS Code |
| `code 文件名` | 用 VS Code 打开指定文件 |
| `code 目录名` | 用 VS Code 打开指定目录/项目 |
| `code -n` | 打开新窗口 |
| `code -r 文件` | 在当前窗口打开文件 |
| `code -g 文件:行号` | 打开文件并跳转到指定行 |
| `code -g 文件:行号:列号` | 打开文件并跳转到指定行列 |
| `code -d 文件1 文件2` | 对比两个文件 |
| `code -w 文件` | 等待文件关闭后再返回终端 |
| `code --list-extensions` | 列出已安装的扩展 |
| `code --install-extension 扩展ID` | 安装扩展 |
| `code --uninstall-extension 扩展ID` | 卸载扩展 |

**示例：**

```bash
# 打开当前项目
code .

# 打开特定文件
code ~/Documents/notes.md

# 打开文件并跳转到第 25 行
code -g src/main.js:25

# 打开文件并跳转到第 10 行第 5 列
code -g config.json:10:5

# 对比两个文件
code -d version1.txt version2.txt

# 在当前项目中新建文件
code newfile.js

# 打开最近的项目
code -r ~/projects/myapp
```

### 5.3 结合其他命令使用

```bash
# 查找文件并用 VS Code 打开
find . -name "app.js" | head -1 | xargs code

# 查看日志时快速打开文件
tail -f error.log | grep "Error" | awk '{print $3}' | xargs code
```

---

## 6. 系统与进程管理

### 6.1 查看系统信息

| 命令 | 说明 |
|------|------|
| `uname -a` | 显示系统内核信息 |
| `sw_vers` | 显示 macOS 版本信息 |
| `system_profiler SPHardwareDataType` | 查看硬件信息 |
| `uptime` | 查看系统运行时间 |
| `date` | 显示当前日期时间 |
| `cal` | 显示日历 |
| `whoami` | 显示当前用户名 |
| `id` | 显示当前用户信息 |

### 6.2 进程管理

| 命令 | 说明 |
|------|------|
| `ps` | 查看当前终端的进程 |
| `ps aux` | 查看所有进程（详细） |
| `ps aux | grep 进程名` | 查找特定进程 |
| `top` | 实时显示进程（按 CPU 排序） |
| `htop` | 增强版 top（需安装） |
| `kill PID` | 终止指定进程 |
| `kill -9 PID` | 强制终止进程 |
| `killall 进程名` | 按名称终止所有匹配进程 |
| `pkill 进程名` | 按名称匹配终止进程 |
| `pgrep 进程名` | 查找进程 PID |

**示例：**

```bash
# 查找 Chrome 进程
ps aux | grep chrome

# 终止所有 Chrome 进程
killall Chrome

# 强制终止 PID 为 1234 的进程
kill -9 1234

# 查找并终止 Python 进程
pgrep python | xargs kill -9
```

### 6.3 系统活动监控

| 命令 | 说明 |
|------|------|
| `top` | 查看 CPU 和内存占用最高的进程 |
| `top -o cpu` | 按 CPU 使用率排序 |
| `top -o rsize` | 按内存使用量排序 |
| `vm_stat` | 查看虚拟内存统计 |
| `df -h` | 查看磁盘空间使用情况 |
| `du -sh 目录` | 查看指定目录的总大小 |
| `du -h -d 1` | 查看当前目录下各子目录大小 |

### 6.4 开关机与重启

| 命令 | 说明 |
|------|------|
| `sudo shutdown -h now` | 立即关机 |
| `sudo shutdown -r now` | 立即重启 |
| `sudo shutdown -h +10` | 10 分钟后关机 |
| `sudo reboot` | 重启 |

---

## 7. 网络相关命令

### 7.1 网络配置与诊断

| 命令 | 说明 |
|------|------|
| `ifconfig` | 查看网络接口配置 |
| `ipconfig getifaddr en0` | 获取 Wi-Fi IP 地址 |
| `ipconfig getifaddr en1` | 获取有线网络 IP 地址（如适用） |
| `ping 域名/IP` | 测试网络连通性 |
| `ping -c 5 域名` | 发送 5 个数据包后停止 |
| `nslookup 域名` | 查询域名 DNS 信息 |
| `dig 域名` | 详细 DNS 查询 |
| `traceroute 域名` | 追踪路由路径 |
| `netstat -an` | 查看网络连接状态 |
| `lsof -i :端口号` | 查看占用指定端口的进程 |

**示例：**

```bash
# 查看本机 IP
ipconfig getifaddr en0

# 测试网络连通性
ping baidu.com

# 查看 8080 端口被哪个进程占用
lsof -i :8080

# 终止占用 8080 端口的进程
lsof -ti :8080 | xargs kill -9
```

### 7.2 下载文件

| 命令 | 说明 |
|------|------|
| `curl -O URL` | 下载文件（保留原文件名） |
| `curl -o 文件名 URL` | 下载并指定文件名 |
| `curl -L URL` | 跟随重定向 |
| `wget URL` | 下载文件（需安装） |

```bash
# 下载文件
curl -O https://example.com/file.zip

# 下载并指定名称
curl -o myfile.zip https://example.com/file.zip

# 下载并显示进度
curl -# -O https://example.com/largefile.zip
```

---

## 8. 权限与用户管理

### 8.1 文件权限基础

macOS 文件权限分为三组：所有者（owner）、所属组（group）、其他用户（others）。

| 权限 | 数值 | 说明 |
|------|------|------|
| r（读） | 4 | 读取文件/列出目录内容 |
| w（写） | 2 | 修改文件/在目录中创建删除 |
| x（执行） | 1 | 执行文件/进入目录 |

常见组合：

- `755` = rwxr-xr-x（所有者可读写执行，其他人可读执行）
- `644` = rw-r--r--（所有者可读写，其他人只读）
- `777` = rwxrwxrwx（所有人都有所有权限，**不安全**）

### 8.2 chmod — 修改权限

| 命令 | 说明 |
|------|------|
| `chmod 755 文件` | 设置权限为 rwxr-xr-x |
| `chmod +x 脚本.sh` | 给文件添加可执行权限 |
| `chmod -x 文件` | 移除可执行权限 |
| `chmod -R 755 目录` | 递归修改目录及子目录权限 |
| `chmod u+w 文件` | 给所有者添加写权限 |

### 8.3 chown — 修改所有者

| 命令 | 说明 |
|------|------|
| `sudo chown 用户名 文件` | 修改文件所有者 |
| `sudo chown 用户:组 文件` | 同时修改所有者和所属组 |
| `sudo chown -R 用户 目录` | 递归修改目录所有者 |

```bash
# 修改文件所有者为当前用户
sudo chown $(whoami) file.txt

# 递归修改目录
sudo chown -R $(whoami):staff ~/myproject
```

### 8.4 sudo — 以管理员权限执行

| 命令 | 说明 |
|------|------|
| `sudo 命令` | 以超级用户权限执行命令 |
| `sudo -s` | 切换到 root 用户 shell |
| `sudo !!` | 以 sudo 重新执行上一条命令 |

---

## 9. 压缩与解压

### 9.1 zip 格式

| 命令 | 说明 |
|------|------|
| `zip 压缩包.zip 文件1 文件2` | 压缩文件 |
| `zip -r 压缩包.zip 目录/` | 递归压缩整个目录 |
| `unzip 压缩包.zip` | 解压到当前目录 |
| `unzip 压缩包.zip -d 目标目录` | 解压到指定目录 |
| `unzip -l 压缩包.zip` | 列出压缩包内容 |

```bash
# 压缩单个文件
zip archive.zip document.txt

# 压缩整个项目目录
zip -r project.zip myproject/

# 解压到桌面
unzip download.zip -d ~/Desktop/
```

### 9.2 tar 格式（.tar.gz / .tgz）

| 命令 | 说明 |
|------|------|
| `tar -czvf 压缩包.tar.gz 目录/` | 压缩为 tar.gz |
| `tar -xzvf 压缩包.tar.gz` | 解压 tar.gz |
| `tar -tvf 压缩包.tar.gz` | 查看压缩包内容 |
| `tar -czvf 压缩包.tgz 文件` | 压缩为 tgz |

**参数说明：**

- `-c`：创建压缩包
- `-x`：解压
- `-z`：使用 gzip 压缩
- `-v`：显示详细过程
- `-f`：指定文件名
- `-t`：查看内容

```bash
# 压缩目录
tar -czvf backup.tar.gz ~/Documents/important/

# 解压
tar -xzvf backup.tar.gz

# 解压到指定目录
tar -xzvf backup.tar.gz -C ~/Desktop/
```

### 9.3 其他格式

| 命令 | 说明 |
|------|------|
| `gzip 文件` | 压缩为 .gz |
| `gunzip 文件.gz` | 解压 .gz |
| `bzip2 文件` | 压缩为 .bz2 |
| `bunzip2 文件.bz2` | 解压 .bz2 |

---

## 10. 环境变量配置

### 10.1 查看环境变量

| 命令 | 说明 |
|------|------|
| `env` | 显示所有环境变量 |
| `echo $PATH` | 显示 PATH 环境变量 |
| `echo $HOME` | 显示用户主目录 |
| `echo $SHELL` | 显示当前使用的 shell |

### 10.2 临时设置环境变量（当前终端有效）

```bash
# 设置环境变量
export MY_VAR="hello"

# 查看
echo $MY_VAR

# 添加到 PATH
export PATH="/usr/local/custom/bin:$PATH"

# 取消设置
unset MY_VAR
```

### 10.3 永久设置环境变量

macOS 使用 zsh（Catalina 及以后版本默认），配置文件为 `~/.zshrc`。

```bash
# 编辑 zsh 配置文件
nano ~/.zshrc
# 或
code ~/.zshrc
```

**常用配置示例：**

```bash
# ~/.zshrc

# 自定义 PATH
export PATH="/usr/local/bin:/opt/homebrew/bin:$PATH"

# 设置 Java 环境变量
export JAVA_HOME=$(/usr/libexec/java_home -v 17)

# 设置 Python 虚拟环境默认路径
export WORKON_HOME=~/.virtualenvs

# 设置 Node.js 镜像
export NVM_NODEJS_ORG_MIRROR=https://npmmirror.com/mirrors/node

# 设置代理（根据需要）
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890

# 自定义别名
alias ll='ls -lah'
alias ..='cd ..'
```

### 10.4 使配置生效

```bash
source ~/.zshrc
```

### 10.5 不同 Shell 的配置文件

| Shell | 配置文件 |
|-------|---------|
| zsh | `~/.zshrc` |
| bash | `~/.bash_profile` 或 `~/.bashrc` |
| 所有 Shell | `~/.profile` |

### 10.6 别名（Alias）设置

```bash
# 在 ~/.zshrc 中添加
alias ..='cd ..'
alias ...='cd ../..'
alias ll='ls -lah'
alias la='ls -A'
alias grep='grep --color=auto'
alias cp='cp -i'
alias mv='mv -i'
alias rm='rm -i'
alias c='clear'
alias h='history'
alias p='pwd'

# 项目相关
alias proj='cd ~/projects'
alias desk='cd ~/Desktop'

# Git 别名
alias gs='git status'
alias ga='git add'
alias gc='git commit'
alias gp='git push'
```

---

## 11. 磁盘与存储

### 11.1 磁盘空间查看

| 命令 | 说明 |
|------|------|
| `df -h` | 查看各分区磁盘使用情况 |
| `du -sh 目录` | 查看目录总大小 |
| `du -h -d 1` | 查看当前目录下各一级子目录大小 |
| `du -h --max-depth=1 | sort -hr` | 查看目录大小并排序 |

```bash
# 查看当前目录下哪个文件夹最大
du -h -d 1 | sort -hr | head -10

# 查看用户目录总大小
du -sh ~
```

### 11.2 磁盘工具

| 命令 | 说明 |
|------|------|
| `diskutil list` | 列出所有磁盘和分区 |
| `diskutil info disk0` | 查看磁盘详细信息 |
| `diskutil eraseDisk 格式 名称 /dev/disk2` | 格式化磁盘 |

### 11.3 清理缓存与日志

```bash
# 查看日志大小
du -sh /var/log/

# 清理用户缓存（谨慎操作）
rm -rf ~/Library/Caches/*

# 清理 Docker 占用空间（如果使用）
docker system prune -a
```

---

## 12. 实用小技巧

### 12.1 命令行快捷键

| 快捷键 | 说明 |
|--------|------|
| `Ctrl + A` | 光标移到行首 |
| `Ctrl + E` | 光标移到行尾 |
| `Ctrl + U` | 删除光标到行首的内容 |
| `Ctrl + K` | 删除光标到行尾的内容 |
| `Ctrl + W` | 删除光标前的一个单词 |
| `Ctrl + L` | 清屏（相当于 `clear`） |
| `Ctrl + C` | 终止当前命令 |
| `Ctrl + Z` | 暂停当前命令（可后续恢复） |
| `Ctrl + R` | 搜索历史命令 |
| `!!` | 执行上一条命令 |
| `!n` | 执行历史记录中第 n 条命令 |
| `Tab` | 自动补全文件名/命令 |
| `Tab Tab` | 显示所有可能的补全选项 |

### 12.2 历史命令

| 命令 | 说明 |
|------|------|
| `history` | 显示命令历史 |
| `history | grep "关键词"` | 搜索历史命令 |
| `!字符串` | 执行最近以该字符串开头的命令 |
| `!?字符串` | 执行最近包含该字符串的命令 |

### 12.3 管道与重定向

| 符号 | 说明 |
|------|------|
| `\|` | 管道，将前一个命令的输出传给后一个命令 |
| `>` | 输出重定向到文件（覆盖） |
| `>>` | 输出追加到文件 |
| `<` | 从文件读取输入 |
| `2>` | 错误输出重定向 |
| `&>` | 标准输出和错误输出都重定向 |

```bash
# 将 ls 结果保存到文件
ls -la > filelist.txt

# 将错误信息保存到文件
command 2> error.log

# 同时保存输出和错误
command &> output.log

# 管道组合
cat file.txt | grep "error" | sort | uniq -c
```

### 12.4 后台运行

```bash
# 在命令后加 &，在后台运行
long_running_task &

# 查看后台任务
jobs

# 将后台任务调到前台
fg %1

# 让前台任务在后台继续运行
# 先按 Ctrl + Z 暂停，然后执行
bg %1

# nohup 让命令在退出终端后继续运行
nohup python script.py &
```

### 12.5 批量与组合操作

```bash
# 批量重命名（将所有 .txt 改为 .bak）
for f in *.txt; do mv "$f" "${f%.txt}.bak"; done

# 批量创建目录
mkdir -p project/{src,test,docs,bin}

# 并行执行多个命令
command1 & command2 & command3 & wait

# 条件执行
command1 && command2   # command1 成功才执行 command2
command1 || command2   # command1 失败才执行 command2
```

### 12.6 常用路径速记

| 路径 | 说明 |
|------|------|
| `~` | 用户主目录（/Users/用户名） |
| `.` | 当前目录 |
| `..` | 上一级目录 |
| `-` | 刚才所在的目录 |
| `/` | 系统根目录 |

### 12.7 Homebrew 常用命令

macOS 上最流行的包管理器，建议安装：[https://brew.sh](https://brew.sh)

| 命令 | 说明 |
|------|------|
| `brew install 包名` | 安装软件 |
| `brew uninstall 包名` | 卸载软件 |
| `brew search 关键词` | 搜索软件 |
| `brew list` | 列出已安装的软件 |
| `brew update` | 更新 Homebrew 本身 |
| `brew upgrade` | 更新所有已安装的软件 |
| `brew upgrade 包名` | 更新指定软件 |
| `brew cleanup` | 清理旧版本和缓存 |
| `brew doctor` | 检查 Homebrew 健康状况 |
| `brew services list` | 查看后台服务状态 |
| `brew services start 服务名` | 启动服务 |
| `brew services stop 服务名` | 停止服务 |

```bash
# 安装常用工具示例
brew install wget tree htop git node python
```

### 12.8 tree 命令 — 可视化目录结构

```bash
# 安装 tree
brew install tree

# 基本使用
tree                    # 显示完整目录树
tree -L 2               # 只显示 2 层深度
tree -d                 # 只显示目录
tree -I 'node_modules'  # 忽略指定文件夹
tree -L 3 > structure.txt  # 导出到文件
```

---

## 附录：快速查询表

### A. 文件操作速查

| 操作 | 命令 |
|------|------|
| 复制文件 | `cp 源文件 目标` |
| 复制目录 | `cp -r 源目录 目标` |
| 移动/剪切文件 | `mv 源文件 目标` |
| 移动/剪切目录 | `mv 源目录 目标` |
| 删除文件 | `rm 文件` |
| 删除目录 | `rm -r 目录` |
| 强制删除 | `rm -rf 目录/文件` |
| 批量删除 .bak 文件 | `find . -name "*.bak" -delete` |

### B. 查找速查

| 场景 | 命令 |
|------|------|
| 按文件名查找 | `find . -name "文件名"` |
| 按类型查找文件 | `find . -type f -name "*.py"` |
| 文件内容搜索 | `grep -r "关键词" 目录/` |
| 查找命令位置 | `which 命令` |

### C. VS Code 速查

| 场景 | 命令 |
|------|------|
| 打开当前目录 | `code .` |
| 打开文件 | `code 文件名` |
| 打开并跳转到行 | `code -g 文件:行号` |
| 对比文件 | `code -d 文件1 文件2` |

### D. 环境变量速查

| 操作 | 命令/文件 |
|------|----------|
| 临时设置 | `export VAR=值` |
| 永久设置（zsh） | 编辑 `~/.zshrc` |
| 使配置生效 | `source ~/.zshrc` |
| 查看 PATH | `echo $PATH` |

---

## 结语

终端命令看似复杂，但一旦熟悉，效率远超图形界面。建议：

1. **从常用命令开始**：先熟练掌握 `ls`, `cd`, `cp`, `mv`, `rm`, `find`, `grep`
2. **善用 Tab 补全**：减少输入错误，加速操作
3. **使用别名**：在 `~/.zshrc` 中定义常用命令的简写
4. **善用 `man` 和 `--help`**：`man 命令名` 或 `命令 --help` 查看详细文档
5. **谨慎使用 `rm -rf`**：删除前确认路径，避免误删

> 💡 **提示**：不确定命令效果时，先在不重要的文件/目录上测试，或使用 `-i` 参数开启交互确认。

---

*本手册持续更新中，如有遗漏或错误，欢迎补充指正。*
