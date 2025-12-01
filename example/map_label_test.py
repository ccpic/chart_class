"""
地图标签功能测试

测试各个层级地图的标签显示功能
"""

import os
import sys
import pandas as pd

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from chart import GridFigure  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402


def test_province_labels():
    """测试省级地图标签"""
    print("=" * 60)
    print("测试 1: 省级地图标签")
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
        "云南",
        "贵州",
        "陕西",
        "重庆",
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
                27000,
                19000,
                30000,
                27000,
            ],
        }
    )

    # 绘制带标签的省级地图
    f = plt.figure(FigureClass=GridFigure, width=14, height=12)
    f.plot(
        kind="map",
        data=data,
        level="province",
        scope="national",
        region_column="省份",
        value_column="GDP",
        label_column="GDP",  # 添加标签
        cmap="YlOrRd",
        show_colorbar=True,
    )

    output_path = os.path.join(project_root, "example/plots/测试-省级地图带标签.png")
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    print(f"✓ 已生成: {output_path}")
    plt.close()


def test_prefecture_labels():
    """测试地级市地图标签"""
    print("\n" + "=" * 60)
    print("测试 2: 地级市地图标签（云南省）")
    print("=" * 60)

    # 创建云南省地级市数据
    cities = [
        "昆明",
        "曲靖",
        "玉溪",
        "保山",
        "昭通",
        "丽江",
        "普洱",
        "临沧",
        "楚雄",
        "红河",
        "文山",
        "西双版纳",
        "大理",
        "德宏",
        "怒江",
        "迪庆",
    ]
    data = pd.DataFrame(
        {
            "城市": cities,
            "人口": [
                850,
                600,
                240,
                260,
                540,
                130,
                260,
                250,
                270,
                470,
                360,
                120,
                350,
                130,
                54,
                40,
            ],
        }
    )

    # 绘制云南省地级市地图，带标签
    f = plt.figure(FigureClass=GridFigure, width=12, height=12)
    f.plot(
        kind="map",
        data=data,
        level="prefecture",
        scope="provinces",
        regions=["云南"],
        region_column="城市",
        value_column="人口",
        label_column="人口",  # 添加标签
        cmap="Blues",
        show_colorbar=True,
    )

    output_path = os.path.join(project_root, "example/plots/测试-云南地级市带标签.png")
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    print(f"✓ 已生成: {output_path}")
    plt.close()


def test_county_labels():
    """测试区县地图标签"""
    print("\n" + "=" * 60)
    print("测试 3: 区县地图标签（昆明市）")
    print("=" * 60)

    # 创建昆明市区县数据
    counties = [
        "五华区",
        "盘龙区",
        "官渡区",
        "西山区",
        "东川区",
        "呈贡区",
        "晋宁区",
        "富民县",
        "宜良县",
        "石林彝族自治县",
        "嵩明县",
        "禄劝彝族苗族自治县",
        "寻甸回族彝族自治县",
        "安宁市",
    ]
    data = pd.DataFrame(
        {
            "区县": counties,
            "GDP": [
                800,
                650,
                920,
                680,
                120,
                720,
                350,
                180,
                260,
                240,
                200,
                150,
                170,
                550,
            ],
        }
    )

    # 绘制昆明市区县地图，带标签
    f = plt.figure(FigureClass=GridFigure, width=12, height=12)
    f.plot(
        kind="map",
        data=data,
        level="county",
        scope="cities",
        regions=["昆明"],
        region_column="区县",
        value_column="GDP",
        label_column="GDP",  # 添加标签
        cmap="Greens",
        show_colorbar=True,
        dissolve_urban=True,  # 高亮市区
    )

    output_path = os.path.join(project_root, "example/plots/测试-昆明区县带标签.png")
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    print(f"✓ 已生成: {output_path}")
    plt.close()


def test_multi_province_labels():
    """测试多省地级市地图标签"""
    print("\n" + "=" * 60)
    print("测试 4: 多省地级市地图标签（云贵川）")
    print("=" * 60)

    # 创建云贵川部分地级市数据
    cities = [
        # 云南
        "昆明",
        "曲靖",
        "大理",
        "丽江",
        # 四川
        "成都",
        "绵阳",
        "德阳",
        "南充",
        # 贵州
        "贵阳",
        "遵义",
        "六盘水",
        "安顺",
    ]
    data = pd.DataFrame(
        {
            "城市": cities,
            "GDP": [
                7000,
                3000,
                1500,
                500,
                19000,
                3000,
                2500,
                2300,
                4000,
                3500,
                1500,
                1000,
            ],
        }
    )

    # 绘制多省地级市地图，带标签
    f = plt.figure(FigureClass=GridFigure, width=14, height=12)
    f.plot(
        kind="map",
        data=data,
        level="prefecture",
        scope="provinces",
        regions=["云南", "四川", "贵州"],
        region_column="城市",
        value_column="GDP",
        label_column="GDP",  # 添加标签
        cmap="RdPu",
        show_colorbar=True,
    )

    output_path = os.path.join(
        project_root, "example/plots/测试-云贵川地级市带标签.png"
    )
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    print(f"✓ 已生成: {output_path}")
    plt.close()


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("地图标签功能测试")
    print("=" * 60)

    # 测试省级地图标签
    test_province_labels()

    # 测试地级市地图标签
    test_prefecture_labels()

    # 测试区县地图标签
    test_county_labels()

    # 测试多省地级市地图标签
    test_multi_province_labels()

    print("\n" + "=" * 60)
    print("所有测试完成！")
    print("=" * 60)
    print("\n生成的测试文件：")
    print("  - example/plots/测试-省级地图带标签.png")
    print("  - example/plots/测试-云南地级市带标签.png")
    print("  - example/plots/测试-昆明区县带标签.png")
    print("  - example/plots/测试-云贵川地级市带标签.png")
    print()


if __name__ == "__main__":
    main()
