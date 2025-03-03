import os
import json

from utils.util import count_json_by_letter


def calculate_unique_path_ratio(src_directory):
    path_values = []

    # Step 2: 遍历src目录下的所有JSON文件
    for root, dirs, files in os.walk(src_directory):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as json_file:
                    try:
                        data = json.load(json_file)
                        # Step 3: 读取"path"字段的值
                        if 'scence' in data:
                            full_path = data['scence']["full_path"]
                            path_values.append(str(full_path))
                    except json.JSONDecodeError:
                        print(f"Error decoding JSON from file: {file_path}")

    # Step 4: 计算非重复值的数量
    unique_paths = set(path_values)
    total_paths = len(path_values)
    print(f"total_paths:{total_paths}")

    if total_paths == 0:
        return 0

    # Step 5: 计算非重复值的占比
    unique_ratio = len(unique_paths) / total_paths

    return unique_ratio


# 使用示例
src_dir = './dialogue_scences'  # 假设我们的源目录是当前目录下的src文件夹
src_dir = '/Users/logen/Public/人工智能/research/TOD-23/dataset_v2/tasks/step_2_annotate_scence/dialogue_scences'
ratio = calculate_unique_path_ratio(src_dir)
print(f"The unique path ratio is: {ratio}")

# 统计已经生成的场景
src_directory = '/Users/logen/Public/人工智能/research/TOD-23/dataset_v2/tasks/step_2_annotate_scence/dialogue_scences'  # 替换为实际的目录路径
task_counts, total_count = count_json_by_letter(src_directory)
print("Letter counts:", task_counts)
print("Total JSON files:", total_count)

tasks = len(task_counts.keys())
print(f"domain len:{tasks}")
