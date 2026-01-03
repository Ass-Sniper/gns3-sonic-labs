
# SONiC BGP 基础路由实验手册 (管理网与业务配置已整合)

本手册详细介绍了如何在两台 Broadcom SONiC 交换机之间建立 eBGP 邻居，并实现 Loopback 地址互通，同时解决了 Web UI 下的连线占用与管理 IP 冲突问题。

## 1. 实验拓扑与规划

* **物理连接**: `gns3-sonic-1` [e0]  [e0] `gns3-sonic-2` (内部标识为 Ethernet0)
* **管理平面 (通过 Mgmt-Switch 中转)**:
* **宿主机**: 192.168.100.1
* **GNS3 VM**: 192.168.100.103
* **gns3-sonic-1**: **192.168.100.201**
* **gns3-sonic-2**: **192.168.100.202**



| 节点名称 | 本地 AS | Ethernet0 IP (互联) | Loopback IP (业务) |
| --- | --- | --- | --- |
| **gns3-sonic-1** | 65001 | 10.1.1.1/30 | 1.1.1.1/32 |
| **gns3-sonic-2** | 65002 | 10.1.1.2/30 | 2.2.2.2/32 |

---

## 2. 节点 1 配置 (gns3-sonic-1)

### A. 管理 IP 变更 (Console 执行)

若存在冲突，请在 Console 强制修改并**立即保存**：

```bash
sudo config interface ip remove eth0 192.168.100.102/24
sudo config interface ip add eth0 192.168.100.201/24 192.168.100.1
sudo config save -y

```

### B. 业务配置 (通过 SSH 192.168.100.201 登录)

```bash
# 1. 配置业务接口 IP
sudo config interface ip add Ethernet0 10.1.1.1/30

# 2. 配置 Loopback 接口
sudo config loopback add Loopback0
sudo config interface ip add Loopback0 1.1.1.1/32

# 3. 配置 BGP 协议
sudo config bgp startup-tsa disable
sudo config bgp add local-asn 65001
sudo config bgp add neighbor 10.1.1.2 65002

# 4. 关键：持久化配置
sudo config save -y

```

**系统自检 (日志参考):**

```text
admin@sonic:~$ show ip interfaces
Interface    IPv4 address/mask    Admin/Oper    Flags
-----------  -------------------  ------------  -------
eth0         192.168.100.201/24   up/up         N/A

admin@sonic:~$ docker ps | grep bgp
7b2aec76a72d  docker-fpm-frr:latest  "/usr/bin/supervisord"  Up About an hour  bgp

```

---

## 3. 节点 2 配置 (gns3-sonic-2)

### A. 管理 IP 变更 (Console 执行)

```bash
sudo config interface ip remove eth0 192.168.100.103/24
sudo config interface ip add eth0 192.168.100.202/24 192.168.100.1
sudo config save -y

```

### B. 业务配置 (通过 SSH 192.168.100.202 登录)

```bash
# 1. 配置业务接口 IP
sudo config interface ip add Ethernet0 10.1.1.2/30

# 2. 配置 Loopback 接口
sudo config loopback add Loopback0
sudo config interface ip add Loopback0 2.2.2.2/32

# 3. 配置 BGP 协议
# 如果你想启动所有 BGP 实例
sudo config bgp startup all
sudo config bgp add local-asn 65002
sudo config bgp add neighbor 10.1.1.1 65001

# 4. 关键：持久化配置
sudo config save -y

```

---

## 4. 实验验证与核心维护

### A. 检查 BGP 邻居状态

```bash
show ip bgp summary

```

* **成功标志**: `State/PfxRcd` 列显示数字（如 `1`）。

### B. 查看 BGP 路由表

```bash
show ip route bgp

```

> 预期输出：`B 2.2.2.2/32 [20/0] via 10.1.1.2, Ethernet0, ...`

### C. 连通性测试 (带源 Ping)

```bash
# 在 sonic-1 上执行
ping 2.2.2.2 -I 1.1.1.1

```

---

## 5. Web UI 连线修改规范 (重要)

在 GNS3 Web UI 中，如果需要删除或更换线路，请务必执行以下步骤防止配置丢失：

1. **保存**: `sudo config save -y`。
2. **停止**: 在 Web UI 点击 **Stop**。
3. **删线**: 点击连线  垃圾桶图标。
4. **建线**: 连接新端口（如 `Mgmt-Switch` 到 `eth0`）。
5. **启动**: 点击 **Start**。

| 故障排查命令 | 作用 |
| --- | --- |
| `show system-status` | 确认系统是否 Ready |
| `show interface status` | 确认 Ethernet0 物理层是否 Up |
| `ssh-keygen -R <IP>` | **Win10 执行**: 解决更换管理 IP 后的 SSH 指纹报错 |

**💡 提示**: SONiC 的所有 BGP 变更都实时写入 Redis，但必须通过 `sudo config save -y` 才能确保在 GNS3 节点重启或重新连线后配置依然存在。
