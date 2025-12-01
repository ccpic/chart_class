"""
地图标签格式化测试

测试标签的各种显示格式和样式
"""

import os
import sys
import pandas as pd

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from chart import GridFigure  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402


def test_label_with_region_name():
    """测试同时显示区域名称和数值"""
    print("=" * 60)
    print("测试：显示区域名称 + 数值标签")
    print("=" * 60)

    # 创建重点省份数据
    provinces = ["北京", "上海", "广东", "浙江", "江苏", "山东", "四川", "河南"]
    data = pd.DataFrame(
        {
            "省份": provinces,
            "GDP": [36000, 43000, 129000, 77000, 122000, 87000, 56000, 61000],
            "增长率": [6.3, 5.5, 4.8, 5.1, 5.4, 6.0, 8.0, 7.2],
        }
    )

    # 创建组合标签（区域名 + GDP）
    data["标签"] = (
        data["省份"] + "\n" + data["GDP"].apply(lambda x: f"{x/10000:.1f}万亿")
    )

    f = plt.figure(FigureClass=GridFigure, width=14, height=12)
    f.plot(
        kind="map",
        data=data,
        level="province",
        scope="national",
        region_column="省份",
        value_column="GDP",
        label_column="标签",
        cmap="YlOrRd",
    )

    output_path = os.path.join(project_root, "example/plots/测试-标签包含区域名.png")
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    print(f"✓ 已生成: {output_path}")
    print("  - 标签格式: 区域名 + GDP（万亿元）")
    plt.close()


def test_label_percentage():
    """测试显示百分比标签"""
    print("\n" + "=" * 60)
    print("测试：显示百分比标签")
    print("=" * 60)

    cities = ["昆明", "曲靖", "玉溪", "保山", "大理", "丽江", "楚雄", "红河"]
    gdp = [7000, 3000, 1500, 800, 1200, 500, 900, 1800]
    total_gdp = sum(gdp)

    data = pd.DataFrame(
        {"城市": cities, "GDP": gdp, "占比": [g / total_gdp * 100 for g in gdp]}
    )

    # 创建百分比标签
    data["标签"] = data["占比"].apply(lambda x: f"{x:.1f}%")

    f = plt.figure(FigureClass=GridFigure, width=12, height=12)
    f.plot(
        kind="map",
        data=data,
        level="prefecture",
        scope="provinces",
        regions=["云南"],
        region_column="城市",
        value_column="GDP",
        label_column="标签",
        cmap="Blues",
    )

    output_path = os.path.join(project_root, "example/plots/测试-标签显示百分比.png")
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    print(f"✓ 已生成: {output_path}")
    print("  - 标签格式: 百分比（占全省GDP比重）")
    plt.close()


def test_conditional_labels():
    """测试条件标签（仅显示重点区域）"""
    print("\n" + "=" * 60)
    print("测试：条件标签（仅标注GDP>500的城市）")
    print("=" * 60)

    cities = [
        "昆明",
        "曲靖",
        "玉溪",
        "保山",
        "昭通",
        "大理",
        "丽江",
        "普洱",
        "临沧",
        "楚雄",
        "红河",
        "文山",
    ]
    gdp = [7000, 3000, 1500, 800, 600, 1200, 500, 600, 400, 900, 1800, 750]

    data = pd.DataFrame({"城市": cities, "GDP": gdp})

    # 只为GDP>500的城市添加标签
    data["标签"] = data.apply(
        lambda row: f"{row['城市']}\n{row['GDP']}" if row["GDP"] > 500 else "", axis=1
    )

    f = plt.figure(FigureClass=GridFigure, width=12, height=12)
    f.plot(
        kind="map",
        data=data,
        level="prefecture",
        scope="provinces",
        regions=["云南"],
        region_column="城市",
        value_column="GDP",
        label_column="标签",
        cmap="Greens",
    )

    output_path = os.path.join(project_root, "example/plots/测试-条件标签.png")
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    print(f"✓ 已生成: {output_path}")
    print("  - 标签格式: 仅显示GDP>500的城市")
    plt.close()


def test_simple_number_labels():
    """测试简单数值标签"""
    print("\n" + "=" * 60)
    print("测试：简单数值标签（不带单位）")
    print("=" * 60)

    counties = ["五华区", "盘龙区", "官渡区", "西山区", "呈贡区", "晋宁区", "安宁市"]
    data = pd.DataFrame({"区县": counties, "人口": [80, 70, 95, 75, 45, 35, 40]})

    f = plt.figure(FigureClass=GridFigure, width=10, height=10)
    f.plot(
        kind="map",
        data=data,
        level="county",
        scope="cities",
        regions=["昆明"],
        region_column="区县",
        value_column="人口",
        label_column="人口",  # 直接使用数值列
        cmap="Oranges",
        dissolve_urban=True,
    )

    output_path = os.path.join(project_root, "example/plots/测试-简单数值标签.png")
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    print(f"✓ 已生成: {output_path}")
    print("  - 标签格式: 直接显示人口数值（万人）")
    plt.close()


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("地图标签格式化测试")
    print("=" * 60)

    # 测试各种标签格式
    test_label_with_region_name()
    test_label_percentage()
    test_conditional_labels()
    test_simple_number_labels()

    print("\n" + "=" * 60)
    print("所有格式化测试完成！")
    print("=" * 60)
    print("\n生成的测试文件：")
    print("  - example/plots/测试-标签包含区域名.png")
    print("  - example/plots/测试-标签显示百分比.png")
    print("  - example/plots/测试-条件标签.png")
    print("  - example/plots/测试-简单数值标签.png")
    print("\n标签功能总结：")
    print("  ✓ 支持自定义标签文本（通过创建标签列）")
    print("  ✓ 支持直接使用数值列作为标签")
    print("  ✓ 支持多行标签（使用\\n换行）")
    print("  ✓ 支持条件标签（空字符串不显示）")
    print("  ✓ 支持百分比、单位转换等格式化")
    print()


if __name__ == "__main__":
    main()
