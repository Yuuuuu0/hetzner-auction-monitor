import os
import json
import logging
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


# 配置日志输出
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y年%m月%d日 %H:%M:%S',
        handlers=[logging.StreamHandler()]
    )


# 从环境变量获取配置
def get_config(prefix):
    return {
        "BARK_PUSH_URL": os.getenv("BARK_PUSH_URL"),
        "BARK_PUSH_KEY": os.getenv("BARK_PUSH_KEY"),
        "NOTIFY_TITLE": os.getenv(f"{prefix}_NOTIFY_TITLE"),
        "TG_TOKEN": os.getenv("TG_TOKEN"),
        "TG_CHAT_ID": os.getenv("TG_CHAT_ID"),
        "CPU": os.getenv(f"{prefix}_CPU"),
        "RAM": os.getenv(f"{prefix}_RAM"),
        "LOCATION": os.getenv(f"{prefix}_LOCATION"),
        "TRAFFIC": os.getenv(f"{prefix}_TRAFFIC"),
        "PRICE": float(os.getenv(f"{prefix}_PRICE", 0)),
        "LIVE_DATA_JSON": os.getenv(f"{prefix}_LIVE_DATA_JSON")
    }


# 过滤服务器数据
def filter_server(server, filters, field_map):
    """
    通用过滤逻辑
    :param server: 当前服务器数据
    :param filters: 用户定义的过滤条件
    :param field_map: 字段映射
    :return: 是否符合条件
    """
    for key, filter_value in filters.items():
        if not filter_value:  # 如果过滤条件为空，跳过此条件
            continue
        field = field_map.get(key)  # 获取字段映射
        if field is None:
            continue

        # 获取字段的实际值
        server_value = server.get(field, None)

        # 处理价格字段
        if key == "PRICE":
            try:
                if float(server_value) >= float(filter_value):
                    return False
            except (TypeError, ValueError):
                logging.error(f"价格过滤器异常: server_value={server_value}, filter_value={filter_value}")
                return False

        # 处理 RAM 字段（列表匹配）
        elif key == "RAM":
            if not any(filter_value in item for item in (server_value or [])):
                return False

        # 一般字段匹配
        elif isinstance(server_value, list):
            if filter_value not in server_value:
                return False
        else:
            if filter_value not in str(server_value):  # 转为字符串匹配
                return False

    return True


# 格式化服务器描述
def format_server_description(server, field_map, custom_labels=None):
    """
    通用的服务器描述格式化函数
    :param server: 当前服务器数据
    :param field_map: 字段映射，用于动态提取字段
    :param custom_labels: 自定义显示标签，默认为字段名
    :return: 格式化后的字符串
    """
    custom_labels = custom_labels or {}
    description_parts = []

    for field, server_key in field_map.items():
        value = server.get(server_key, "N/A")

        # 如果值是列表，则处理每个元素
        if isinstance(value, list):
            if all(isinstance(item, dict) for item in value):
                # 如果列表元素是字典，尝试提取主要字段
                value = ", ".join([str(item.get("name", item)) for item in value])
            else:
                # 普通列表转换为字符串
                value = ", ".join(map(str, value))

        # 如果值是字典，直接转换为字符串
        elif isinstance(value, dict):
            value = json.dumps(value, ensure_ascii=False)

        label = custom_labels.get(field, field)  # 如果没有自定义标签，使用字段名作为标签
        description_parts.append(f"{label}：{value}")

    return "\n".join(description_parts)


# 发送推送消息
def send_telegram_msg(message, config):
    """向指定的 Telegram 发送消息"""
    if not config["TG_TOKEN"]:
        logging.info("TG_TOKEN为空，跳过发送消息")
        return True

    url = f"https://api.telegram.org/bot{config['TG_TOKEN']}/sendMessage"
    payload = {
        "chat_id": config["TG_CHAT_ID"],
        "text": config["NOTIFY_TITLE"] + "\n\n" + message
    }
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        if response.status_code != 200:
            logging.error(f"发送消息失败: {response.status_code}, {response.text}")
            return False
        return True
    except requests.exceptions.RequestException as e:
        logging.error(f"发送Telegram消息时发生错误: {e}")
        return False


def send_bark_notification(message, config):
    """发送Bark通知"""
    if not config["BARK_PUSH_URL"] or not config["BARK_PUSH_KEY"]:
        logging.info("BARK关键参数为空，跳过发送消息")
        return True

    payload = json.dumps({
        "title": config["NOTIFY_TITLE"],
        "body": message,
        "device_key": config["BARK_PUSH_KEY"]
    })
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br"
    }
    response = requests.post(config["BARK_PUSH_URL"], headers=headers, data=payload.encode('utf-8'))
    logging.info(f"Response Status Code:{response.status_code}")
    return response.status_code == 200


# 统一消息发送
def send_msg(message, config):
    return send_telegram_msg(message, config) and send_bark_notification(message, config)
    # return send_bark_notification(message, config)


# 获取服务器数据
def fetch_data(config):
    with open(config["LIVE_DATA_JSON"], 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data


# 获取过滤后的服务器
def get_filtered_servers(data, filters, field_map):
    return [server for server in data['server'] if filter_server(server, filters, field_map)]
