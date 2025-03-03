# 统计已经生成的场景
import json
import os
def show_domain_task(src_directory):
    allfiles = os.listdir(src_directory)
    domain_to_task = {}

    print(f"文件数：{len(allfiles)}")
    for filename in allfiles:
        # 检查是否为json文件
        if filename.lower().endswith('.json'):
            print(f"开始统计：{filename}")

            name_split = filename.split("-")
            domain = name_split[0]
            task_name = name_split[1].split(".")[0]
            if domain in domain_to_task and task_name not in domain_to_task[domain]:
                domain_to_task[domain].append(task_name)
            else:
                domain_to_task[domain] = [task_name]
        else:
            print(f"非json：{filename}")

    print(f"domian to task:\n{json.dumps(domain_to_task,ensure_ascii=False)}")
    print(len(domain_to_task))
    for k,v in domain_to_task.items():
        k = k.replace("_"," ")

        v = [s.replace("_"," ") for s in v]
        print(f"{k}: {','.join(v)}")


src_directory = "./"
show_domain_task(src_directory)

# 将health preservationhot: product promotion改成 tourism: booking,hot spring promotion
# 将travel改成tourism