import json

wyh = """
bank-agent_large_transaction_inquiry
bank-financial_product_sales
car_insurance-sales_promotion
clear_node_name
courier-delayed_package_handling
internet-broadband_repair_phone_support
restaurant-private_room_booking
shopping-return_request
survey-membership_reward
telecom-sim_card_upgrade_promotion
travel-booking
"""
import os

def split(src_directory):
    count_dict = {}
    # 遍历指定目录
    for filename in os.listdir(src_directory):
        # 检查是否为json文件
        if filename.lower().endswith('.json'):

            # 获取文件名第一个字母
            file_path = os.path.join(src_directory, filename)
            with open(file_path, 'r', encoding='utf-8-sig') as json_file:
                data = json.load(json_file)
                aid = str(data["a_id"])
                if aid.startswith("ws"):
                    name = aid[:2]
                else:
                    name = aid[:3]

            save_path = f'{src_directory}/../{name}'

            if not os.path.exists(save_path):
                os.makedirs(save_path)
            print(f"目录 {save_path} 已创建。")

            # 写回JSON文件
            with open(str(save_path)+f"/{filename}", 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
                print(f"已更新文件 {filename}")

            # 统计该字母开头的json文件数量
            if name in count_dict:
                count_dict[name] += 1
            else:
                count_dict[name] = 1

    # 返回字母计数字典和文件总数
    print(count_dict)

split("./one_file_one_dialogue")
# 1700 {'wyh': 306, 'pjx': 190, 'zmh': 334, 'ws': 300, 'wyq': 270, 'slx': 300}
# 1120 {'pjx': 150, 'ws': 224, 'wyq': 177, 'slx': 200, 'wyh': 150, 'zmh': 256}