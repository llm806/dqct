# -*- coding: utf-8 -*-

"""
pandas
numpy
openai
python-dotenv
openpyxl
pyyaml
"""

import yaml
import os
from typing import Dict, Any

from src.core.workflow import execute_comparison_workflow, execute_historical_workflow

def load_config(path: str = 'config.yaml') -> Dict[str, Any]:
    """加载YAML配置文件。"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"❌ 配置文件未找到: {path}")
        return {}
    except Exception as e:
        print(f"❌ 加载配置文件失败: {e}")
        return {}

def main():
    """项目主入口函数。"""
    # 1. 加载配置
    config = load_config()
    if not config:
        print("🔴 无法加载配置，程序终止")
        return

    # 2. 根据配置准备分析任务列表
    analysis_tasks = []
    mode = config.get('active_mode', 'FILES')

    print("--- 配置检查 ---")
    if mode == 'FILES':
        files_to_compare = config.get('data_sources', {}).get('files', [])
        print(f"ℹ️ 模式: 【文件对比】")
        print(f"📚 文件列表: {', '.join([os.path.basename(f) for f in files_to_compare])}")
        analysis_tasks = [{'file': f} for f in files_to_compare]
    elif mode == 'SHEETS':
        sheets_config = config.get('data_sources', {}).get('sheets_config', {})
        file_path = sheets_config.get('file_path')
        sheet_names = sheets_config.get('sheet_names')
        if file_path and sheet_names:
            print(f"ℹ️ 模式: 【工作表对比】")
            print(f"📂 文件: {os.path.basename(file_path)}")
            print(f"📑 工作表顺序: {', '.join(sheet_names)}")
            analysis_tasks = [{'file': file_path, 'sheet': s} for s in sheet_names]
        else:
            print("❌ 'SHEETS' 模式配置不完整。")
    else:
        print(f"❌ 未知的对比模式: '{mode}'。")
    print("------------------\n")

    if not analysis_tasks:
        print("🔴 未执行分析，因为没有有效的分析任务。请检查您的配置。")
        return

    # 3. 根据任务数量选择并执行相应的工作流
    num_tasks = len(analysis_tasks)
    if num_tasks < 2:
        print("❌ 错误：至少需要提供两个数据源才能进行分析。")
        return

    if num_tasks == 2:
        print(f"\n🚀 检测到 {num_tasks} 个数据源，已启动【双版本高精度比对分析】工作流...")
        execute_comparison_workflow(analysis_tasks, config)
    else:
        print(f"\n🚀 检测到 {num_tasks} 个数据源，已启动【多版本历史追溯分析】工作流...")
        execute_historical_workflow(analysis_tasks, config)

if __name__ == '__main__':
    main()