"""
地图标签功能综合演示

演示标签的所有功能：
1. 字体大小控制
2. 占位符格式化 ({index}, {value})
3. 简称显示 (use_abbr)
"""

import os
import sys
import pandas as pd

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from chart import GridFigure
import matplotlib.pyplot as plt


def demo_all_features():
    """综合演示所有标签功能"""
    print("=" * 60)
    print("地图标签功能综合演示")
    print("=" * 60)

    # 创建普洱市区县数据
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
        "GDP": [120, 85, 95, 110, 105, 75, 55, 60, 140, 45],
    }
    df = pd.DataFrame(data)
    df.set_index("区县", inplace=True)

    # 创建 2x3 网格图
    f = plt.figure(
        FigureClass=GridFigure,
        nrows=2,
        ncols=3,
        width=18,
        height=12,
    )

    # 示例1：基础标签 - 只显示数值
    print("\n示例1：基础标签 - 只显示数值")
    f.plot(
        kind="map",
        data=df,
        level="county",
        scope="cities",
        regions=["普洱"],
        ax_index=0,
        value_column="人口",
        label_column="人口",
        title="基础标签\n直接显示数值",
    )

    # 示例2：使用 {value} 占位符 + 单位
    print("示例2：使用占位符 + 单位")
    f.plot(
        kind="map",
        data=df,
        level="county",
        scope="cities",
        regions=["普洱"],
        ax_index=1,
        value_column="人口",
        label_column="人口",
        label_format="{value}万",
        title="占位符格式化\n{value}万人",
    )

    # 示例3：使用 {index} 显示区域名
    print("示例3：使用 {index} 显示区域名")
    f.plot(
        kind="map",
        data=df,
        level="county",
        scope="cities",
        regions=["普洱"],
        ax_index=2,
        value_column="GDP",
        label_column="GDP",
        label_format="{index}",
        label_fontsize=7,
        title="显示完整区域名\n{index}",
    )

    # 示例4：{index} + {value} 组合
    print("示例4：{index} + {value} 组合")
    f.plot(
        kind="map",
        data=df,
        level="county",
        scope="cities",
        regions=["普洱"],
        ax_index=3,
        value_column="人口",
        label_column="人口",
        label_format="{index}\n{value}万人",
        label_fontsize=6,
        title="组合显示\n{index}\\n{value}万人",
    )

    # 示例5：使用简称 (use_abbr=True)
    print("示例5：使用简称")
    f.plot(
        kind="map",
        data=df,
        level="county",
        scope="cities",
        regions=["普洱"],
        ax_index=4,
        value_column="GDP",
        label_column="GDP",
        label_format="{index}",
        label_fontsize=8,
        use_abbr=True,
        title="使用简称\nuse_abbr=True",
    )

    # 示例6：简称 + 数值 + 大字体
    print("示例6：简称 + 数值 + 大字体")
    f.plot(
        kind="map",
        data=df,
        level="county",
        scope="cities",
        regions=["普洱"],
        ax_index=5,
        value_column="人口",
        label_column="人口",
        label_format="{index}\n{value}",
        label_fontsize=10,
        use_abbr=True,
        title="简称+数值+大字体\nfontsize=10",
    )

    # 保存图片
    output_dir = os.path.join(project_root, "example", "plots")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "地图标签功能演示.png")
    plt.savefig(output_path, dpi=200, bbox_inches="tight")
    print(f"\n✓ 图片已保存至: {output_path}")

    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)
    print("\n标签功能总结：")
    print("  1. label_column: 指定要显示的数据列")
    print("  2. label_format: 使用占位符格式化标签")
    print("     - {index}: 区域名称")
    print("     - {value}: 数据值")
    print("     - 可组合使用，如 '{index}\\n{value}万'")
    print("  3. label_fontsize: 控制标签字体大小 (默认8)")
    print("  4. use_abbr: 使用简称显示区域名 (默认False)")
    print("     - 省份: 黑龙江省 → 黑龙江")
    print("     - 自治区: 内蒙古自治区 → 内蒙古")
    print("     - 自治县: 宁洱哈尼族彝族自治县 → 宁洱")
    print()


if __name__ == "__main__":
    demo_all_features()
