import os
import shutil
import sys
from datetime import datetime

def organize_lab(lab_name):
    date_str = datetime.now().strftime("%Y%m%d")
    data_dir = os.path.join("data", f"{date_str}_{lab_name}")
    
    # 创建标准目录结构
    for folder in ["scripts", "labs", "data", data_dir]:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f" [+] 创建目录: {folder}")

    # 1. 归档 PCAP 抓包文件
    for file in os.listdir("."):
        if file.endswith(".pcap"):
            try:
                shutil.move(file, os.path.join(data_dir, file))
                print(f" [OK] 抓包归档: {file} -> {data_dir}")
            except PermissionError:
                print(f" [!] 错误: 无法移动 {file}，请先关闭 Wireshark！")

    # 2. 归档脚本文件 (第一次初始化用)
    scripts_to_move = [
        "sync_from_file.py", "import_from_file.py", 
        "check_sonic.py", "full_lab_with_download.py"
    ]
    for script in scripts_to_move:
        if os.path.exists(script):
            shutil.move(script, os.path.join("scripts", script))
            print(f" [OK] 脚本归档: {script} -> scripts/")

    # 3. 归档初始配置文件
    initial_lab_dir = os.path.join("labs", "01_base_bgp")
    if not os.path.exists(initial_lab_dir):
        os.makedirs(initial_lab_dir)
        
    configs = ["inventory.json", "config_201.conf", "config_202.conf"]
    for cfg in configs:
        if os.path.exists(cfg):
            shutil.move(cfg, os.path.join(initial_lab_dir, cfg))
            print(f" [OK] 配置归档: {cfg} -> {initial_lab_dir}/")

if __name__ == "__main__":
    # 支持命令行参数，如果没有参数则弹出提示
    if len(sys.argv) > 1:
        name = sys.argv[1]
    else:
        name = input("请输入本次实验名称: ")
    
    organize_lab(name)
    print("\n>>> 目录整理完成！")