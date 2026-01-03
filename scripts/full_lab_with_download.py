import paramiko
import json
import os
import time
import sys
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

def load_inventory(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def run_full_experiment(config_path):
    # 1. 加载 JSON 并解析路径
    inventory = load_inventory(config_path)
    lab_path = os.path.dirname(config_path)
    lab_name = os.path.basename(lab_path)
    
    # 2. 从新结构中提取数据
    common = inventory["common"]
    nodes = inventory["nodes"]  # 关键：先进入 nodes 这一层
    
    # 获取所有节点 IP
    device_ips = list(nodes.keys())
    if not device_ips:
        print(" [!] 错误：inventory.json 的 nodes 字段中没有发现设备")
        return
    
    # 选取第一个节点进行抓包
    target_ip = device_ips[0]
    node_config = nodes[target_ip]
    
    peer_ip = node_config["neighbor"]
    
    # 3. 构造文件名
    timestamp = time.strftime("%H%M%S")
    remote_pcap = f"/tmp/{lab_name}_{timestamp}.pcap"
    
    # 确保本地 data 目录下有实验子目录
    local_data_dir = os.path.join("data", lab_name)
    if not os.path.exists(local_data_dir):
        os.makedirs(local_data_dir)
    
    local_pcap = os.path.join(local_data_dir, f"{lab_name}_{timestamp}.pcap")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"--- 实验名称: {lab_name} ---")
        print(f"--- 连接节点: {target_ip} ---")
        client.connect(hostname=target_ip, username=common["user"], password=common["pash"], timeout=10)
        
        # [步骤 1-5 逻辑保持不变，但使用 remote_pcap 变量]
        print(f">>> [1/6] 启动远程抓包 (any接口)...")
        capture_cmd = f"sudo stdbuf -oL -eL tcpdump -i any 'tcp port 179 or icmp' -s 0 -U -n -w {remote_pcap} > /dev/null 2>&1 &"
        client.exec_command(capture_cmd)
        time.sleep(2)

        print(f">>> [2/6] 触发 BGP Clear...")
        client.exec_command("sudo vtysh -c 'clear ip bgp *'")
        time.sleep(8)

        print(f">>> [3/6] 发起业务 Ping...")
        stdin, stdout, stderr = client.exec_command(f"ping {peer_ip} -c 5")
        stdout.read() # 等待执行完成

        print(f">>> [4/6] 模拟接口故障...")
        client.exec_command("sudo config interface shutdown Ethernet0")
        time.sleep(2)

        print(f">>> [5/6] 恢复环境并停止抓包...")
        client.exec_command("sudo pkill -f tcpdump")
        client.exec_command("sudo config interface startup Ethernet0")
        time.sleep(2)

        # 6. 下载文件
        abs_local_data_dir = os.path.abspath(os.path.join("data", lab_name))
        if not os.path.exists(abs_local_data_dir):
            os.makedirs(abs_local_data_dir)
            
        local_pcap = os.path.join(abs_local_data_dir, f"{lab_name}_{timestamp}.pcap")

        print(f">>> [6/6] 正在下载抓包到: {local_pcap}")
        sftp = client.open_sftp()
        try:
            # 使用临时文件名下载，避开 VS Code 的实时扫描锁定
            temp_local = local_pcap + ".tmp"
            sftp.get(remote_pcap, temp_local)
            
            # 下载完成后重命名（这在 Windows 上比直接写入更不容易被锁定）
            if os.path.exists(local_pcap):
                os.remove(local_pcap)
            os.rename(temp_local, local_pcap)
            
            print(f"\n[OK] 实验数据已存入: {local_pcap}")
            sftp.remove(remote_pcap)
        except Exception as e:
            print(f"\n[!] VS Code 或系统可能正在占用目录，下载至备用路径...")
            # 实在不行存到根目录，避开 data 层级
            sftp.get(remote_pcap, f"emergency_{timestamp}.pcap")
        finally:
            sftp.close()
        
        print(f"\n[成功] 实验数据已存入: {local_pcap}")

    except Exception as e:
        print(f" [! ] 错误: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python scripts/full_lab_with_download.py <inventory路径>")
        print("示例: python scripts/full_lab_with_download.py labs/01_base_bgp/inventory.json")
    else:
        run_full_experiment(sys.argv[1])