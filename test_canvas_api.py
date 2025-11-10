"""
测试 Canvas API
验证前后端数据格式是否匹配
"""

import requests
import json

# 测试数据
test_request = {
    "canvas": {
        "width": 15,
        "height": 6,
        "rows": 1,
        "cols": 2,
        "wspace": 0.3,
        "hspace": 0.3,
        "title": "测试画布",
        "show_legend": True,
        "legend_loc": "upper right",
        "legend_ncol": 1,
        "bbox_to_anchor": [1.0, 1.0],
        "label_outer": False,
    },
    "subplots": [
        {
            "subplot_id": "test-1",
            "ax_index": 0,
            "chart_type": "bar",
            "data": {
                "columns": ["销量", "目标"],
                "index": ["产品A", "产品B", "产品C"],
                "data": [[120, 100], [90, 100], [150, 100]],
            },
            "params": {"stacked": True, "show_label": True},
        },
        {
            "subplot_id": "test-2",
            "ax_index": 1,
            "chart_type": "line",
            "data": {
                "columns": ["营收", "成本"],
                "index": ["1月", "2月", "3月"],
                "data": [[50, 30], [60, 35], [70, 40]],
            },
            "params": {"marker": "o", "linewidth": 2},
        },
    ],
}

print("发送测试请求...")
print(json.dumps(test_request, indent=2, ensure_ascii=False))

try:
    response = requests.post(
        "http://localhost:8000/api/render/canvas",
        json=test_request,
        headers={"Content-Type": "application/json"},
    )

    print(f"\n状态码: {response.status_code}")

    if response.status_code == 200:
        print("✅ 渲染成功!")
        print(f"图片大小: {len(response.content)} bytes")

        # 保存图片
        with open("test_outputs/canvas_test.png", "wb") as f:
            f.write(response.content)
        print("图片已保存到 test_outputs/canvas_test.png")
    else:
        print(f"❌ 渲染失败: {response.status_code}")
        try:
            error_data = response.json()
            print(f"错误详情: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
        except Exception:
            print(f"错误响应: {response.text}")

except Exception as e:
    print(f"❌ 请求失败: {str(e)}")
