"""测试地图标签简称功能"""

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from chart import GridFigure


def test_county_abbr():
    """测试区县层级简称功能"""
    # 创建测试数据 - 云南省普洱市区县数据
    data = {
        "区县": [
            "思茅区",
            "宁洱哈尼族彝族自治县",
            "墨江哈尼族自治县",
            "景东彝族自治县",
            "景谷傣族彝族自治县",
            "镇沅彝族哈尼族拉祜族自治县",
            "江城哈尼族彝族自治县",
            "孟连傣族拉祜族佤族自治县",
            "澜沧拉祜族自治县",
            "西盟佤族自治县",
        ],
        "人口": [25.6, 19.3, 36.5, 35.8, 29.7, 21.2, 11.8, 13.2, 48.7, 9.4],
    }
    df = pd.DataFrame(data)
    df.set_index("区县", inplace=True)

    # 创建 2x2 网格图
    f = plt.figure(
        FigureClass=GridFigure,
        nrows=2,
        ncols=2,
        width=16,
        height=12,
    )

    # 测试1：全国区县地图 - 不使用简称
    f.plot(
        kind="map",
        data=df,
        level="county",
        scope="national",
        ax_index=0,
        value_column="人口",
        label_column="人口",
        label_format="{index}",
        label_fontsize=6,
        use_abbr=False,
        title="全国区县地图 - 全称",
    )

    # 测试2：全国区县地图 - 使用简称
    f.plot(
        kind="map",
        data=df,
        level="county",
        scope="national",
        ax_index=1,
        value_column="人口",
        label_column="人口",
        label_format="{index}",
        label_fontsize=6,
        use_abbr=True,
        title="全国区县地图 - 简称",
    )

    # 测试3：指定城市集合 - 不使用简称
    f.plot(
        kind="map",
        data=df,
        level="county",
        scope="cities",
        regions=["普洱市"],
        ax_index=2,
        value_column="人口",
        label_column="人口",
        label_format="{index}\n{value}万",
        label_fontsize=8,
        use_abbr=False,
        title="普洱市区县地图 - 全称",
    )

    # 测试4：指定城市集合 - 使用简称
    f.plot(
        kind="map",
        data=df,
        level="county",
        scope="cities",
        regions=["普洱市"],
        ax_index=3,
        value_column="人口",
        label_column="人口",
        label_format="{index}\n{value}万",
        label_fontsize=8,
        use_abbr=True,
        title="普洱市区县地图 - 简称",
    )

    # 保存图片
    output_dir = os.path.join(project_root, "example", "plots")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "地图_简称测试.png")
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"图片已保存至: {output_path}")
    plt.show()


def test_province_city_abbr():
    """测试省份和地级市简称功能"""
    # 创建测试数据 - 部分省份
    data = {
        "省份": ["黑龙江省", "内蒙古自治区", "新疆维吾尔自治区"],
        "GDP": [15901, 23159, 17741],
    }
    df_province = pd.DataFrame(data)
    df_province.set_index("省份", inplace=True)

    # 创建测试数据 - 自治州
    data_city = {
        "地级市": [
            "阿坝藏族羌族自治州",
            "甘孜藏族自治州",
            "凉山彝族自治州",
            "德宏傣族景颇族自治州",
            "大理白族自治州",
        ],
        "人口": [82.3, 116.4, 515.4, 131.8, 342.9],
    }
    df_city = pd.DataFrame(data_city)
    df_city.set_index("地级市", inplace=True)

    # 创建 1x2 网格图
    f = plt.figure(
        FigureClass=GridFigure,
        nrows=1,
        ncols=2,
        width=16,
        height=6,
    )

    # 测试5：省份地图对比
    f.plot(
        kind="map",
        data=df_province,
        level="province",
        scope="national",
        ax_index=0,
        value_column="GDP",
        label_column="GDP",
        label_format="{index}",
        label_fontsize=10,
        use_abbr=True,
        title="省份地图 - 简称",
    )

    # 测试6：地级市地图对比
    f.plot(
        kind="map",
        data=df_city,
        level="prefecture",
        scope="national",
        ax_index=1,
        value_column="人口",
        label_column="人口",
        label_format="{index}",
        label_fontsize=8,
        use_abbr=True,
        title="自治州地图 - 简称",
    )

    # 保存图片
    output_dir = os.path.join(project_root, "example", "plots")
    output_path = os.path.join(output_dir, "地图_省市简称测试.png")
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"图片已保存至: {output_path}")
    plt.show()


if __name__ == "__main__":
    print("=" * 60)
    print("测试1: 区县层级简称功能")
    print("=" * 60)
    test_county_abbr()

    print("\n" + "=" * 60)
    print("测试2: 省份和地级市简称功能")
    print("=" * 60)
    test_province_city_abbr()
