# -*- coding: utf-8 -*-

import pandas as pd
from typing import List

def generate_precise_diff_report(
    df_hist: pd.DataFrame,
    df_latest: pd.DataFrame,
    key_columns: List[str],
    hist_name: str = '历史版本',
    latest_name: str = '最新版本'
) -> str:
    """
    生成高精度的人类可读的数据差异日志，对比两个DataFrame。
    """
    hist = df_hist.copy()
    latest = df_latest.copy()
    value_cols = sorted([col for col in df_hist.columns if col not in key_columns])

    merged_df = pd.merge(
        hist, latest, on=key_columns, how='outer', suffixes=('_hist', '_latest'), indicator=True
    )

    log_entries = []

    # 处理删除的行
    deleted_rows = merged_df[merged_df['_merge'] == 'left_only']
    for _, row in deleted_rows.iterrows():
        key_str = ", ".join([f"{col}: '{row[col]}'" for col in key_columns])
        log_entries.append(f"【删除】源于 {hist_name} 的记录被删除。唯一键: [{key_str}]")

    # 处理新增的行
    added_rows = merged_df[merged_df['_merge'] == 'right_only']
    for _, row in added_rows.iterrows():
        key_str = ", ".join([f"{col}: '{row[col]}'" for col in key_columns])
        log_entries.append(f"【新增】在 {latest_name} 发现新记录。唯一键: [{key_str}]")

    # 处理修改的行
    both_df = merged_df[merged_df['_merge'] == 'both'].copy()
    modified_keys = set()
    for col in value_cols:
        col_hist, col_latest = f'{col}_hist', f'{col}_latest'

        # ======================================================================
        # --- 关键修复点 ---
        # 在比较前，将两列都显式转换为字符串类型，以避免因格式（如 '269' vs '269.0'）
        # 或潜在的混合类型（如 None vs ''）导致的不准确比较。
        # 这是使比较逻辑更健壮的核心改动。
        diff_mask = both_df[col_hist].astype(str) != both_df[col_latest].astype(str)
        # ======================================================================

        changed_df = both_df[diff_mask]

        for _, row in changed_df.iterrows():
            key_tuple = tuple(row[k] for k in key_columns)
            # 这里的判断是为了避免同一条记录的多个字段被修改时，在摘要中重复计数
            if key_tuple not in modified_keys:
                modified_keys.add(key_tuple)

            key_str = ", ".join([f"{k}: '{v}'" for k, v in zip(key_columns, key_tuple)])
            log_entries.append(
                f"【修改】唯一键: [{key_str}] | 列 '{col}': 值从 '{row[col_hist]}' 变为 '{row[col_latest]}'"
            )

    summary = f"对比摘要：【新增】{len(added_rows)}条，【删除】{len(deleted_rows)}条，【修改】{len(modified_keys)}条。"
    details = "\n".join(sorted(log_entries))

    return f"{summary}\n\n--- 详细变更记录 ---\n{details}" if details else summary