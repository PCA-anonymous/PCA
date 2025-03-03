import copy
import json
import os
import random
import uuid

from tqdm import tqdm

from llm.openai_model import GPTCompletionModel
from utils.files import list_save_to_excel
from utils.util import extract_json_from_markdown, get_user_profile, validate_path, read_pairwise

# gpt = GPTCompletionModel(model="gpt-4-1106-preview", temperature=0.7, top_p=0.8)

# gpt-4o-2024-05-13
gpt = GPTCompletionModel(model="gpt-4o-2024-05-13", temperature=0.7, top_p=0.8)

# gpt_client = GPTCompletionModel(model="gpt-3.5-turbo")

prompt = """
你是一名资深业务员，通过与用户对话帮助用户办理业务。
现在，由于培训新业务员需要，请你充当编剧，根据下面提供的"对话任务信息"和"用户信息"，和代理与用户在该任务上的"完整对话路径"一一编写符合双方角色的对话话术。

下面是任务相关信息
"对话任务信息": {conversation_profile},

"用户信息": {user_profile},

"完整对话路径"：{full_path}

请基于"对话任务信息"和"用户信息"，为"完整对话路径"一一编写符合双方角色的对话话术，形成一通完整的对话。

请务必遵循下面要求：
1.请直接在"完整对话路径"的每个节点名后面拼接你编导的"话术"，两者用"|"符号隔开。例如："用户.考虑一下|明白了，我再考虑一下。"
2.禁止添加或删除或改变任意一个原始节点
2.完整输出格式与"完整对话路径"保持一致，即用json的字符串数组输出，如["代理.礼貌结束|感谢您的配合，祝您生活愉快！","用户.结束|好的，拜拜！"]

请输出你添加话术后的"完整对话路径"：
"""




def add_dialogue_to_json_files(directory):
    # 遍历目录
    files = os.listdir(directory)
    files = sorted(files)

    files_finished = os.listdir(f"./one_file_one_dialogue")

    dialogues = []
    all_dialogues = []
    all_prompts_labels = []
    num = 0
    need = 10000

    for filename in files:
        # 检查文件扩展名是否为.json
        if not filename.endswith('.json'):
            continue

        # 已经生成的
        if filename.replace("-scence_", f"-dialogue_") in files_finished:
            print(f"跳过已经生成对话的场景：{filename}")
            continue

        print(f"开始对话的场景：{filename}")

        filepath = os.path.join(directory, filename)

        # 读取JSON文件
        # 一个文件一通对话
        with open(filepath, 'r', encoding='utf-8') as file:
            data = json.load(file)
            origin_json = copy.deepcopy(data)

            conversation_profile = data["conversation_profile"]
            user_profile: dict = data["user_profile"]

            full_path = data["scence"]["full_path"]
            session_id = data["scence"]["session_id"]
            query = prompt.format(conversation_profile=conversation_profile,
                                  user_profile=user_profile,
                                  full_path=full_path
                                  )
            try:
                ans = gpt.generate(query).text[0]
                full_path_dialogue = extract_json_from_markdown(ans)[0]
                print(f"主干路径：{full_path}")
                print(f"主干路径加对话：{full_path_dialogue}")
            except Exception as e:
                print(e)
                continue

            # 组成一轮对话
            turns = read_pairwise(full_path_dialogue)
            one_dialogue = {"scene": full_path, "prompt":query,"dialogues": []}
            one_dialogue_excel = []
            try:
                for a, u in turns:
                    print(f"===>代理：{a}")
                    print(f"===>用户：{u}")

                    if "代理." not in a or "用户." not in u:
                        print(f"当前轮错误xxxxxxxxxxxxxxxxxxxxxxxxxxx")
                        continue

                    node_a, agent_script = str(a).split("|")
                    agent_action = str(node_a).split(".")[1]

                    node_u, user_script = str(u).split("|")
                    user_action = str(node_u).split(".")[1]

                    # header = ["prompt", "scene", "role", "script","script_annotation","action","action_annotation","task","a_id","session_id"]
                    one_dialogue_excel.append(
                        [query, full_path, "Agent", agent_script, agent_script, agent_action, agent_action,
                         filename, data["a_id"], session_id])
                    one_dialogue_excel.append(
                        [query, full_path, "User", user_script, user_script, user_action, user_action,
                         filename, data["a_id"], session_id])

                    one_dialogue["dialogues"].append(
                        {
                            "session_id": session_id,
                            "role": "Agent", "script": agent_script, "script_annotation": agent_script,
                            "action": agent_action,
                            "action_annotation": agent_action,
                            "a_id": data["a_id"]
                        })

                    one_dialogue["dialogues"].append(
                        {
                            "session_id": session_id, "role": "User", "script": user_script,
                            "script_annotation": user_script, "action": user_action,
                            "action_annotation": user_action, "a_id": data["a_id"]
                        })

            except Exception as e:
                print(e)
                continue

            dialogues.append(data)
            all_dialogues.append(copy.deepcopy(data))
            all_prompts_labels.extend(one_dialogue_excel)

            data["dialogue"] = one_dialogue
            filepath = f"./one_file_one_dialogue/" + filename.replace("-scence_", f"-dialogue_")

            # 一通对话一个json文件
            with open(str(filepath), 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
                print(f"已更新文件 {filepath}")

        # 过一段时间写出一次
        # 写出预测记录用于标注
        if len(dialogues) == 100:
            header = ["prompt", "scene", "role", "script","script_annotation","action","action_annotation","task","a_id","session_id"]
            # header = ["prompt", "scene", "role", "script", "script_annotation", "action", "action_annotation", "task","annotation"]
            excel_path = f"./dialogue_excel_unlabel/dialogues_{num*100}_{num*100 + 100}"
            list_save_to_excel(data=all_prompts_labels, header=header, output=excel_path)

            filepath = f"./dialogue_json_unlabel/dialogues_{num*100}_{num*100 + 100}.json"
            # 写回JSON文件
            with open(str(filepath), 'w', encoding='utf-8') as file:
                json.dump(dialogues, file, ensure_ascii=False, indent=4)
                print(f"已更新文件 {filepath}")

            num = num + 1
            all_prompts_labels.clear()
            dialogues.clear()

        if len(all_dialogues) >= need:
            break

    # 写出剩余的部分
    header = ["prompt", "scene", "role", "script", "script_annotation", "action", "action_annotation", "task", "a_id",
              "session_id"]
    # header = ["prompt", "scene", "role", "script", "script_annotation", "action", "action_annotation", "task","annotation"]
    excel_path = f"./dialogue_excel_unlabel/dialogues_{num * 100}_{num * 100 + 100}"
    list_save_to_excel(data=all_prompts_labels, header=header, output=excel_path)
    all_prompts_labels.clear()

    filepath = f"./dialogue_json_unlabel/dialogues_{num * 100}_{num * 100 + 100}.json"
    # 写回JSON文件
    with open(str(filepath), 'w', encoding='utf-8') as file:
        json.dump(dialogues, file, ensure_ascii=False, indent=4)
        print(f"已更新文件 {filepath}")



directory = '/Users/logen/Public/人工智能/research/TOD-23/dataset_v2/tasks/step_2_annotate_scence/dialogue_scences/'
add_dialogue_to_json_files(directory)
