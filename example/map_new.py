"""
中国地图热力图示例

演示地图范围和数据粒度的灵活组合：
1. 全国省级热力图 - 全国范围 + 省级数据
2. 全国地级市热力图 - 全国范围 + 地级市数据
3. 多省地级市热力图 - 指定省份范围 + 地级市数据
4. 多市区县热力图 - 指定地级市范围 + 区县数据
"""

import os
import sys
import pandas as pd
import numpy as np

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from chart import GridFigure  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402


def create_province_data():
    """创建省级测试数据（混合使用简称和全称）"""
    provinces = [
        "北京",  # 简称，会自动转换为"北京市"
        "天津市",  # 全称
        "河北",  # 简称
        "山西省",  # 全称
        "内蒙古",  # 简称
        "辽宁省",
        "吉林",  # 简称
        "黑龙江省",
        "上海",  # 简称
        "江苏省",
        "浙江",  # 简称
        "安徽省",
        "福建",  # 简称
        "江西省",
        "山东",  # 简称
        "河南省",
        "湖北",  # 简称
        "湖南省",
        "广东",  # 简称
        "广西",  # 简称
        "海南省",
        "重庆",  # 简称
        "四川省",
        "贵州",  # 简称
        "云南省",
        "西藏",  # 简称
        "陕西省",
        "甘肃",  # 简称
        "青海省",
        "宁夏",  # 简称
        "新疆",  # 简称
    ]

    # 模拟 GDP 数据（单位：亿元）
    np.random.seed(42)
    gdp = np.random.randint(5000, 100000, len(provinces))

    df = pd.DataFrame(
        {
            "GDP": gdp,
            "人口": np.random.randint(1000, 10000, len(provinces)),
        },
        index=provinces,
    )

    return df


def test_national_province_map():
    """测试1: 全国省级热力图"""
    print("=" * 50)
    print("测试 1: 全国省级热力图")
    print("=" * 50)

    df = create_province_data()
    print("\n省级数据样例：")
    print(df.head())

    f = plt.figure(
        FigureClass=GridFigure,
        width=15,
        height=10,
        fontsize=12,
        style={"title": "全国各省GDP分布（自动排除三沙市）"},
    )

    f.plot(
        kind="map",
        data=df,
        value_column="GDP",
        level="province",
        scope="national",
        cmap="YlOrRd",
        ax_index=0,
    )

    plots_dir = os.path.join(os.path.dirname(__file__), "plots")
    if not os.path.exists(plots_dir):
        os.makedirs(plots_dir)
    savepath = f.save(os.path.join(plots_dir, "地图-全国省级.png"))
    print(f"\n全国省级地图已保存: {savepath}")


def test_national_prefecture_map():
    """测试2: 全国地级市热力图"""
    print("\n" + "=" * 50)
    print("测试 2: 全国地级市热力图")
    print("=" * 50)

    # 创建全国地级市数据（这里用部分城市演示）
    cities = [
        "北京",
        "上海",
        "广州",
        "深圳",
        "杭州",
        "成都",
        "武汉",
        "西安",
        "南京",
        "天津",
        "苏州",
        "重庆",
        "郑州",
        "长沙",
        "东莞",
        "沈阳",
        "青岛",
        "合肥",
        "佛山",
        "昆明",
        "福州",
        "济南",
        "厦门",
        "哈尔滨",
        "石家庄",
        "南昌",
        "宁波",
        "无锡",
        "太原",
        "长春",
        "南宁",
        "贵阳",
    ]

    np.random.seed(42)
    df_cities = pd.DataFrame(
        {"销售额": np.random.randint(1000, 10000, len(cities))}, index=cities
    )

    print("\n地级市数据样例：")
    print(df_cities.head(10))

    f = plt.figure(
        FigureClass=GridFigure,
        width=16,
        height=12,
        fontsize=10,
        style={"title": "全国主要城市销售额分布（自动排除三沙市）"},
    )

    f.plot(
        kind="map",
        data=df_cities,
        value_column="销售额",
        level="prefecture",
        scope="national",
        cmap="Blues",
        ax_index=0,
    )

    plots_dir = os.path.join(os.path.dirname(__file__), "plots")
    if not os.path.exists(plots_dir):
        os.makedirs(plots_dir)
    savepath = f.save(os.path.join(plots_dir, "地图-全国地级市.png"))
    print(f"\n全国地级市地图已保存: {savepath}")


def test_multi_province_prefecture_map():
    """测试3: 多省地级市热力图"""
    print("\n" + "=" * 50)
    print("测试 3: 多省地级市热力图（云南+四川+贵州）")
    print("=" * 50)

    # 创建三省地级市数据
    cities_multi = [
        # 云南
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
        # 四川
        "成都",
        "绵阳",
        "德阳",
        "南充",
        "宜宾",
        "自贡",
        "乐山",
        "泸州",
        "达州",
        "内江",
        "遂宁",
        "攀枝花",
        "眉山",
        "广安",
        "资阳",
        "凉山",
        # 贵州
        "贵阳",
        "遵义",
        "六盘水",
        "安顺",
        "毕节",
        "铜仁",
        "黔东南",
        "黔南",
        "黔西南",
    ]

    np.random.seed(123)
    df_multi = pd.DataFrame(
        {"人口": np.random.randint(100, 1000, len(cities_multi))}, index=cities_multi
    )

    print("\n多省地级市数据样例：")
    print(df_multi.head(10))

    f = plt.figure(
        FigureClass=GridFigure,
        width=14,
        height=12,
        fontsize=11,
        style={"title": "云贵川三省地级市人口分布"},
    )

    f.plot(
        kind="map",
        data=df_multi,
        value_column="人口",
        level="prefecture",
        scope="provinces",
        regions=["云南", "四川", "贵州"],  # 支持简称
        cmap="Greens",
        ax_index=0,
    )

    plots_dir = os.path.join(os.path.dirname(__file__), "plots")
    if not os.path.exists(plots_dir):
        os.makedirs(plots_dir)
    savepath = f.save(os.path.join(plots_dir, "地图-多省地级市.png"))
    print(f"\n多省地级市地图已保存: {savepath}")


def test_multi_city_county_map():
    """测试4: 多市区县热力图"""
    print("\n" + "=" * 50)
    print("测试 4: 多市区县热力图（昆明+大理）")
    print("=" * 50)

    # 昆明市的区县
    counties_kunming = [
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

    # 大理州的区县
    counties_dali = [
        "大理市",
        "漾濞彝族自治县",
        "祥云县",
        "宾川县",
        "弥渡县",
        "南涧彝族自治县",
        "巍山彝族回族自治县",
        "永平县",
        "云龙县",
        "洱源县",
        "剑川县",
        "鹤庆县",
    ]

    all_counties = counties_kunming + counties_dali
    np.random.seed(456)
    df_counties = pd.DataFrame(
        {"GDP": np.random.randint(50, 500, len(all_counties))}, index=all_counties
    )

    print("\n多市区县数据样例：")
    print(df_counties.head(10))

    f = plt.figure(
        FigureClass=GridFigure,
        width=14,
        height=10,
        fontsize=10,
        style={"title": "昆明市+大理州区县GDP分布"},
    )

    f.plot(
        kind="map",
        data=df_counties,
        value_column="GDP",
        level="county",
        scope="cities",
        regions=["昆明", "大理"],  # 支持简称
        cmap="Oranges",
        dissolve_urban=True,
        ax_index=0,
    )

    plots_dir = os.path.join(os.path.dirname(__file__), "plots")
    if not os.path.exists(plots_dir):
        os.makedirs(plots_dir)
    savepath = f.save(os.path.join(plots_dir, "地图-多市区县.png"))
    print(f"\n多市区县地图已保存: {savepath}")


def test_all():
    """运行所有测试"""
    print("\n开始测试中国地图热力图模块（新版 API）...\n")

    try:
        # 测试1: 全国省级热力图
        test_national_province_map()

        # 测试2: 全国地级市热力图
        test_national_prefecture_map()

        # 测试3: 多省地级市热力图
        test_multi_province_prefecture_map()

        # 测试4: 多市区县热力图
        test_multi_city_county_map()

        print("\n" + "=" * 50)
        print("所有测试完成！")
        print("=" * 50)
        print("\n生成的图表文件：")
        print("  - example/plots/地图-全国省级.png")
        print("  - example/plots/地图-全国地级市.png")
        print("  - example/plots/地图-多省地级市.png")
        print("  - example/plots/地图-多市区县.png")

    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_all()
