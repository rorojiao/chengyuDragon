#!/bin/bash
# 成语接龙游戏启动器

APP_DIR="/Users/jiaojunze/Library/Mobile Documents/com~apple~CloudDocs/working_MAC/chengyuDragon"
PYTHON_EXE="/opt/homebrew/opt/python@3.13/bin/python3.13"

echo "=== 成语接龙游戏 ==="
echo ""

cd "$APP_DIR"

# 检查Python
if [ ! -f "$PYTHON_EXE" ]; then
    echo "错误: 找不到Python 3.13"
    echo "正在尝试使用系统Python..."
    PYTHON_EXE="python3"
fi

echo "Python路径: $PYTHON_EXE"
echo "工作目录: $APP_DIR"
echo ""

# 检查依赖
echo "检查依赖..."
$PYTHON_EXE -c "import PyQt6" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "缺少依赖，正在安装..."
    $PYTHON_EXE -m pip install --user --break-system-packages PyQt6 PyYAML requests pypinyin httpx
    echo ""
fi

# 清理缓存（确保使用最新代码）
echo "清理Python缓存..."
find . -name "*.pyc" -delete 2>/dev/null
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
echo "缓存已清理"
echo ""

# 运行游戏
echo "启动游戏..."
echo "--------------------"
$PYTHON_EXE main.py
