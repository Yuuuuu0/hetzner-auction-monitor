
# Hetzner Auction Monitor

Hetzner Auction Monitor 是一个用于监控 Hetzner 服务器拍卖网站的脚本，自动过滤符合特定条件的服务器并通过 Bark 推送通知。

## 功能

1. 下载并解析 Hetzner 服务器拍卖的 JSON 数据。
2. 根据用户在 `.env` 文件中配置的过滤条件筛选服务器。
3. 将符合条件的服务器通过 Bark 推送通知，推送内容包含服务器的详细信息。

## 使用方法

### 先决条件

- Python 3.x
- `requests` 库
- `python-dotenv` 库
- Bark 推送配置


### 安装依赖

在项目目录下运行以下命令安装所需依赖：

```bash
pip install -r requirements.txt
```

### 配置环境变量

在项目根目录下创建一个 `.env` 文件，并配置以下内容：

```plaintext
LIVE_DATA_SB_JSON=/path/to/your/project/live_data_sb.json
BARK_PUSH_URL=https://api.day.app/your_device_key
CPU=AMD Ryzen 9 5950X
RAM=4 x RAM 32768 MB
LOCATION=FSN
TRAFFIC=unlimited
PRICE=1000
```

### 运行脚本

确保 `run_monitor.sh` 脚本具有可执行权限，并通过以下命令运行：

```bash
chmod +x run_monitor.sh
./run_monitor.sh /path/to/your/project
```

### 日志记录

脚本的运行日志将记录在 `logs/monitor.log` 文件中，包括下载 JSON 文件的时间戳和执行过程中的其他信息。

### 示例输出

通过 Bark 推送通知，格式如下：

```
Price: 1000
id: 123456
CPU: AMD Ryzen 9 5950X
RAM: 4 x RAM 32768 MB
Drives: 2 x 512 GB NVMe
Location: FSN
```
