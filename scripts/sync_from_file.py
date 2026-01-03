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

def run_sync(ip, host_conf, common):
    print(f"\n>>> 正在同步节点: {ip}")
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
        
        # 组装 BGP 配置命令
        bgp_cmds = [
            f"sudo vtysh -c 'conf t' -c 'router bgp {host_conf['as']}' "
            f"-c 'bgp router_id {host_conf['router_id']}' "
            f"-c 'neighbor {host_conf['neighbor']} remote-as {host_conf['remote_as']}' "
            f"-c 'address-family ipv4 unicast' -c 'network {host_conf['network']}' "
            f"-c 'exit' -c 'exit' -c 'write memory'",
            "sudo config save -y"
        ]

        for cmd in bgp_cmds:
            stdin, stdout, stderr = client.exec_command(cmd)
            if stdout.channel.recv_exit_status() == 0:
                print(f" [OK] 命令下发成功")
            else:
                print(f" [ERR] 报错: {stderr.read().decode()}")
            time.sleep(common["cmd_delay"])

    except Exception as e:
        print(f" [! ] 连接失败 {ip}: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("\n使用错误！请指定配置文件名。")
        print("用法示例: python sync_from_file.py inventory.json")
        sys.exit(1)

    config_file = sys.argv[1] # 获取命令行传入的第一个参数
    
    if os.path.exists(config_file):
        print(f"--- 正在加载配置: {config_file} ---")
        data = load_inventory(config_file)
        common_params = data["common"]
        nodes_list = data["nodes"]

        for ip, host_conf in nodes_list.items():
            run_sync(ip, host_conf, common_params)
            
        print("\n--- 任务全部完成 ---")
    else:
        print(f"错误: 找不到文件 '{config_file}'")