# GNS3 SONiC Labs 🚀

这是一个基于 GNS3 和 SONiC (Software for Open Networking in the Cloud) 的 BGP 协议自动化实验框架。

## 🌟 项目亮点
- **自动化部署**：通过 Python 脚本实现多节点配置的一键同步。
- **全流程验证**：脚本自动触发 BGP 邻居建立、业务流量测试及接口故障模拟。
- **精准抓包**：自动在远程节点启动 tcpdump，并根据实验名称分类下载 `.pcap` 结果。

## 🛠️ 环境要求
- GNS3 2.2+
- SONiC-VS 镜像
- Python 3.7+ (依赖 Paramiko 库)

## 🚀 快速开始

### 1. 初始化实验环境
在根目录运行，为新的实验创建规范化目录：
```bash
python init_lab.py