#!/bin/bash
# 成语接龙游戏 - 简单启动脚本

cd "/Users/jiaojunze/Library/Mobile Documents/com~apple~CloudDocs/working_MAC/chengyuDragon"

# 检查依赖
echo "检查依赖..."
if ! /opt/homebrew/opt/python@3.13/bin/python3.13 -c "import PyQt6" 2>/dev/null; then
    echo "缺少依赖，正在安装..."
    /opt/homebrew/opt/python@3.13/bin/python3.13 -m pip install --user --break-system-packages PyQt6 PyYAML requests pypinyin httpx
fi

# 运行游戏
echo "启动游戏..."
/opt/homebrew/opt/python@3.13/bin/python3.13 main.py
