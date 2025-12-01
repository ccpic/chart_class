"""
地图标签增强功能测试

测试 label_format 占位符和 label_fontsize 自定义字体大小功能
"""

import os
import sys
import pandas as pd

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from chart import GridFigure  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402


def test_label_format_index_value():
    """测试 {index} 和 {value} 占位符"""
    print("=" * 60)
    print("测试 1: 使用 {index} 和 {value} 占位符")
    print("=" * 60)

    provinces = ["北京", "上海", "广东", "浙江", "江苏", "山东", "四川", "河南"]
    data = pd.DataFrame(
        {
            "省份": provinces,
            "GDP": [36000, 43000, 129000, 77000, 122000, 87000, 56000, 61000],
        }
    )

    # 使用占位符格式化标签
    f = plt.figure(FigureClass=GridFigure, width=14, height=12)
    f.plot(
        kind="map",
        data=data,
        level="province",
        scope="national",
        region_column="省份",
        value_column="GDP",
        label_column="GDP",
        label_format="{index}\n{value}亿",  # 显示"省份名\nGDP值亿"
        cmap="YlOrRd",
    )

    output_path = os.path.join(
        project_root, "example/plots/测试-占位符index和value.png"
    )
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    print(f"✓ 已生成: {output_path}")
    print(f"  - 标签格式: {{index}}\\n{{value}}亿")
    plt.close()


def test_label_format_value_only():
    """测试仅使用 {value} 占位符"""
    print("\n" + "=" * 60)
    print("测试 2: 仅使用 {value} 占位符添加单位")
    print("=" * 60)

    cities = ["昆明", "曲靖", "玉溪", "保山", "大理", "丽江", "楚雄", "红河"]
    data = pd.DataFrame(
        {"城市": cities, "人口": [850, 600, 240, 260, 350, 130, 270, 470]}
    )

    f = plt.figure(FigureClass=GridFigure, width=12, height=12)
    f.plot(
        kind="map",
        data=data,
        level="prefecture",
        scope="provinces",
        regions=["云南"],
        region_column="城市",
        value_column="人口",
        label_column="人口",
        label_format="{value}万人",  # 显示"XXX万人"
        cmap="Blues",
    )

    output_path = os.path.join(
        project_root, "example/plots/测试-占位符value添加单位.png"
    )
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    print(f"✓ 已生成: {output_path}")
    print(f"  - 标签格式: {{value}}万人")
    plt.close()


def test_custom_fontsize():
    """测试自定义字体大小"""
    print("\n" + "=" * 60)
    print("测试 3: 自定义标签字体大小")
    print("=" * 60)

    provinces = ["北京", "上海", "广东", "浙江", "江苏", "山东"]
    data = pd.DataFrame(
        {"省份": provinces, "GDP": [36000, 43000, 129000, 77000, 122000, 87000]}
    )

    # 使用较大的字体
    f = plt.figure(FigureClass=GridFigure, width=14, height=12)
    f.plot(
        kind="map",
        data=data,
        level="province",
        scope="national",
        region_column="省份",
        value_column="GDP",
        label_column="GDP",
        label_format="{index}",  # 只显示省份名
        label_fontsize=16,  # 自定义字体大小为16
        cmap="Greens",
    )

    output_path = os.path.join(project_root, "example/plots/测试-自定义字体大小16.png")
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    print(f"✓ 已生成: {output_path}")
    print(f"  - 标签格式: {{index}}")
    print(f"  - 字体大小: 16 (自定义)")
    plt.close()


def test_small_fontsize():
    """测试小字体标签"""
    print("\n" + "=" * 60)
    print("测试 4: 小字体标签（适合密集区域）")
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
        "西双版纳",
        "德宏",
        "怒江",
        "迪庆",
    ]
    data = pd.DataFrame(
        {
            "城市": cities,
            "GDP": [
                7000,
                3000,
                1500,
                800,
                600,
                1200,
                500,
                600,
                400,
                900,
                1800,
                750,
                600,
                350,
                120,
                80,
            ],
        }
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
        label_column="GDP",
        label_format="{index}\n{value}",
        label_fontsize=6,  # 小字体适合密集区域
        cmap="RdPu",
    )

    output_path = os.path.join(project_root, "example/plots/测试-小字体密集标签.png")
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    print(f"✓ 已生成: {output_path}")
    print(f"  - 标签格式: {{index}}\\n{{value}}")
    print(f"  - 字体大小: 6 (小字体)")
    plt.close()


def test_complex_format():
    """测试复杂格式化"""
    print("\n" + "=" * 60)
    print("测试 5: 复杂标签格式化")
    print("=" * 60)

    counties = ["五华区", "盘龙区", "官渡区", "西山区", "呈贡区", "晋宁区", "安宁市"]
    data = pd.DataFrame(
        {
            "区县": counties,
            "人口": [80, 70, 95, 75, 45, 35, 40],
            "增长": [2.3, 1.8, 3.5, 2.1, 5.6, 4.2, 3.8],
        }
    )

    # 创建复杂的格式化标签（需要先在数据中准备）
    data["增长率"] = data["增长"].apply(lambda x: f"{x}%")

    f = plt.figure(FigureClass=GridFigure, width=10, height=10)
    f.plot(
        kind="map",
        data=data,
        level="county",
        scope="cities",
        regions=["昆明"],
        region_column="区县",
        value_column="人口",
        label_column="增长率",
        label_format="{index}\n增长{value}",  # 显示"区县名\n增长X.X%"
        label_fontsize=8,
        cmap="Oranges",
        dissolve_urban=True,
    )

    output_path = os.path.join(project_root, "example/plots/测试-复杂格式化标签.png")
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    print(f"✓ 已生成: {output_path}")
    print(f"  - 标签格式: {{index}}\\n增长{{value}}")
    print(f"  - 字体大小: 8")
    plt.close()


def test_comparison():
    """测试对比：默认 vs 自定义"""
    print("\n" + "=" * 60)
    print("测试 6: 对比默认标签和自定义标签")
    print("=" * 60)

    provinces = ["云南", "四川", "贵州", "重庆"]
    data = pd.DataFrame({"省份": provinces, "GDP": [27000, 56000, 19000, 27000]})

    # 6a. 默认标签（不使用占位符）
    print("  6a. 生成默认标签样式...")
    f = plt.figure(FigureClass=GridFigure, width=12, height=10)
    f.plot(
        kind="map",
        data=data,
        level="province",
        scope="provinces",
        regions=["云南", "四川", "贵州", "重庆"],
        region_column="省份",
        value_column="GDP",
        label_column="GDP",  # 直接显示数值
        cmap="YlGnBu",
    )

    output_path = os.path.join(project_root, "example/plots/对比-默认标签.png")
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    print(f"     ✓ 已生成: {output_path}")
    plt.close()

    # 6b. 自定义标签（使用占位符和自定义字体）
    print("  6b. 生成自定义标签样式...")
    f = plt.figure(FigureClass=GridFigure, width=12, height=10)
    f.plot(
        kind="map",
        data=data,
        level="province",
        scope="provinces",
        regions=["云南", "四川", "贵州", "重庆"],
        region_column="省份",
        value_column="GDP",
        label_column="GDP",
        label_format="{index}\nGDP: {value}亿",  # 自定义格式
        label_fontsize=12,  # 自定义字体大小
        cmap="YlGnBu",
    )

    output_path = os.path.join(project_root, "example/plots/对比-自定义标签.png")
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    print(f"     ✓ 已生成: {output_path}")
    print(f"     - 标签格式: {{index}}\\nGDP: {{value}}亿")
    print(f"     - 字体大小: 12")
    plt.close()


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("地图标签增强功能测试")
    print("=" * 60)
    print("\n新功能说明：")
    print("  1. label_format 参数：支持占位符格式化")
    print("     - {index}: 区域名称（省份/城市/区县）")
    print("     - {value}: label_column 列的值")
    print("  2. label_fontsize 参数：自定义标签字体大小")
    print("     - 不指定时根据层级自动调整")
    print("     - 可手动设置任意大小")
    print()

    # 运行所有测试
    test_label_format_index_value()
    test_label_format_value_only()
    test_custom_fontsize()
    test_small_fontsize()
    test_complex_format()
    test_comparison()

    print("\n" + "=" * 60)
    print("所有测试完成！")
    print("=" * 60)
    print("\n生成的测试文件：")
    print("  - example/plots/测试-占位符index和value.png")
    print("  - example/plots/测试-占位符value添加单位.png")
    print("  - example/plots/测试-自定义字体大小16.png")
    print("  - example/plots/测试-小字体密集标签.png")
    print("  - example/plots/测试-复杂格式化标签.png")
    print("  - example/plots/对比-默认标签.png")
    print("  - example/plots/对比-自定义标签.png")
    print("\n功能总结：")
    print("  ✓ 支持 {index} 占位符显示区域名称")
    print("  ✓ 支持 {value} 占位符显示数据值")
    print("  ✓ 支持自由组合占位符和文本")
    print("  ✓ 支持自定义字体大小 label_fontsize")
    print("  ✓ 支持多行标签（使用\\n）")
    print("  ✓ 向后兼容：不使用新参数时保持原有行为")
    print()


if __name__ == "__main__":
    main()
