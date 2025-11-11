"""
颜色去重脚本
- 分析 COLOR_DICT 中的重复项
- 生成去重后的定义（保留第一个）
- 导出为 Python 和 JSON 格式
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from chart.color.color import COLOR_DICT
from collections import OrderedDict
import json


def analyze_and_deduplicate():
    """分析并去重颜色定义"""

    # 使用 OrderedDict 保留第一次出现的定义
    deduped = OrderedDict()
    duplicates = []

    for name, color in COLOR_DICT.items():
        if name in deduped:
            duplicates.append(
                {"name": name, "first_color": deduped[name], "duplicate_color": color}
            )
        else:
            deduped[name] = color

    stats = {
        "original_count": len(COLOR_DICT),
        "deduped_count": len(deduped),
        "duplicate_count": len(duplicates),
        "duplicates": duplicates,
    }

    return dict(deduped), stats


def generate_python_file(deduped_dict, output_path):
    """生成 Python 文件"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write('"""去重后的颜色字典（自动生成）"""\n\n')
        f.write("COLOR_DICT_DEDUPED = {\n")

        for name, color in deduped_dict.items():
            # 转义引号
            safe_name = name.replace('"', '\\"')
            f.write(f'    "{safe_name}": "{color}",\n')

        f.write("}\n")


def export_to_json(deduped_dict, output_path):
    """导出为 JSON"""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(deduped_dict, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    print("🔍 分析颜色重复项...")
    deduped, stats = analyze_and_deduplicate()

    print(f"\n📊 统计结果:")
    print(f"  原始条目: {stats['original_count']}")
    print(f"  去重后: {stats['deduped_count']}")
    print(f"  重复项: {stats['duplicate_count']}")

    if stats["duplicates"]:
        print(f"\n⚠️  发现 {len(stats['duplicates'])} 个重复定义:")
        for dup in stats["duplicates"][:10]:  # 只显示前10个
            print(
                f"  - '{dup['name']}': {dup['first_color']} -> {dup['duplicate_color']} (已忽略)"
            )
        if len(stats["duplicates"]) > 10:
            print(f"  ... 还有 {len(stats['duplicates']) - 10} 个")

    # 导出文件
    script_dir = os.path.dirname(__file__)

    # Python 文件
    py_output = os.path.join(
        script_dir, "..", "chart", "color", "color_dict_deduped.py"
    )
    generate_python_file(deduped, py_output)
    print(f"\n✅ 已生成 Python 文件: {py_output}")

    # JSON 文件
    json_output = os.path.join(script_dir, "..", "data", "color_dict.json")
    export_to_json(deduped, json_output)
    print(f"✅ 已生成 JSON 文件: {json_output}")

    # 完整重复报告
    report_output = os.path.join(
        script_dir, "..", "data", "color_duplicates_report.json"
    )
    with open(report_output, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print(f"✅ 已生成重复报告: {report_output}")
