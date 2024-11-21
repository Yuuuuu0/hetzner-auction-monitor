import logging
import requests
import json
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# 从环境变量获取过滤条件和Bark推送地址
BARK_PUSH_URL = os.getenv("BARK_PUSH_URL")
BARK_PUSH_KEY = os.getenv("BARK_PUSH_KEY")
TG_TOKEN = os.getenv("TG_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")
# 配置过滤条件
CPU = os.getenv("EN_CPU")
RAM = os.getenv("EN_RAM")
LOCATION = os.getenv("EN_LOCATION")
TRAFFIC = os.getenv("EN_TRAFFIC")
PRICE = float(os.getenv("EN_PRICE"))
LIVE_DATA_JSON = os.getenv("LIVE_DATA_EN_JSON")
# 通知头
SEND_TITLE = "Hetzner - 独服监控"

# 设置日志输出
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y年%m月%d日 %H:%M:%S',
    handlers=[logging.StreamHandler()]
)


def fetch_data():
    with open(LIVE_DATA_JSON, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data


def filter_server(server):
    if CPU and CPU not in server["cpu_fullname"]:
        return False
    if RAM and RAM not in server["ram_hr"]:
        return False
    if LOCATION and LOCATION not in server["datacenter"]:
        return False
    if TRAFFIC and server["traffic"] != TRAFFIC:
        return False
    if PRICE and server["price"] >= PRICE:
        return False
    return True


def get_filtered_servers(data):
    return [server for server in data['server'] if filter_server(server)]


def format_server_description(server):
    price = server.get("price", "N/A")
    name = server.get("name", "N/A")
    id = server.get("id", "N/A")
    cpu = server.get("cpu_fullname", "N/A")
    ram = server.get("ram_hr", "N/A")
    drives = ", ".join(server.get("hdd_arr", ["N/A"]))
    location = server.get("datacenter", "N/A")
    return f"Price：€{price}/month\nServer Name：{name}\nAuctionID：{id}\nCPU：{cpu}\nRAM：{ram}\nDrives：{drives}\nLocation：{location}\n"


def send_msg(message):
    return send_telegram_msg(message) and send_bark_notification(message)


def send_bark_notification(message):
    if not BARK_PUSH_URL or not BARK_PUSH_KEY:
        logging.info("BARK关键参数为空，跳过发送消息")
        return True

    payload = json.dumps({
        "title": SEND_TITLE,
        "body": message,
        "device_key": BARK_PUSH_KEY
    })
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br"
    }
    response = requests.post(BARK_PUSH_URL, headers=headers, data=payload.encode('utf-8'))
    logging.info(f"Response Status Code:{response.status_code}")
    return response.status_code == 200


def send_telegram_msg(message):
    """向指定的 Telegram 发送消息"""
    if not TG_TOKEN:
        logging.info("TG_TOKEN为空，跳过发送消息")
        return True

    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {
        "chat_id": TG_CHAT_ID,
        "text": SEND_TITLE + "\n\n" + message
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


if __name__ == "__main__":
    data = fetch_data()
    filtered_servers = get_filtered_servers(data)

    if filtered_servers:
        message = "\n\n".join(
            [format_server_description(server) for server in filtered_servers]
        )
        success = send_msg(message)
        if success:
            logging.info("Notification sent successfully")
        else:
            logging.info("Failed to send notification")
    else:
        logging.info("No servers matched the filter criteria.")
