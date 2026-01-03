import paramiko
import json
import os
import sys
import warnings

# 忽略 Python 3.7 警告
warnings.filterwarnings("ignore", category=DeprecationWarning)

def load_inventory(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def check_node_status(ip, common):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    status_report = {"ip": ip, "bgp_state": "Unknown", "routes": "0"}
    
    try:
        client.connect(
            hostname=ip,
            username=common["user"],
            password=common["pash"],
            port=common["port"],
            timeout=5
        )
        
        # 1. 检查 BGP 邻居状态
        stdin, stdout, stderr = client.exec_command("sudo vtysh -c 'show ip bgp summary'")
        bgp_output = stdout.read().decode()
        
        # 简单的逻辑解析：寻找 Established 标志
        # 在 FRR/SONiC 中，最后一行如果有数字（PfxRcd）代表已建立，如果是单词（Active/Idle）代表没通
        for line in bgp_output.splitlines():
            if "10.1.1." in line: # 匹配邻居 IP 段
                parts = line.split()
                state_val = parts[-1]
                status_report["bgp_state"] = "Established" if state_val.isdigit() else state_val
        
        # 2. 检查学到的 BGP 路由数量
        stdin, stdout, stderr = client.exec_command("sudo vtysh -c 'show ip route bgp'")
        route_output = stdout.read().decode()
        status_report["routes"] = route_output.count('B>') # 统计有效 BGP 路由条数

        client.close()
    except Exception as e:
        status_report["bgp_state"] = f"Error: {str(e)[:20]}"
    
    return status_report

if __name__ == "__main__":
    inventory_file = sys.argv[1] if len(sys.argv) > 1 else "inventory.json"
    
    if os.path.exists(inventory_file):
        data = load_inventory(inventory_file)
        common = data["common"]
        nodes = data["nodes"]

        print("\n" + "="*60)
        print(f"{'Node IP':<18} | {'BGP State':<15} | {'BGP Routes':<10}")
        print("-" * 60)

        for ip in nodes.keys():
            res = check_node_status(ip, common)
            print(f"{res['ip']:<18} | {res['bgp_state']:<15} | {res['routes']:<10}")
        
        print("="*60 + "\n")
    else:
        print(f"找不到配置文件: {inventory_file}")