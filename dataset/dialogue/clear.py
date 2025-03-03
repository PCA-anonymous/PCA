import os
import json


def remove_scene_from_dialogue():
    # 获取当前文件夹路径
    current_directory = os.getcwd()

    # 遍历当前文件夹下的所有文件
    for filename in os.listdir(current_directory):
        # 检查文件是否是 JSON 文件
        if filename.endswith('.json'):
            file_path = os.path.join(current_directory, filename)

            # 读取 JSON 文件
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 检查并删除 dialogue 中的 scene 字段
            if 'dialogue' in data and 'scene' in data['dialogue']:
                del data['dialogue']['scene']

            # 将修改后的数据保存为同名文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)


# 调用函数
remove_scene_from_dialogue()
