"""
地图投影和三沙市处理演示

本示例展示：
1. EPSG:2343 投影转换效果（避免地图变形）
2. 三沙市的智能过滤逻辑
"""

import os
import sys
import pandas as pd

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from chart import GridFigure  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402


def demo_projection():
    """演示投影转换效果"""
    print("=" * 60)
    print("演示：EPSG:2343 投影转换（避免地图变形）")
    print("=" * 60)

    # 创建省级数据
    provinces = [
        "北京",
        "上海",
        "广东",
        "浙江",
        "江苏",
        "山东",
        "河南",
        "四川",
        "湖北",
        "湖南",
        "河北",
        "福建",
    ]
    data = pd.DataFrame(
        {
            "省份": provinces,
            "GDP": [
                36000,
                43000,
                129000,
                77000,
                122000,
                87000,
                61000,
                56000,
                53000,
                48000,
                42000,
                51000,
            ],
        }
    )

    # 绘制全国省级地图
    f = plt.figure(FigureClass=GridFigure, width=12, height=10)
    f.plot(
        kind="map",
        data=data,
        level="province",
        scope="national",
        region_column="省份",
        value_column="GDP",
        cmap="YlOrRd",
        show_colorbar=True,
    )

    output_path = os.path.join(project_root, "example/plots/演示-投影转换.png")
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    print(f"✓ 已生成: {output_path}")
    print(f"  - 使用 EPSG:2343 投影")
    print(f"  - 地图纵横比正确，不会显得扁平")
    plt.close()


def demo_sansha_filter():
    """演示三沙市的智能过滤"""
    print("\n" + "=" * 60)
    print("演示：三沙市智能过滤逻辑")
    print("=" * 60)

    # 创建包含海南省城市的数据
    cities = ["海口", "三亚", "三沙", "儋州", "五指山", "文昌", "琼海", "万宁", "东方"]
    data = pd.DataFrame(
        {"城市": cities, "GDP": [1600, 705, 26, 400, 65, 260, 300, 220, 150]}
    )

    # 1. 全国地级市地图（自动排除三沙市）
    print("\n1. 全国地级市地图（自动排除三沙市）")
    f = plt.figure(FigureClass=GridFigure, width=12, height=10)
    f.plot(
        kind="map",
        data=data,
        level="prefecture",
        scope="national",
        region_column="城市",
        value_column="GDP",
        cmap="Blues",
    )

    output_path = os.path.join(project_root, "example/plots/演示-全国不含三沙.png")
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    print(f"   ✓ 已生成: {output_path}")
    print(f"   - 三沙市被自动排除，避免地图变形")
    plt.close()

    # 2. 海南省地级市地图（保留三沙市）
    print("\n2. 海南省地级市地图（保留三沙市）")
    f = plt.figure(FigureClass=GridFigure, width=10, height=10)
    f.plot(
        kind="map",
        data=data,
        level="prefecture",
        scope="provinces",
        regions=["海南"],
        region_column="城市",
        value_column="GDP",
        cmap="Greens",
    )

    output_path = os.path.join(project_root, "example/plots/演示-海南含三沙.png")
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    print(f"   ✓ 已生成: {output_path}")
    print(f"   - 展示海南省时，三沙市被保留")
    plt.close()

    # 3. 海南+广东地图（排除三沙市）
    print("\n3. 海南+广东地级市地图（排除三沙市）")
    # 添加广东城市数据
    guangdong_cities = ["广州", "深圳", "珠海", "佛山", "东莞"]
    combined_data = pd.concat(
        [
            data,
            pd.DataFrame(
                {"城市": guangdong_cities, "GDP": [28000, 32000, 3800, 12000, 10000]}
            ),
        ]
    )

    f = plt.figure(FigureClass=GridFigure, width=12, height=10)
    f.plot(
        kind="map",
        data=combined_data,
        level="prefecture",
        scope="provinces",
        regions=["海南", "广东"],
        region_column="城市",
        value_column="GDP",
        cmap="Purples",
    )

    output_path = os.path.join(project_root, "example/plots/演示-海南广东不含三沙.png")
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    print(f"   ✓ 已生成: {output_path}")
    print(f"   - 多省组合时，三沙市被排除（非单独展示海南省）")
    plt.close()


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("地图投影和三沙市处理演示")
    print("=" * 60)

    # 演示投影转换
    demo_projection()

    # 演示三沙市过滤
    demo_sansha_filter()

    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)
    print("\n关键改进：")
    print("1. ✓ 使用 EPSG:2343 投影，避免全国地图变形")
    print("2. ✓ 智能处理三沙市：")
    print("   - 全国地图：自动排除三沙市")
    print("   - 海南省单独展示：保留三沙市")
    print("   - 多省组合（非海南单独）：排除三沙市")
    print("\n生成的图表文件：")
    print("  - example/plots/演示-投影转换.png")
    print("  - example/plots/演示-全国不含三沙.png")
    print("  - example/plots/演示-海南含三沙.png")
    print("  - example/plots/演示-海南广东不含三沙.png")
    print()


if __name__ == "__main__":
    main()
