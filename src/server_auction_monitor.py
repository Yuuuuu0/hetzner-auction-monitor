import logging
from utils import *

# 配置日志
setup_logging()

# 加载环境变量
config = get_config("SB")

filters = {
    "CPU": config["CPU"],
    "RAM": config["RAM"],
    "LOCATION": config["LOCATION"],
    "TRAFFIC": config["TRAFFIC"],
    "PRICE": config["PRICE"]
}

field_map = {
    "PRICE": "price",
    "AuctionID": "id",
    "CPU": "cpu",
    "RAM": "ram",
    "Drives": "hdd_arr",
    "LOCATION": "datacenter",
    "TRAFFIC": "traffic"
}

custom_labels = {
    "PRICE": "Price (€)",
    "AuctionID": "Server AuctionID",
    "RAM": "RAM (GB)"
}

# 主逻辑
if __name__ == "__main__":
    data = fetch_data(config)
    filtered_servers = get_filtered_servers(data, filters, field_map)

    if filtered_servers:
        message = "\n\n".join(
            [format_server_description(server, field_map, custom_labels) for server in filtered_servers])
        success = send_msg(message, config)
        if success:
            logging.info("Notification sent successfully")
        else:
            logging.info("Failed to send notification")
    else:
        logging.info("No servers matched the filter criteria.")
