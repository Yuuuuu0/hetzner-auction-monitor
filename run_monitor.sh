#!/bin/bash

# 获取当前脚本的目录
WORK_DIR=$(dirname "$(realpath "$0")")

# 初始化配置信息
ENV_FILE="$WORK_DIR/.env"
LOGS_DIR="$WORK_DIR/logs"
LIVE_DATA_SB_JSON="$WORK_DIR/config/live_data_sb.json"
LIVE_DATA_EN_JSON="$WORK_DIR/config/live_data_en.json"

# 判断 .env 文件是否存在
if [ ! -f "$ENV_FILE" ]; then
  echo "The .env file does not exist."
  exit 0
fi

# 判断 logs 文件夹是否存在
if [ ! -d "$LOGS_DIR" ]; then
  echo "Creating logs directory."
  mkdir -p "$LOGS_DIR"
fi

# 下载 JSON 文件到工作目录下
echo "$(date +"%Y-%m-%d %H:%M:%S") - Downloading JSON file from Hetzner." >> "$LOGS_DIR/sb_monitor.log"
curl -s https://www.hetzner.com/_resources/app/jsondata/live_data_sb.json -o "$LIVE_DATA_SB_JSON"
echo "$(date +"%Y-%m-%d %H:%M:%S") - Downloading JSON file from Hetzner." >> "$LOGS_DIR/en_monitor.log"
curl -s https://www.hetzner.com/_resources/app/jsondata/live_data_en.json -o "$LIVE_DATA_EN_JSON"

# 调用 server_auction_monitor.py 并将日志写到 logs 文件夹中
echo "Running server_auction_monitor.py and logging output to $LOGS_DIR/sb_monitor.log."
/usr/bin/python3 "$WORK_DIR/src/server_auction_monitor.py" >> "$LOGS_DIR/sb_monitor.log" 2>&1

echo "Running dedicated_server_monitor.py and logging output to $LOGS_DIR/en_monitor.log."
/usr/bin/python3 "$WORK_DIR/src/dedicated_server_monitor.py" >> "$LOGS_DIR/en_monitor.log" 2>&1
