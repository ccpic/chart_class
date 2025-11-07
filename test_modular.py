"""
Test script to verify the modular structure works correctly.
"""

import matplotlib.pyplot as plt
import pandas as pd
from figure import GridFigure

# 创建测试数据
df = pd.DataFrame(
    {
        "产品A": [100, 120, 110, 130],
        "产品B": [80, 90, 95, 100],
        "产品C": [60, 70, 75, 80],
    },
    index=["Q1", "Q2", "Q3", "Q4"],
)

print("✓ 数据创建成功")

# 测试创建图形
try:
    f = plt.figure(
        FigureClass=GridFigure,
        width=15,
        height=6,
        ncols=1,
        fontsize=11,
        style={
            "title": "测试柱状图 - 模块化结构",
        },
    )
    print("✓ GridFigure 创建成功")
except Exception as e:
    print(f"✗ GridFigure 创建失败: {e}")
    exit(1)

# 测试绘图
try:
    f.plot(
        kind="bar",
        data=df,
        ax_index=0,
        show_total_label=True,
    )
    print("✓ Bar图绘制成功")
except Exception as e:
    print(f"✗ Bar图绘制失败: {e}")
    exit(1)

# 测试保存
try:
    savepath = f.save(savepath="test_modular_structure.png")
    print(f"✓ 图表保存成功: {savepath}")
except Exception as e:
    print(f"✗ 图表保存失败: {e}")
    exit(1)

print("\n🎉 所有测试通过！模块化结构工作正常。")
