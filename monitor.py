import requests
import json
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# 从环境变量获取过滤条件和Bark推送地址
CPU = os.getenv("CPU")
RAM = os.getenv("RAM")
LOCATION = os.getenv("LOCATION")
TRAFFIC = os.getenv("TRAFFIC")
PRICE = float(os.getenv("PRICE"))
BARK_PUSH_URL = os.getenv("BARK_PUSH_URL")
BARK_PUSH_KEY = os.getenv("BARK_PUSH_KEY")
LIVE_DATA_SB_JSON = os.getenv("LIVE_DATA_SB_JSON")


def fetch_data():
    with open(LIVE_DATA_SB_JSON, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data


def filter_server(server):
    return (
            #CPU in server["description"] and
            any(CPU in desc for desc in server["description"]) and
            any(RAM in desc for desc in server["description"]) and
            LOCATION in server["datacenter"] and
            server["traffic"] == TRAFFIC and
            server["price"] < PRICE
    )


def get_filtered_servers(data):
    return [server for server in data['server'] if filter_server(server)]


def format_server_description(server):
    price = server.get("price", "N/A")
    id = server.get("id", "N/A")
    cpu = server.get("cpu", "N/A")
    ram = ", ".join(server.get("ram", ["N/A"]))
    drives = ", ".join(server.get("hdd_arr", ["N/A"]))
    location = server.get("datacenter", "N/A")
    return f"Price：€{price}/month\nServer AuctionID：{id}\nCPU：{cpu}\nRAM：{ram}\nDrives：{drives}\nLocation：{location}\n"


def send_bark_notification(url, filtered_servers):
    descriptions = "\n\n".join(
        [format_server_description(server) for server in filtered_servers]
    )
    payload = json.dumps({
        "title": "监控到指定Hetzner独服了",
        "body": descriptions,
        "device_key": BARK_PUSH_KEY
    })
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br"
    }

    response = requests.post(url, headers=headers, data=payload.encode('utf-8'))
    print("Response Status Code:", response.status_code)

    return response.status_code == 200


if __name__ == "__main__":
    data = fetch_data()
    filtered_servers = get_filtered_servers(data)

    if filtered_servers:
        success = send_bark_notification(BARK_PUSH_URL, filtered_servers)
        if success:
            print("Notification sent successfully")
        else:
            print("Failed to send notification")
    else:
        print("No servers matched the filter criteria.")
