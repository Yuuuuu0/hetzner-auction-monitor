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
        "BARK_PUSH_URL": os.getenv(f"{prefix}_BARK_PUSH_URL"),
        "BARK_PUSH_KEY": os.getenv(f"{prefix}_BARK_PUSH_KEY"),
        "TG_TOKEN": os.getenv(f"{prefix}_TG_TOKEN"),
        "TG_CHAT_ID": os.getenv(f"{prefix}_TG_CHAT_ID"),
        "CPU": os.getenv(f"{prefix}_CPU"),
        "RAM": os.getenv(f"{prefix}_RAM"),
        "LOCATION": os.getenv(f"{prefix}_LOCATION"),
        "TRAFFIC": os.getenv(f"{prefix}_TRAFFIC"),
        "PRICE": float(os.getenv(f"{prefix}_PRICE", 0)),
        "LIVE_DATA_JSON": os.getenv(f"{prefix}_LIVE_DATA_JSON")
    }


# 过滤服务器数据
def filter_server(server, config):
    if config["CPU"] and config["CPU"] not in server["cpu_fullname"]:
        return False
    if config["RAM"] and config["RAM"] not in server["ram_hr"]:
        return False
    if config["LOCATION"] and config["LOCATION"] not in server["datacenter"]:
        return False
    if config["TRAFFIC"] and server["traffic"] != config["TRAFFIC"]:
        return False
    if config["PRICE"] and server["price"] >= config["PRICE"]:
        return False
    return True


# 格式化服务器描述
def format_server_description(server):
    price = server.get("price", "N/A")
    name = server.get("name", "N/A")
    id = server.get("id", "N/A")
    cpu = server.get("cpu_fullname", "N/A")
    ram = server.get("ram_hr", "N/A")
    drives = ", ".join(server.get("hdd_arr", ["N/A"]))
    location = server.get("datacenter", "N/A")
    return f"Price：€{price}/month\nServer Name：{name}\nAuctionID：{id}\nCPU：{cpu}\nRAM：{ram}\nDrives：{drives}\nLocation：{location}\n"


# 发送推送消息
def send_telegram_msg(message, config):
    """向指定的 Telegram 发送消息"""
    if not config["TG_TOKEN"]:
        logging.info("TG_TOKEN为空，跳过发送消息")
        return True

    url = f"https://api.telegram.org/bot{config['TG_TOKEN']}/sendMessage"
    payload = {
        "chat_id": config["TG_CHAT_ID"],
        "text": "Hetzner - 服务器监控\n\n" + message
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
        "title": "Hetzner - 服务器监控",
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


# 获取服务器数据
def fetch_data(config):
    with open(config["LIVE_DATA_JSON"], 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data


# 获取过滤后的服务器
def get_filtered_servers(data, config):
    return [server for server in data['server'] if filter_server(server, config)]
