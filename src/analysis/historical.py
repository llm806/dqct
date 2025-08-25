# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from typing import List, Dict, Optional

def _calculate_anomaly_score(row: pd.Series) -> float:
    """计算单行记录的异常得分，用于筛选最值得关注的变更。"""
    WEIGHT_MOD_COUNT = 0.6
    WEIGHT_MAX_PCT_CHANGE = 0.4

    mod_count_score = row['修改次数']
    pct_changes = [abs(c) for c in row['历史变化率列表(%)'] if np.isfinite(c)]
    max_pct_change_score = max(pct_changes) if pct_changes else 0.0

    score = (WEIGHT_MOD_COUNT * mod_count_score) + (WEIGHT_MAX_PCT_CHANGE * (max_pct_change_score / 100.0))
    return score

def generate_historical_trace_table(
    all_dfs: List[pd.DataFrame],
    key_columns: List[str],
    value_column: str,
    top_n: Optional[int]
) -> pd.DataFrame:
    """
    根据多个版本的DataFrame生成历史轨迹表，并根据“异常得分”筛选出Top-N条记录。
    """
    if not all_dfs:
        return pd.DataFrame()

    for i, df in enumerate(all_dfs):
        df[value_column] = pd.to_numeric(df[value_column], errors='coerce')
        df['_version_index'] = i

    combined_df = pd.concat(all_dfs, ignore_index=True)
    combined_df.sort_values(by=key_columns + ['_version_index'], inplace=True)

    print("  - 正在聚合所有版本数据...")
    aggregated = combined_df.groupby(key_columns).agg(
        历史值列表=(value_column, list),
        **{col: (col, 'last') for col in combined_df.columns if col not in key_columns + [value_column, '_version_index']}
    ).reset_index()

    aggregated = aggregated[aggregated['历史值列表'].apply(lambda x: len(set(x)) > 1)].copy()
    if aggregated.empty:
        return pd.DataFrame()

    def get_diff_list(h):
        return [h[i] - h[i - 1] for i in range(1, len(h))]

    def get_pct_change_list(h):
        return [np.inf if h[i-1] == 0 else ((h[i] - h[i-1]) / h[i-1]) * 100 for i in range(1, len(h))]

    aggregated['历史差值列表'] = aggregated['历史值列表'].apply(get_diff_list)
    aggregated['历史变化率列表(%)'] = aggregated['历史值列表'].apply(get_pct_change_list)
    aggregated['最新值'] = aggregated['历史值列表'].apply(lambda x: x[-1] if x else None)
    aggregated['修改次数'] = aggregated['历史值列表'].apply(lambda x: len(set(x)) - 1)

    print("  - 正在计算每条记录的异常得分...")
    aggregated['异常得分'] = aggregated.apply(_calculate_anomaly_score, axis=1)
    aggregated.sort_values(by=['异常得分', '修改次数'], ascending=[False, False], inplace=True)

    print(f"  - 成功生成轨迹表，共发现 {len(aggregated)} 条有变化的记录。")
    if top_n and top_n > 0:
        print(f"  - 根据配置，筛选出异常得分最高的 Top {top_n} 条记录进行分析。")
        return aggregated.head(top_n)

    return aggregated

def create_historical_trace_markdown(df: pd.DataFrame, key_columns: List[str]) -> str:
    """根据历史追溯DataFrame创建Markdown表格。"""
    if df.empty:
        return "在所有数据版本中，未发现任何记录的核心数值发生过变化。"

    display_columns = key_columns + ['历史值列表', '最新值', '历史差值列表', '历史变化率列表(%)', '修改次数', '异常得分']
    headers = key_columns + ['历史值演变轨迹', '最新值', '历史差值列表', '历史变化率列表(%)', '总修改次数', '异常得分']
    df_display = df[display_columns].copy()

    header_line = "| " + " | ".join(headers) + " |"
    separator_line = "| " + " | ".join(['---'] * len(headers)) + " |"
    markdown_lines = [header_line, separator_line]

    for _, row in df_display.iterrows():
        row_values = []
        for col_name in display_columns:
            value = row[col_name]
            if col_name in key_columns or col_name == '修改次数':
                formatted_value = str(value)
            elif col_name == '历史值列表':
                formatted_value = " -> ".join([f"{v:.2f}" for v in value])
            elif col_name == '最新值':
                formatted_value = f"{value:.2f}"
            elif col_name == '历史差值列表':
                formatted_value = " -> ".join([f"{v:+.2f}" for v in value]) or "无变化"
            elif col_name == '历史变化率列表(%)':
                formatted_value = " -> ".join([f"∞" if np.isinf(v) else f"{v:+.2f}%" for v in value]) or "无变化"
            elif col_name == '异常得分':
                formatted_value = f"{value:.2f}"
            else:
                formatted_value = str(value)
            row_values.append(formatted_value)
        markdown_lines.append("| " + " | ".join(row_values) + " |")

    return "\n".join(markdown_lines)