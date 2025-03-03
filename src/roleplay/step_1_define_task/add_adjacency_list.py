import json
import os
import uuid

import os

# 获取当前工作目录的完整路径
from utils.util import extract_json_from_markdown

current_path = os.getcwd()

# 从完整路径中分割出文件夹名称
folder_name = os.path.basename(current_path)

print("当前文件夹名称:", folder_name)

from llm.openai_model import GPTCompletionModel

# gpt = GPTCompletionModel(model="gpt-3.5-turbo")
# gpt = GPTCompletionModel(model="gpt-4-1106-preview", temperature=0.7, top_p=0.8)
# gpt-4o-2024-05-13
gpt = GPTCompletionModel(model="gpt-4o-2024-05-13", temperature=0.7, top_p=0.8)


prompt = """请将下面Mermaid代码表示的图转成json格式的临接表。 
要求： 
1.Mermaid中的线条节点也是图的正常节点，例如"|用户.是本人|"代表节点"用户.是本人"，节点名必须去掉竖线"|" 
2.邻接表需要包含所有涉及的节点和它对应的相邻节点，如果相邻节点为空，则为空[] 

例如：
"mermaid": "graph TD\n    代理.开始 --> 代理.核对身份\n    代理.核对身份 --> |用户.是本人| 代理.介绍激活活动\n    代理.核对身份 --> |用户.非本人| 代理.礼貌结束\n    代理.介绍激活活动 --> |用户.明确同意| 代理.请求设置交易密码\n    代理.请求设置交易密码 --> |用户.提供密码合法| 代理.告知激活成功\n    代理.请求设置交易密码 --> |用户.提供密码不合法| 代理.请求设置交易密码\n    代理.介绍激活活动 --> |用户.明确拒绝| 代理.礼貌结束\n    代理.告知激活成功 --> 代理.礼貌结束",

对应邻接表json为：
{{
    "代理.开始": [
      "代理.核对身份"
    ],
    "代理.核对身份": [
      "用户.是本人",
      "用户.非本人"
    ],
    "用户.是本人": [
      "代理.介绍激活活动"
    ],
    "代理.介绍激活活动": [
      "用户.明确同意",
      "用户.明确拒绝"
    ],
    "用户.非本人": [
      "代理.礼貌结束"
    ],
    "用户.明确同意": [
      "代理.请求设置交易密码"
    ],
    "代理.请求设置交易密码": [
      "用户.提供密码合法",
      "用户.提供密码不合法"
    ],
    "用户.提供密码合法": [
      "代理.告知激活成功"
    ],
    "用户.提供密码不合法": [
      "代理.请求设置交易密码"
    ],
    "用户.明确拒绝": [
      "代理.礼貌结束"
    ],
    "代理.礼貌结束": [],
    "代理.告知激活成功": [
        "代理.礼貌结束"
    ]
}}

让我们开始吧
"mermaid": {mermaid}

对应邻接表json为：
"""


def show_mermaid(directory):
    # 遍历目录
    for filename in os.listdir(directory):
        # 检查文件扩展名是否为.json
        if filename.endswith('.json'):
            filepath = os.path.join(directory, filename)

            # 读取JSON文件
            with open(filepath, 'r', encoding='utf-8') as file:
                data = json.load(file)
                print(f"{filepath}")
                data["a_id"] = folder_name + uuid.uuid4().hex[:5]

                mermaid = data["sop"]["mermaid"]
                text = gpt.generate(prompt.format(mermaid=mermaid)).text[0]
                markdown_str = str(text).strip()
                adjacency_list_gpt = extract_json_from_markdown(markdown_str)[0]

                adjacency_list = data["sop"].get("adjacency_list",None)
                if adjacency_list and adjacency_list != adjacency_list_gpt:
                    print(adjacency_list)
                    print(adjacency_list_gpt)
                    break


                filepath = f"/Users/logen/Public/人工智能/research/TOD-23/dataset_v2/tasks/step_1_define_task/pre_define/" + filename.lower()
                # 写回JSON文件
                with open(str(filepath), 'w', encoding='utf-8') as file:
                    json.dump(data, file, ensure_ascii=False, indent=4)
                    print(f"已更新文件 {filepath}")

                # 使用示例

directory = './'
show_mermaid(directory)