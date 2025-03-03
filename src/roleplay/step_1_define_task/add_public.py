import copy
import json
import os

from utils.util import jaccard_distance

user_state = """
打招呼
习惯性应答可以继续
没听懂
担忧疑惑
抱怨
投诉
不礼貌用语
不感兴趣
不方便
拖延决策
闲聊
其他意图
感谢
结束
"""
user_state = user_state.strip().split("\n")
print(user_state)

agent_action = """
开始
打招呼
共情安抚
建立信任
排忧解惑
尝试说服
闲聊
感谢
其他动作
礼貌结束
"""
agent_action = agent_action.strip().split("\n")
print(agent_action)


def add_item(old:list,adder:list):
    old = [str(i).replace("代理.","").replace("用户.","") for i in old]
    for a in adder:
        for b in old:
            jd = jaccard_distance(set(a), set(b))
            if jd != 0 and jd < 0.6:
                print(f"[添加通用动作] jd={jd} 可能相似的节点：old {b}  vs  {a}")
    for a in adder:
        if a not in old:
            old.append(a)
    return old


def add_public_to_json_files(directory):
    # 遍历目录
    for filename in os.listdir(directory):
        # 检查文件扩展名是否为.json
        if filename.endswith('.json'):
            filepath = os.path.join(directory, filename)
            print(f"开始处理：{filepath}")

            # 读取JSON文件
            with open(filepath, 'r', encoding='utf-8') as file:
                data = json.load(file)
                print(f"开始处理：{data['a_id']}")

                # 邻居表的节点是否都在定义中
                all_nodes = []
                for k,v in data["sop"]["adjacency_list"].items():
                    all_nodes.extend(v)
                    all_nodes.append(k)
                for one in all_nodes:
                    # print(f"one:{one}")
                    ty,name = one.split(".")
                    if ty == "用户" and name not in data["user_state"]:
                        print(f"node :{one} 不存在")
                        print(f"user_state:{data['user_state']}")
                        data['user_state'].append(name)
                    if ty == "代理" and name not in data["agent_action"]:
                        print(f"node :{one} 不存在")
                        print(f"agent_action:{data['agent_action']}")
                        data['agent_action'].append(name)

                # 添加公共的节点
                data["agent_action"] = add_item(data["agent_action"],agent_action)
                data["user_state"] = add_item(data["user_state"],user_state)
                prof = data["user_profile"].get("画像","")
                if prof:
                    print(f"画像：{prof}")

                filepath = f"{directory}/../define_finish/" + filename.replace(".json",".json")
                # 写回JSON文件
                with open(str(filepath), 'w', encoding='utf-8') as file:
                    json.dump(data, file, ensure_ascii=False, indent=4)
                    print(f"已更新文件 {filepath}")

                # 使用示例

directory = './pre_define'
add_public_to_json_files(directory)