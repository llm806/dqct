# -*- coding: utf-8 -*-

import pandas as pd
from typing import List, Optional

def _are_series_equal(s1: pd.Series, s2: pd.Series) -> pd.Series:
    """
    智能比较两个Series，优先尝试数值比较，失败则回退到字符串比较。
    这是解决 '269' 和 '269.0' 被错误识别为差异的关键。
    """
    s1_numeric = pd.to_numeric(s1, errors='coerce')
    s2_numeric = pd.to_numeric(s2, errors='coerce')

    if s1_numeric.isnull().all() or s2_numeric.isnull().all():
        return s1.astype(str) == s2.astype(str)
    else:
        return s1_numeric == s2_numeric


def generate_precise_diff_report(
    df_hist: pd.DataFrame,
    df_latest: pd.DataFrame,
    key_columns: List[str],
    hist_name: str = '历史版本',
    latest_name: str = '最新版本',
    # --- 新增参数 ---
    # 允许调用者指定只检查哪些列。如果为None，则检查所有非关键列。
    columns_to_check: Optional[List[str]] = None
) -> str:
    """
    生成高精度的人类可读的数据差异日志，对比两个DataFrame。
    """
    hist = df_hist.copy()
    latest = df_latest.copy()

    # --- 逻辑修改 ---
    # 如果未指定检查列，则默认检查所有非关键列
    if columns_to_check is None:
        value_cols = sorted([col for col in df_hist.columns if col not in key_columns])
    else:
        value_cols = columns_to_check

    merged_df = pd.merge(
        hist, latest, on=key_columns, how='outer', suffixes=('_hist', '_latest'), indicator=True
    )

    log_entries = []

    deleted_rows = merged_df[merged_df['_merge'] == 'left_only']
    for _, row in deleted_rows.iterrows():
        key_str = ", ".join([f"{col}: '{row[col]}'" for col in key_columns])
        log_entries.append(f"【删除】源于 {hist_name} 的记录被删除。唯一键: [{key_str}]")

    added_rows = merged_df[merged_df['_merge'] == 'right_only']
    for _, row in added_rows.iterrows():
        key_str = ", ".join([f"{col}: '{row[col]}'" for col in key_columns])
        log_entries.append(f"【新增】在 {latest_name} 发现新记录。唯一键: [{key_str}]")

    both_df = merged_df[merged_df['_merge'] == 'both'].copy()
    modified_keys = set()

    # 现在的 value_cols 可能是所有非关键列，也可能是指定的列
    for col in value_cols:
        col_hist, col_latest = f'{col}_hist', f'{col}_latest'

        are_equal = _are_series_equal(both_df[col_hist], both_df[col_latest])
        diff_mask = ~are_equal

        changed_df = both_df[diff_mask]

        for _, row in changed_df.iterrows():
            key_tuple = tuple(row[k] for k in key_columns)
            modified_keys.add(key_tuple)

            key_str = ", ".join([f"{k}: '{v}'" for k, v in zip(key_columns, key_tuple)])
            log_entries.append(
                f"【修改】唯一键: [{key_str}] | 列 '{col}': 值从 '{row[col_hist]}' 变为 '{row[col_latest]}'"
            )

    summary = f"对比摘要：【新增】{len(added_rows)}条，【删除】{len(deleted_rows)}条，【修改】{len(modified_keys)}条。"
    details = "\n".join(sorted(log_entries))

    return f"  {summary}\n\n--- 详细变更记录 ---\n{details}" if details else summary