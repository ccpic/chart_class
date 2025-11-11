"""
颜色管理系统测试
运行: python -m pytest tests/test_color_manager.py -v
或直接: python tests/test_color_manager.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from chart.color.color_manager import ColorManager, ColorMapping
import tempfile
import json
from pathlib import Path


def test_color_manager_basic():
    """测试基本 CRUD 操作"""
    # 使用临时文件
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        temp_path = f.name

    try:
        manager = ColorManager(json_path=temp_path)

        # 测试添加
        assert manager.add("测试颜色1", "#FF0000", category="test")
        assert len(manager.to_dict()) == 1

        # 重新加载以验证持久化
        manager2 = ColorManager(json_path=temp_path)
        mapping = manager2.get("测试颜色1")
        assert mapping is not None
        assert mapping.name == "测试颜色1"
        assert mapping.color == "#FF0000"
        assert mapping.category == "test"

        # 测试不覆盖
        assert not manager.add("测试颜色1", "#00FF00", overwrite=False)
        assert manager.get_color("测试颜色1") == "#FF0000"

        # 测试覆盖
        assert manager.add("测试颜色1", "#00FF00", overwrite=True)
        assert manager.get_color("测试颜色1") == "#00FF00"

        # 测试更新
        assert manager.update("测试颜色1", color="#0000FF")
        assert manager.get_color("测试颜色1") == "#0000FF"

        # 测试删除
        assert manager.delete("测试颜色1")
        assert manager.get("测试颜色1") is None

        print("✅ 基本 CRUD 测试通过")

    finally:
        # 清理临时文件
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_color_aliases():
    """测试别名功能"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        temp_path = f.name

    try:
        manager = ColorManager(json_path=temp_path)

        # 添加带别名的颜色
        manager.add(
            "测试药品", "#FF5733", category="drug", aliases=["TestDrug", "药品A"]
        )

        # 通过主名称查询
        assert manager.get_color("测试药品") == "#FF5733"

        # 通过别名查询
        assert manager.get_color("TestDrug") == "#FF5733"
        assert manager.get_color("药品A") == "#FF5733"

        print("✅ 别名测试通过")

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_list_and_search():
    """测试列表和搜索功能"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        temp_path = f.name

    try:
        manager = ColorManager(json_path=temp_path)

        # 添加多个颜色
        manager.add("药品A", "#FF0000", category="drug", description="治疗高血压")
        manager.add("药品B", "#00FF00", category="drug", description="治疗糖尿病")
        manager.add("疾病X", "#0000FF", category="disease")

        # 测试列出所有
        all_colors = manager.list_all()
        assert len(all_colors) >= 3

        # 测试按分类筛选
        drugs = manager.list_all(category="drug")
        assert len(drugs) == 2

        # 测试搜索
        results = manager.list_all(search="高血压")
        assert len(results) >= 1
        assert any(c.name == "药品A" for c in results)

        # 测试获取分类列表
        categories = manager.get_categories()
        assert "drug" in categories
        assert "disease" in categories

        print("✅ 列表和搜索测试通过")

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_persistence():
    """测试持久化"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        temp_path = f.name

    try:
        # 第一个管理器：添加数据
        manager1 = ColorManager(json_path=temp_path)
        manager1.add("持久化测试", "#ABCDEF")

        # 第二个管理器：从文件加载
        manager2 = ColorManager(json_path=temp_path)
        assert manager2.get_color("持久化测试") == "#ABCDEF"

        print("✅ 持久化测试通过")

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_export_typescript():
    """测试导出 TypeScript"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json_path = f.name

    with tempfile.NamedTemporaryFile(mode="w", suffix=".ts", delete=False) as f:
        ts_path = f.name

    try:
        manager = ColorManager(json_path=json_path)
        manager.add("测试1", "#FF0000", category="test1")
        manager.add("测试2", "#00FF00", category="test2")

        # 导出
        manager.export_to_typescript(ts_path)

        # 验证文件存在
        assert os.path.exists(ts_path)

        # 验证内容
        with open(ts_path, "r", encoding="utf-8") as f:
            content = f.read()
            assert "export const COLOR_DICT" in content
            assert '"测试1": "#FF0000"' in content
            assert '"测试2": "#00FF00"' in content

        print("✅ TypeScript 导出测试通过")

    finally:
        if os.path.exists(json_path):
            os.remove(json_path)
        if os.path.exists(ts_path):
            os.remove(ts_path)


def run_all_tests():
    """运行所有测试"""
    print("🧪 开始测试颜色管理系统...\n")

    try:
        test_color_manager_basic()
        test_color_aliases()
        test_list_and_search()
        test_persistence()
        test_export_typescript()

        print("\n✅ 所有测试通过！")
        return True

    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
