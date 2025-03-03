import copy
import json
import os
import random
import uuid
from datetime import datetime

from tqdm import tqdm

from llm.openai_model import GPTCompletionModel
from utils.files import list_save_to_excel
from utils.util import extract_json_from_markdown, get_user_profile, validate_path, modify_node_name, \
    count_json_by_letter

# gpt = GPTCompletionModel(model="gpt-4-1106-preview", temperature=0.7, top_p=0.8)

#gpt-4o-2024-05-13
gpt = GPTCompletionModel(model="gpt-4o-2024-05-13", temperature=0.7, top_p=0.8)

# gpt_client = GPTCompletionModel(model="gpt-3.5-turbo")

prompt = """
你是一名资深业务员，通过与用户对话帮助用户办理业务。
现在，请根据下面提供的"对话任务信息"和"用户信息"，结合用于指导对话来办理业务的"标准操作流程"图，为"主干对话路径"添加更多的"用户状态"和"代理动作"形成"完整对话路径"，以更好地模拟该用户与代理完整的对话过程。

下面是任务相关信息
"对话任务信息": {conversation_profile},

"用户信息": {user_profile},

"代理动作": {agent_action},

"用户状态": {user_state},

"标准操作流程": {adjacency_list},

"主干对话路径"：{main_path}

请在上述"主干对话路径"中插入更多的"用户状态"和"代理动作"，以丰富用户可能产生的反应和代理针对用户状态做出的相应的决策动作，形成一通完整的对话。

请务必遵循下面要求：
1.一条完整的对话路径都以"代理.打招呼"开始，以"用户.结束"结束
2.完整对话路径要求"代理动作"和"用户状态"各说一次交替进行，代表一轮对话，禁止一方连续出现两次及以上，请在一轮对话后添加一个"--"用来隔离前后两轮对话，如"主干对话路径"中的["代理.打招呼","代理.介绍活动"]不满足该要求，需要你补充节点以满足该规则，你可以插入一次"用户.打招呼"使其变成["代理.打招呼","用户.打招呼","--","代理.介绍活动"]
3.只需在上述"主干对话路径"补充和插入更多的回合
4.禁止删除"主对话路径"中的任何节点
5.禁止调整"主对话路径"中任何节点的顺序
6.为了控制插入的数量，请仅插入{min_turn}到{max_turn}轮合理的对话
7.插入的对话路径节点只能选自上文定义的"用户状态"和"代理动作"，禁止自己命名
8.当前置节点为"标准操作流程"中的节点时，请尽量从邻接表当前节点的后续节点中选择一个插入
8.输出格式与上文保持一致，即用json的字符串数组输出

下面是两个正确的示例：
"主干对话路径"：
["代理.打招呼","代理.核对身份","用户.不是本人","代理.礼貌结束"]
补充后的json格式的完整对话路径：
```json
["代理.打招呼","用户.打招呼","--","代理.核对身份","用户.不是本人","--","代理.礼貌结束","用户.结束"]
```

"主干对话路径"：
["代理.打招呼","用户.要求订票","代理.核对身份","用户.不是本人","代理.礼貌结束"]
补充后的json格式的完整对话路径：
```json
["代理.打招呼","用户.要求订票","--","代理.核对身份","用户.不是本人","--","代理.礼貌结束","用户.结束"]
```

上面两个示例仅用于说明本任务输出逻辑和格式要求，请忽略其文字含义，下面让我们正式开始：
"主干对话路径"：
{main_path}
补充后的json格式的完整对话路径：
"""



all_scences = []

sample_path_times = 100

one_task_need = 25
need = 1200


def add_paths_to_json_files(directory):
    # 遍历目录
    files = os.listdir(directory)
    files = sorted(files)
    # 统计已经生成的场景
    src_directory = '/Users/logen/Public/人工智能/research/TOD-23/dataset_v2/tasks/step_2_annotate_scence/dialogue_scences'  # 替换为实际的目录路径
    task_counts, total_count = count_json_by_letter(src_directory)
    print("Letter counts:", task_counts)
    print("Total JSON files:", total_count)

    for filename in files:
        # 检查文件扩展名是否为.json
        if not filename.endswith('.json'):
            continue
        first_letter = filename.split(".json")[0]
        one_task_saved = task_counts.get(first_letter, 0)
        if one_task_saved >= one_task_need:
            print(f"跳过task：{first_letter} 生成数量{one_task_saved}超过{one_task_need}")
            continue

        print(f"开始处理task：{filename}")

        filepath = os.path.join(directory, filename)
        one_task_all_scences = []

        # 读取JSON文件
        with open(filepath, 'r', encoding='utf-8') as file:
            data = json.load(file)

            conversation_profile = data["conversation_profile"]
            user_profile:dict = data["user_profile"]
            agent_action = data["agent_action"]
            user_state = data["user_state"]

            paths = data["sop"]["paths"]
            adjacency_list = data["sop"]["adjacency_list"]
            sop_vertex = data["sop"]["vertex"]

            # 使用choices()函数采样，允许重复
            # n = sample_path_times * len(paths)  # 你想要采样的次数
            paths = sorted(paths,key=lambda k:len(k),reverse=False)
            sampled_path1 = random.choices(paths[1:], k=sample_path_times)
            sampled_path2 = random.choices(paths[2:], k=sample_path_times)
            sampled_path3 = sampled_path1 + sampled_path2
            sampled_path = random.choices(sampled_path3, k=sample_path_times)

            print(f"采样path len:{len(sampled_path)}")
            # 缓存校验不通过的main_path，避免重复去生成导致一直失败
            failed_main_paths = set()
            for main_path in sampled_path:
                main_path = copy.deepcopy(main_path)
                if str(main_path) in failed_main_paths:
                    print(f"跳过，当前path失败过：{main_path}")
                    continue

                min_turn, max_turn = random.choices([(1, 3), (1, 4), (2, 4), (2, 5), (3, 6), (5, 9)], k=1)[0]
                print(f"原始画像：{user_profile}")
                prof = get_user_profile()
                user_profile.update(prof)
                print(f"更新画像：{user_profile}")

                # path 代理.开始 替换为 代理.打招呼
                if main_path[0] == "代理.开始":
                    if "代理.打招呼" not in main_path:
                        main_path[0] = "代理.打招呼"
                    else:
                        main_path.pop(0)

                main_path.append("用户.结束")


                query = prompt.format(conversation_profile=conversation_profile,
                                      user_profile=user_profile,
                                      agent_action=agent_action,
                                      user_state=user_state,
                                      adjacency_list=adjacency_list,
                                      main_path=main_path,
                                      min_turn=min_turn, max_turn=max_turn
                                      )
                try:
                    ans = gpt.generate(query).text[0]
                    full_path = extract_json_from_markdown(ans)[0]
                    # 过滤掉生成中的分割轮数符
                    full_path = [i for i in full_path if "." in i]
                    # 如果当前节点和下一个节点角色重复，则仅保留下一个，即去掉下面的情况，救活这通对话
                    #   "代理.打招呼",
                    #   "用户.打招呼",
                    #   "--",
                    #   "用户.要求商品退货",
                    #   "代理.询问订单号",
                    #   "--",
                    #   "用户.提供订单号",
                    #   "代理.核对订单信息",
                    for idx in range(len(full_path)-1):
                        if str(full_path[idx])[:2] == str(full_path[idx+1])[:2]:
                            if full_path[idx] not in sop_vertex:
                                print(f"出现重复角色对话，删除非sop中的那个：{full_path[idx]}")
                                full_path[idx] = ""
                            elif full_path[idx+1] not in sop_vertex:
                                print(f"出现重复角色对话，删除非sop中的那个：{full_path[idx+1]}")
                                full_path[idx+1] = ""

                    full_path = [i for i in full_path if i]


                    # 判断节点名并修正
                    full_path_modidied,errors = modify_node_name(full_path=full_path, user_state=user_state,agent_action=agent_action)

                    print(f"主干路径：{main_path}")
                    print(f"完整路径：{full_path}")
                    print(f"错误信息：{errors}")
                    print(f"修复路径：{full_path_modidied}")

                    validate,idx = validate_path(G=adjacency_list,P=full_path_modidied)

                    data["scence"] = dict()
                    data["scence"]["main_path"] = main_path
                    data["scence"]["full_path"] = full_path_modidied
                    data["scence"]["full_path_before_modidied"] = full_path
                    data["scence"]["full_path_errors"] = errors

                    # 获取当前日期和时间
                    now = datetime.now()
                    # 将日期时间格式化为月日时的字符串连写格式
                    formatted_date = now.strftime("%m%d%H")
                    print(formatted_date)  # 例如：如果当前是2021年12月31日15时，则输出为"123115"

                    session_id = formatted_date + uuid.uuid4().hex[:6]
                    data["scence"]["session_id"] = session_id
                    data["scence"]["validate"] = validate
                    data["scence"]["validate_idx"] = idx

                    all_scences.append(copy.deepcopy(data))

                    # 保存对话场景用于统计
                    filepath = f"./dialogue_scences_log/" + filename.replace(".json", f"-scence_{session_id}.json")
                    # 写回JSON文件
                    with open(str(filepath), 'w', encoding='utf-8') as file:
                        json.dump(data, file, ensure_ascii=False, indent=4)
                        print(f"已更新文件 {filepath}")

                    if not validate:
                        failed_main_paths.add(str(main_path))
                        print(f"路径校验不通过")
                        continue
                except Exception as e:
                    print(e)
                    continue

                # 保存成功的对话场景
                filepath = f"./dialogue_scences/" + filename.replace(".json", f"-scence_{session_id}.json")
                # 写回JSON文件
                with open(str(filepath), 'w', encoding='utf-8') as file:
                    json.dump(data, file, ensure_ascii=False, indent=4)
                    print(f"已更新文件 {filepath}")

                one_task_all_scences.append(data)
                if len(one_task_all_scences) + one_task_saved >= one_task_need:
                    break

                if len(all_scences) >= need:
                    break
        if len(all_scences) >= need:
            break

    # 保存所有的对话场景
    filepath = f"./dialogue_scences_inonefile/" + filename.replace(".json", f"-scence.json")
    # 写回JSON文件
    with open(str(filepath), 'w', encoding='utf-8') as file:
        json.dump(all_scences, file, ensure_ascii=False, indent=4)
        print(f"已更新文件 {filepath}")



directory = './task_add_paths/'
add_paths_to_json_files(directory)
