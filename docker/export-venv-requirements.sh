#!/bin/bash
# 从本地 .venv 导出依赖到 requirements-venv.txt

echo "正在从 .venv 导出 Python 包依赖..."

# 检查 .venv 是否存在
if [ ! -f "../.venv/bin/pip" ]; then
    echo "❌ 错误: 未找到 .venv 虚拟环境"
    echo "请确保在项目根目录下已创建并激活 .venv"
    exit 1
fi

# 激活虚拟环境并导出依赖
source ../.venv/bin/activate

if [ $? -ne 0 ]; then
    echo "❌ 错误: 无法激活虚拟环境"
    exit 1
fi

# 导出依赖到 requirements-venv.txt
echo "正在导出依赖列表..."
pip freeze > requirements-venv.txt

if [ $? -ne 0 ]; then
    echo "❌ 导出失败"
    exit 1
fi

# 统计导出的包数量
count=$(wc -l < requirements-venv.txt)

echo ""
echo "✅ 成功导出 $count 个包到 requirements-venv.txt"
echo ""
echo "📝 文件位置: docker/requirements-venv.txt"
echo ""
echo "💡 提示: Docker 构建时会自动使用此文件中的包版本"
echo ""

