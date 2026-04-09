#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simple-AiOps - AI 辅助运维工具
通过 DeepSeek 等模型将自然语言转化为 Ansible Playbooks
"""

import os
import sys
import json
import yaml
import logging
from datetime import datetime

# 配置日志
def setup_logging():
    log_dir = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(
        log_dir,
        f"aiops_{datetime.now().strftime('%Y%m%d')}.log"
    )
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)


class SimpleAiOps:
    """AI 运维助手核心类"""

    def __init__(self, api_key: str = None, base_url: str = None,
                 model: str = "deepseek-chat",
                 os_type: str = "linux"):
        import openai

        # 读取配置
        config = self._load_config()
        self.api_key = api_key or config.get("api_key") or os.getenv("DEEPSEEK_API_KEY")
        self.base_url = base_url or config.get("base_url", "https://api.deepseek.com")
        self.model = model or config.get("model", "deepseek-chat")
        self.os_type = os_type or config.get("os_type", "linux")

        if not self.api_key:
            raise ValueError(
                "API Key 未设置！请在 config.yaml 中配置，或设置环境变量 DEEPSEEK_API_KEY"
            )

        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        self.logger = setup_logging()
        self.logger.info(f"SimpleAiOps 初始化完成，模型: {self.model}")

    def _load_config(self) -> dict:
        """加载配置文件"""
        config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        return {}

    def _load_prompt(self) -> str:
        """加载 Prompt 模板"""
        prompt_path = os.path.join(
            os.path.dirname(__file__),
            "prompts", "ansible.j2"
        )
        if os.path.exists(prompt_path):
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()

        # 默认 Prompt
        return """你是一个资深运维专家，擅长编写 Ansible Playbooks。

请根据以下需求，写一个 Ansible Playbook YAML 文件。

要求：
1. 只返回 YAML 代码，不要说任何废话
2. YAML 必须符合 Ansible 规范，可以直接 ansible-playbook 运行
3. 使用标准 Ansible 模块
4. 如果涉及国产系统（麒麟、统信），请使用兼容模块
5. 包含适当的 tags，方便选择性执行

需求：
{user_input}

只返回 YAML 代码："""

    def _extract_yaml(self, response: str) -> str:
        """从模型返回中提取 YAML 代码"""
        # 移除 markdown 代码块标记
        lines = response.strip().split("\n")
        if lines[0].strip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        yaml_text = "\n".join(lines).strip()

        # 移除可能的解释性文字
        for sep in ["---", "yaml", "YAML"]:
            if yaml_text.startswith(sep):
                yaml_text = yaml_text[len(sep):].strip()
                break

        return yaml_text

    def _generate_filename(self, user_input: str) -> str:
        """生成输出文件名"""
        # 取需求的前20个字符作为标识
        prefix = user_input[:20].replace(" ", "_").replace("/", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"ai_check_{prefix}_{timestamp}.yml"

    def generate(self, user_input: str, output_dir: str = None) -> str:
        """
        根据自然语言需求生成 Ansible Playbook

        Args:
            user_input: 用户的自然语言需求描述
            output_dir: 输出目录，默认为 output/

        Returns:
            生成的 YAML 文件路径
        """
        self.logger.info(f"开始生成 Playbook，需求: {user_input}")

        # 构建 Prompt
        prompt_template = self._load_prompt()
        prompt = prompt_template.format(user_input=user_input)

        # 调用模型
        self.logger.info("正在调用 AI 模型...")
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "你是一个专业的 Ansible 运维工程师，只返回 YAML 代码，不说废话。"
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2048
        )

        content = response.choices[0].message.content
        self.logger.info("模型返回成功")

        # 提取 YAML
        yaml_code = self._extract_yaml(content)

        # 保存文件
        output_dir = output_dir or os.path.join(os.path.dirname(__file__), "output")
        os.makedirs(output_dir, exist_ok=True)

        filename = self._generate_filename(user_input)
        filepath = os.path.join(output_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(yaml_code)

        self.logger.info(f"Playbook 已保存: {filepath}")
        return filepath


def print_banner():
    """打印欢迎banner"""
    banner = """
╔══════════════════════════════════════════════════╗
║           🛠️  Simple-AiOps 智能运维助手            ║
║     DeepSeek 驱动的 Ansible Playbook 生成器        ║
╚══════════════════════════════════════════════════╝
"""
    print(banner)


def interactive_mode():
    """交互式命令行模式"""
    print_banner()

    # 初始化（加载配置中的 API Key）
    try:
        ops = SimpleAiOps()
    except ValueError as e:
        print(f"❌ 配置错误: {e}")
        print("\n请创建 config.yaml 文件，配置你的 API Key：")
        print("1. cp config.example.yaml config.yaml")
        print("2. 编辑 config.yaml，填入 api_key")
        print("3. 或设置环境变量: export DEEPSEEK_API_KEY=your-key")
        return

    print("✅ 初始化成功！\n")
    print("💡 提示：输入你的运维需求，例如：")
    print("   - 巡检所有 Web 服务器的 CPU、内存和磁盘使用情况")
    print("   - 在所有服务器上批量更新 Nginx 到最新版本")
    print("   - 帮我写一个一键部署 Docker 的 Playbook\n")
    print("-" * 50)

    while True:
        try:
            user_input = input("\n📝 请输入运维需求（或 quit 退出）：\n> ").strip()

            if user_input.lower() in ["quit", "exit", "q", "退出"]:
                print("\n👋 再见！")
                break

            if not user_input:
                print("⚠️  请输入有效内容")
                continue

            print("\n🤖 正在生成 Ansible Playbook...")
            filepath = ops.generate(user_input)
            print(f"\n✅ Playbook 已生成！")
            print(f"📄 文件位置: {filepath}\n")

        except KeyboardInterrupt:
            print("\n\n👋 再见！")
            break
        except Exception as e:
            print(f"\n❌ 生成失败: {e}")


if __name__ == "__main__":
    interactive_mode()
