"""
全面测试所有图表类型的模块化结构
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from figure import GridFigure


def test_bar():
    """测试柱状图"""
    print("\n测试 PlotBar...")
    df = pd.DataFrame(
        {
            "产品A": [100, 120, 110],
            "产品B": [80, 90, 95],
        },
        index=["Q1", "Q2", "Q3"],
    )

    f = plt.figure(FigureClass=GridFigure, width=10, height=6)
    f.plot(kind="bar", data=df, ax_index=0)
    f.save(savepath="test_outputs/test_bar.png")
    print("  ✓ PlotBar 测试通过")


def test_line():
    """测试折线图"""
    print("\n测试 PlotLine...")
    df = pd.DataFrame(
        {
            "系列1": [10, 15, 13, 17],
            "系列2": [8, 12, 11, 14],
        },
        index=["Jan", "Feb", "Mar", "Apr"],
    )

    f = plt.figure(FigureClass=GridFigure, width=10, height=6)
    f.plot(kind="line", data=df, ax_index=0)
    f.save(savepath="test_outputs/test_line.png")
    print("  ✓ PlotLine 测试通过")


def test_area():
    """测试面积图"""
    print("\n测试 PlotArea...")
    df = pd.DataFrame(
        {
            "系列1": [10, 15, 13, 17],
            "系列2": [8, 12, 11, 14],
        },
        index=["Jan", "Feb", "Mar", "Apr"],
    )

    f = plt.figure(FigureClass=GridFigure, width=10, height=6)
    f.plot(kind="area", data=df, ax_index=0, stacked=True)
    f.save(savepath="test_outputs/test_area.png")
    print("  ✓ PlotArea 测试通过")


def test_barh():
    """测试水平柱状图"""
    print("\n测试 PlotBarh...")
    df = pd.DataFrame(
        {
            "产品A": [100, 120, 110],
            "产品B": [80, 90, 95],
        },
        index=["Q1", "Q2", "Q3"],
    )

    f = plt.figure(FigureClass=GridFigure, width=10, height=6)
    f.plot(kind="barh", data=df, ax_index=0)
    f.save(savepath="test_outputs/test_barh.png")
    print("  ✓ PlotBarh 测试通过")


def test_bubble():
    """测试气泡图"""
    print("\n测试 PlotBubble...")
    np.random.seed(42)
    df = pd.DataFrame(
        {
            "x": np.random.randn(20) * 10 + 50,
            "y": np.random.randn(20) * 5 + 25,
            "size": np.random.rand(20) * 100 + 10,
        },
        index=[f"Point{i}" for i in range(20)],
    )

    f = plt.figure(FigureClass=GridFigure, width=10, height=8)
    f.plot(kind="bubble", data=df, ax_index=0, label_limit=5)
    f.save(savepath="test_outputs/test_bubble.png")
    print("  ✓ PlotBubble 测试通过")


def test_pie():
    """测试饼图"""
    print("\n测试 PlotPie...")
    df = pd.DataFrame(
        {"values": [30, 25, 20, 15, 10]},
        index=["类别A", "类别B", "类别C", "类别D", "类别E"],
    )

    f = plt.figure(FigureClass=GridFigure, width=10, height=8)
    f.plot(kind="pie", data=df, ax_index=0)
    f.save(savepath="test_outputs/test_pie.png")
    print("  ✓ PlotPie 测试通过")


def test_heatmap():
    """测试热力图"""
    print("\n测试 PlotHeatmap...")
    df = pd.DataFrame(
        np.random.rand(5, 4) * 100,
        columns=["指标1", "指标2", "指标3", "指标4"],
        index=["A", "B", "C", "D", "E"],
    )

    f = plt.figure(FigureClass=GridFigure, width=10, height=8)
    f.plot(kind="heatmap", data=df, ax_index=0)
    f.save(savepath="test_outputs/test_heatmap.png")
    print("  ✓ PlotHeatmap 测试通过")


def main():
    """运行所有测试"""
    import os

    # 创建输出目录
    os.makedirs("test_outputs", exist_ok=True)

    print("=" * 60)
    print("开始测试模块化结构的所有图表类型")
    print("=" * 60)

    tests = [
        test_bar,
        test_line,
        test_area,
        test_barh,
        test_bubble,
        test_pie,
        test_heatmap,
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"  ✗ {test_func.__name__} 失败: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"测试完成: {passed} 通过, {failed} 失败")
    print("=" * 60)

    if failed == 0:
        print("\n🎉 所有测试通过！模块化重构成功！")
        print("\n生成的图表保存在 test_outputs/ 目录中")
    else:
        print(f"\n⚠️  有 {failed} 个测试失败，请检查错误信息")


if __name__ == "__main__":
    main()
