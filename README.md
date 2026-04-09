# 🛠️ Simple-AiOps

> 轻量级 AI 辅助运维工具，通过 DeepSeek 模型将自然语言直接转化为 Ansible Playbooks。

[English](./README.md) | 简体中文

---

## ✨ 功能特点

- 🌐 **自然语言交互**：无需死记硬背 Ansible 语法，直接提需求
- 🇨🇳 **信创环境友好**：支持生成适配银河麒麟、统信等国产系统的运维指令
- 📤 **一键导出**：生成的 YAML 文件自带最佳实践规范
- 🤖 **多模型支持**：DeepSeek / OpenAI / 兼容 OpenAI 接口的模型均可

---

## 📦 快速开始

### 环境要求

- Python 3.10+
- DeepSeek API Key（或其他兼容模型的 API Key）

### 安装

```bash
# 克隆项目
git clone https://github.com/z2675039271-svg/Simple-AiOps.git
cd Simple-AiOps

# 安装依赖
pip install -r requirements.txt
```

### 配置

```bash
# 复制配置文件
cp config.example.yaml config.yaml
```

编辑 `config.yaml`，填入你的 API Key：

```yaml
api:
  provider: "deepseek"          # deepseek / openai / custom
  api_key: "your-api-key-here"  # 填入你的 API Key
  base_url: "https://api.deepseek.com"  # OpenAI 填 https://api.openai.com

target:
  os_type: "linux"             # linux / kirin / uos
  ansible_version: "2.9"
```

### 运行

```bash
python main.py
```

输入你的巡检需求，例如：

```
请帮我生成一个用于巡检 Linux 服务器磁盘空间的 Playbook
```

---

## 📁 项目结构

```
Simple-AiOps/
├── main.py              # 主入口
├── config.example.yaml   # 配置文件模板
├── requirements.txt     # Python 依赖
├── prompts/             # Prompt 模板
│   └── ansible.j2       # Ansible 生成 Prompt
├── output/              # 生成的 Playbook 输出目录
├── logs/                # 日志目录
├── tests/               # 单元测试
└── README.md
```

---

## 🎯 使用示例

### 交互式使用

```
$ python main.py

╔══════════════════════════════════════════════╗
║          Simple-AiOps 智能运维助手             ║
╚══════════════════════════════════════════════╝

请输入你的运维需求（或输入 quit 退出）：
> 帮我巡检所有 Web 服务器的 CPU、内存和磁盘使用情况
🤖 正在生成 Ansible Playbook...

✅ Playbook 已生成！
📄 文件位置: output/server_health_check.yml

继续输入需求（或输入 quit 退出）：
> quit
👋 再见！
```

### 代码调用

```python
from simple_aiops import SimpleAiOps

ops = SimpleAiOps(api_key="your-deepseek-key")
result = ops.generate(
    user_input="巡检所有 Linux 服务器的磁盘空间"
)
print(result)  # 返回生成的 Playbook 内容
```

---

## 🛡️ 安全说明

- **API Key 安全**：请勿将 `config.yaml` 或包含真实 Key 的配置文件提交到 GitHub
- **建议**：使用环境变量存储 API Key：
  ```bash
  export DEEPSEEK_API_KEY="your-key"
  ```

---

## 🔧 扩展方向

- [ ] 加入 RAG 知识库，学习历史巡检经验
- [ ] 支持更多运维场景（Docker、K8s）
- [ ] Web 界面
- [ ] 一键执行生成的 Playbook

---

## 📄 License

MIT License

---

## 👤 作者

- GitHub: [@z2675039271-svg](https://github.com/z2675039271-svg)
- Email: z2675039271@gmail.com
