import json
import os

from utils.util import searchpaths


all_paths = []
domains = []
tasks = []

all_sops = []
def add_paths_to_json_files(directory):
    # 遍历目录
    for filename in os.listdir(directory):
        # 检查文件扩展名是否为.json
        if filename.endswith('.json'):
            filepath = os.path.join(directory, filename)
            all_sops.append(filename)

            # 读取JSON文件
            with open(filepath, 'r', encoding='utf-8') as file:
                data = json.load(file)
                print(f"开始处理：{filepath}")
                paths = searchpaths(graph=data["sop"]["adjacency_list"],
                                                   start="代理.开始",
                                                   target="代理.礼貌结束",
                                                   cut=50)

                data["sop"]["paths"] = paths
                data["sop"]["path_count"] = len(paths)
                print(f"{filename} path_count:{len(paths)}")
                all_paths.extend(paths)

                domain = filename.split("-")[0]
                task = filename.split("-")[1].replace(".json","")
                data["domain"] = domain
                data["task"] = task
                domains.append(domain)
                tasks.append(task)
                print(f"domain:{domain} task:{task}")

                filepath = f"./task_add_paths/" + filename.replace(".json",".json")
                # 写回JSON文件
                with open(str(filepath), 'w', encoding='utf-8') as file:
                    json.dump(data, file, ensure_ascii=False, indent=4)
                    print(f"已更新文件 {filepath}")

                # 使用示例

directory = './../step_1_define_task/define_finish'
add_paths_to_json_files(directory)

print(f"all sop:{len(all_sops)}")
print(f"all paths:{len(all_paths)}")
print(f"all domain:{domains}")
print(f"all task:{tasks}")
print(f"all domain:{len(domains)}")
print(f"all task:{len(tasks)}")

print(f"all domain:{len(list(set(domains)))}")
print(f"all task:{len(list(set(tasks)))}")
