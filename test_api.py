"""测试后端 API 的简单脚本"""

import requests
import json

# 测试数据
test_data = {
    "data": {
        "columns": ["品牌A", "品牌B", "品牌C"],
        "index": ["Q1", "Q2", "Q3"],
        "data": [[100, 200, 150], [120, 180, 160], [110, 220, 170]],
    },
    "params": {
        "chart_type": "bar",
        "stacked": True,
        "show_label": True,
        "label_formatter": "{abs}",
    },
}

# 发送请求
url = "http://localhost:8000/api/render"
print(f"发送请求到: {url}")
print(f"数据: {json.dumps(test_data, indent=2, ensure_ascii=False)}")

try:
    response = requests.post(url, json=test_data)
    print(f"\n状态码: {response.status_code}")

    if response.status_code == 200:
        # 保存图片
        with open("test_output.png", "wb") as f:
            f.write(response.content)
        print("✅ 成功！图片已保存到 test_output.png")
    else:
        print(f"❌ 错误: {response.text}")
except Exception as e:
    print(f"❌ 异常: {str(e)}")
