# -*- coding: utf-8 -*-

import os
from datetime import datetime

def save_text_file(directory: str, filename: str, content: str, add_timestamp: bool = True):
    """
    将文本内容保存到指定文件。

    Args:
        directory (str): 保存目录。
        filename (str): 文件名 (不含扩展名)。
        content (str): 要保存的内容。
        add_timestamp (bool): 是否在文件名中添加时间戳。
    """
    try:
        os.makedirs(directory, exist_ok=True)

        if add_timestamp:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            final_filename = f"{filename}_{timestamp}.txt"
        else:
            final_filename = filename

        filepath = os.path.join(directory, final_filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"  - 内容已保存到: {filepath}")
        return filepath
    except IOError as e:
        print(f"❌ 保存文件 '{filepath}' 失败: {e}")
        return None

def save_markdown_report(directory: str, prefix: str, content: str) -> str:
    """将最终的Markdown报告保存到带时间戳的文件。"""
    try:
        os.makedirs(directory, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{prefix}_{timestamp}.md"
        filepath = os.path.join(directory, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\n📄 报告已成功保存至: {filepath}")
        return filepath
    except IOError as e:
        print(f"❌ 保存最终报告失败: {e}")
        return ""