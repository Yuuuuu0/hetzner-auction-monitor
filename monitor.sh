#!/bin/bash

# 检查是否指定了工作目录
if [ -z "$1" ]; then
  echo "Usage: $0 <working_directory>"
  exit 1
fi

WORK_DIR=$1

# 初始化配置信息
ENV_FILE="$WORK_DIR/.env"
LOGS_DIR="$WORK_DIR/logs"
LIVE_DATA_JSON="$WORK_DIR/live_data_sb.json"

# 判断 .env 文件是否存在
if [ ! -f "$ENV_FILE" ]; then
  echo "The .env file does not exist."
  exit 0
else
  echo ".env file exists. Updating LIVE_DATA_SB_JSON path."
  sed -i "" "s|^LIVE_DATA_SB_JSON=.*|LIVE_DATA_SB_JSON=$LIVE_DATA_JSON|" "$ENV_FILE"
fi

# 判断 logs 文件夹是否存在
if [ ! -d "$LOGS_DIR" ]; then
  echo "Creating logs directory."
  mkdir -p "$LOGS_DIR"
fi

# 下载 JSON 文件到工作目录下
echo "$(date +"%Y-%m-%d %H:%M:%S") - Downloading JSON file from Hetzner." >> "$LOGS_DIR/monitor.log"
curl -s https://www.hetzner.com/_resources/app/jsondata/live_data_sb.json -o "$LIVE_DATA_JSON"

# 调用 monitor.py 并将日志写到 logs 文件夹中
echo "Running monitor.py and logging output to $LOGS_DIR/monitor.log."
/usr/bin/python3 "$WORK_DIR/monitor.py" >> "$LOGS_DIR/monitor.log" 2>&1