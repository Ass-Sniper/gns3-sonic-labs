import paramiko
import json
import os
import time
import sys
import warnings

# 忽略 Python 3.7 加密警告
warnings.filterwarnings("ignore", category=DeprecationWarning)

def load_inventory(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def import_raw_config(ip, info, common):
    # 从 JSON 中获取该 IP 对应的配置文件名
    # 如果 JSON 里没写文件名，默认尝试 config_IP.conf
    conf_file = info.get("conf_file", f"config_{ip.split('.')[-1]}.conf")
    
    if not os.path.exists(conf_file):
        print(f" [跳过] {ip}: 找不到预定义的配置文件 {conf_file}")
        return

    print(f"\n>>> 正在导入文本配置到: {ip} (源文件: {conf_file})")
    
    # 读取并过滤 .conf 文件内容
    with open(conf_file, 'r') as f:
        lines = [l.strip() for l in f.readlines() if l.strip() and not l.startswith('!')]

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(
            hostname=ip,
            username=common["user"],
            password=common["pash"],
            port=common["port"],
            timeout=common["timeout"]
        )
        
        # 开启交互式 Shell
        shell = client.invoke_shell()
        time.sleep(1)
        
        shell.send("sudo vtysh\n")
        shell.send("conf t\n")
        time.sleep(0.5)

        for line in lines:
            shell.send(line + "\n")
            time.sleep(common["cmd_delay"])
            print(f"  发送: {line}")
        
        shell.send("end\n")
        shell.send("write memory\n")
        shell.send("exit\n")
        time.sleep(1)

        # SONiC 系统保存
        print(f" [提示] 执行系统级持久化...")
        client.exec_command("sudo config save -y")
        print(f" [成功] {ip} 配置导入完成。")

    except Exception as e:
        print(f" [! ] 导入失败 {ip}: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\n使用错误！请指定环境清单 JSON 文件。")
        print("用法: python import_from_file.py inventory.json")
        sys.exit(1)

    inventory_file = sys.argv[1]
    
    if os.path.exists(inventory_file):
        data = load_inventory(inventory_file)
        common_params = data["common"]
        nodes_list = data["nodes"]

        for ip, info in nodes_list.items():
            import_raw_config(ip, info, common_params)
            
        print("\n--- 所有文本配置导入任务完成 ---")
    else:
        print(f"错误: 找不到文件 '{inventory_file}'")