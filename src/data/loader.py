# -*- coding: utf-8 -*-

import os
import pandas as pd
from typing import List, Dict, Optional

def read_and_validate_excel(
    file_path: str, key_columns: List[str], sheet_name: Optional[str] = None
) -> pd.DataFrame:
    """
    健壮地从Excel文件读取数据，并将所有列统一读取为字符串。

    Raises:
        FileNotFoundError: 如果文件路径不存在。
        ValueError: 如果缺少必要的关键列。
        Exception: 其他读取或验证错误。
    """
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件未找到 '{file_path}'。")

        df = pd.read_excel(file_path, sheet_name=sheet_name or 0, dtype=str)
        df.fillna('', inplace=True)

        required_cols = set(key_columns)
        missing_cols = required_cols - set(df.columns)

        if missing_cols:
            location_str = f"文件 '{os.path.basename(file_path)}'"
            if sheet_name:
                location_str += f" 的工作表 '{sheet_name}'"
            raise ValueError(f"{location_str} 中缺少必要的列: {', '.join(missing_cols)}")

        return df
    except Exception as e:
        raise Exception(f"读取或验证 '{file_path}' (工作表: {sheet_name or '默认'}) 时发生错误: {e}")

def apply_formatting_rules(df: pd.DataFrame, rules: Optional[Dict]) -> pd.DataFrame:
    """
    根据预定义规则对DataFrame的特定列应用格式化（如前置补零等）。
    """
    if not rules:
        return df

    df_formatted = df.copy()
    for col, rule in rules.items():
        if col in df_formatted.columns and pd.api.types.is_string_dtype(df_formatted[col]):
            if rule.get('type') == 'zfill':
                width = rule.get('width', 0)
                if width > 0:
                    df_formatted[col] = df_formatted[col].str.zfill(width)
    return df_formatted

def get_source_name(task: Dict) -> str:
    """根据分析任务字典生成一个人类可读的数据源名称。"""
    file_basename = os.path.basename(task['file'])
    sheet = task.get('sheet')
    return f"{file_basename} (Sheet: {sheet})" if sheet else file_basename