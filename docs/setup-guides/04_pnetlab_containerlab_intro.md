
在网络仿真领域，**PNETLab** 和 **ContainerLab** 是目前最顶级的两大工具，但它们的设计哲学和适用场景截然不同。

简单来说：**PNETLab 是加强版的 GNS3/EVE-NG（重度 UI 驱动），而 ContainerLab 是网络界的 Docker（纯代码驱动）。**

---

## 1. PNETLab (Platform for Network Education and Training)

PNETLab 是基于 EVE-NG 开源版深度二次开发的仿真平台，通常以一个**完整的虚拟机**（OVA）形式运行。

### 核心特点：

* **模拟全能型**：支持 **QEMU/KVM**（运行博通 SONiC、华为 CE12800、思科 IOS-XR）、**Docker** 和 **Dynamips**。
* **Web UI 驱动**：所有的拓扑搭建、连线、开机都在浏览器界面完成，非常直观。
* **实验室中心**：内置了一个“实验室商店”，你可以一键下载别人做好的复杂实验拓扑（含配置）。
* **资源占用**：由于它主要运行完整的虚拟机镜像，对 **RAM 和 CPU 内存**要求极高（运行两个 SONiC 节点建议配置 32GB 内存）。

### 适用场景：

* 备考华为 HCIE、思科 CCIE。
* 需要复杂的图形化界面展示。
* 运行不支持容器化的传统网络设备镜像（QCOW2/ISO）。

---

## 2. ContainerLab (CLab)

ContainerLab 是诺基亚（Nokia）发起的开源项目，它不提供虚拟机，而是**直接在 Linux 宿主机上编排 Docker 容器**来构建网络拓扑。

### 核心特点：

* **轻量化（极致性能）**：因为它不运行庞大的虚拟机，而是运行容器化的 NOS（如博通 SONiC 容器版、Nokia SR Linux）。启动 50 个节点可能只需要几秒钟。
* **IaC (基础架构即代码)**：没有 UI 界面。你通过编写一个简单的 **YAML 配置文件**来定义拓扑，然后执行一条命令 `containerlab deploy` 即可生成整个网络。
* **DevOps 友好**：完美集成 CI/CD 流水线，适合测试自动化脚本、Ansible 剧本。
* **可视化**：虽然没有搭建界面，但它可以生成拓扑图（通过 Graph 模块）。

### 适用场景：

* **现代数据中心实验**（博通 SONiC 的最佳拍档）。
* 大规模网络模拟（100+ 节点）。
* 自动化开发、DevOps 流程测试。

---

## 3. PNETLab vs ContainerLab 对比表

| 特性 | PNETLab | ContainerLab |
| --- | --- | --- |
| **形态** | 庞大的虚拟机 (OVA) | 轻量级 Linux 二进制工具 |
| **操作方式** | 鼠标拖拽 (Web UI) | 编写 YAML 配置文件 (CLI) |
| **核心引擎** | KVM / QEMU | Docker / Containerd |
| **资源消耗** | 极高 (每个节点分配独立内存) | 极低 (共享宿主机内核) |
| **SONiC 支持** | 支持 Broadcom VirtualSwitch (QEMU) | 支持 SONiC-Cloud (Docker) |
| **华为支持** | 完美支持 CE12800 / NE40E | 较难 (需将镜像容器化) |

---

## 4. 你的博通 SONiC 实验该选哪个？

* **选 PNETLab 的理由**：
如果你习惯了 GNS3 的操作逻辑，且希望能在一个界面里把 **博通 SONiC** 和 **华为 eNSP 镜像（CE12800）** 连在一起。PNETLab 就像一个大容器，可以把所有不同厂商的虚拟机装在一起。
* **选 ContainerLab 的理由**：
如果你想深入研究 **博通官方推荐的测试环境**。博通官方 GitHub 上的很多 SONiC 示例都是基于 ContainerLab 的。如果你打算学习 Python/Ansible 自动化配置 10 台以上的 SONiC 交换机，ContainerLab 的效率远超 PNETLab。

---

## 5. 总结：两者的混搭关系

实际上，很多高级玩家会**在 PNETLab 中安装一个轻量级的 Linux 节点，然后在该节点里运行 ContainerLab**。

* **PNETLab** 负责“大环境”和传统设备（华为/思科）。
* **ContainerLab** 在其内部负责快速生成大规模的 SONiC 集群。

**你想尝试用 YAML 代码来“一键部署”你的 BGP 拓扑，还是继续在 Web UI 中手动连线？**