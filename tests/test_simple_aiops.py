#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple-AiOps 测试用例
"""

import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simple_aiops import SimpleAiOps


class TestSimpleAiOps(unittest.TestCase):
    """核心功能测试"""

    def test_yaml_extraction(self):
        """测试 YAML 提取功能"""
        ops = SimpleAiOps.__new__(SimpleAiOps)
        ops.logger = None

        # 测试带 markdown 代码块
        response = """这是一个解释
```yaml
---
- name: test
  hosts: all
```"""
        result = ops._extract_yaml(response)
        self.assertTrue(result.startswith("- name: test"))

        # 测试纯 YAML
        pure_yaml = "- name: pure\n  hosts: all"
        result2 = ops._extract_yaml(pure_yaml)
        self.assertEqual(result2, pure_yaml)

    def test_filename_generation(self):
        """测试文件名生成"""
        ops = SimpleAiOps.__new__(SimpleAiOps)
        ops.logger = None

        short_input = "巡检磁盘"
        long_input = "这是一个非常长的需求描述用来测试文件名截取功能是否正常工作"

        short_result = ops._generate_filename(short_input)
        long_result = ops._generate_filename(long_input)

        self.assertTrue(short_result.startswith("ai_check_"))
        self.assertTrue(short_result.endswith(".yml"))
        self.assertTrue(len(long_result) <= 60)  # 文件名不应过长


class TestPrompt(unittest.TestCase):
    """Prompt 测试"""

    def test_prompt_loading(self):
        """测试 Prompt 模板加载"""
        ops = SimpleAiOps.__new__(SimpleAiOps)
        ops.logger = None

        prompt = ops._load_prompt()
        self.assertIn("{user_input}", prompt)
        self.assertIn("Ansible", prompt)


if __name__ == "__main__":
    unittest.main()
