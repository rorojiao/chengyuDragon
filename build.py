#!/usr/bin/env python3
"""
构建脚本 - 用于创建可分发的应用包
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def get_user_python_path():
    """获取用户Python的路径"""
    result = subprocess.run(
        ['python3', '-c', 'import sys; print(sys.executable)'],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        return result.stdout.strip()
    return 'python3'


def get_user_site_packages():
    """获取用户site-packages路径"""
    result = subprocess.run(
        ['python3', '-c', 'import site; print(site.getusersitepackages())'],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        return result.stdout.strip()
    return ''


def build_app():
    """构建应用"""
    print("=" * 60)
    print("成语接龙游戏 - 构建脚本")
    print("=" * 60)

    # 项目根目录
    root_dir = Path(__file__).parent
    build_dir = root_dir / "build"
    dist_dir = root_dir / "dist"

    # 清理旧的构建
    print("\n1. 清理旧的构建文件...")
    if build_dir.exists():
        shutil.rmtree(build_dir)
    if dist_dir.exists():
        shutil.rmtree(dist_dir)

    # 创建构建目录
    build_dir.mkdir(parents=True, exist_ok=True)
    dist_dir.mkdir(parents=True, exist_ok=True)

    # 获取Python信息
    python_exe = get_user_python_path()
    site_packages = get_user_site_packages()
    print(f"Python路径: {python_exe}")
    print(f"Site-packages: {site_packages}")

    # 复制所有源文件
    print("2. 复制源文件...")

    # 创建macOS应用包结构
    macos_app = dist_dir / "成语接龙.app"
    contents_dir = macos_app / "Contents"
    macos_dir = contents_dir / "MacOS"
    resources_app_dir = contents_dir / "Resources"

    macos_dir.mkdir(parents=True, exist_ok=True)
    resources_app_dir.mkdir(parents=True, exist_ok=True)

    # 复制源代码
    src_dir = resources_app_dir / "src"
    shutil.copytree(root_dir / "src", src_dir)

    # 复制资源
    resources_res_dir = resources_app_dir / "resources"
    shutil.copytree(root_dir / "resources", resources_res_dir, dirs_exist_ok=True)

    # 复制主文件
    shutil.copy(root_dir / "main.py", resources_app_dir)
    shutil.copy(root_dir / "config.yaml", resources_app_dir)

    # 创建Info.plist
    print("3. 创建Info.plist...")
    info_plist = contents_dir / "Info.plist"
    with open(info_plist, 'w') as f:
        f.write('''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>launch.sh</string>
    <key>CFBundleIdentifier</key>
    <string>com.yourcompany.chengyudragon</string>
    <key>CFBundleName</key>
    <string>成语接龙</string>
    <key>CFBundleDisplayName</key>
    <string>成语接龙</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>LSMinimumSystemVersion</key>
    <string>10.15</string>
</dict>
</plist>
''')

    # 创建启动脚本
    print("4. 创建启动脚本...")
    launch_script = macos_dir / "launch.sh"
    with open(launch_script, 'w') as f:
        f.write(f'''#!/bin/bash
# 成语接龙游戏启动脚本

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${{BASH_SOURCE[0]}}" )" && pwd )"
RESOURCE_DIR="$SCRIPT_DIR/../Resources"

cd "$RESOURCE_DIR"

# 使用用户Python运行
echo "正在启动成语接龙游戏..."
echo "工作目录: $RESOURCE_DIR"

# 检查PyQt6
if ! {python_exe} -c "import PyQt6" 2>/dev/null; then
    osascript -e 'display dialog "缺少PyQt6依赖包\\n\\n请运行以下命令安装:\\npip3 install PyQt6" buttons{{"OK"}}' 2>/dev/null || \
    echo "错误: 缺少PyQt6依赖包，请运行: pip3 install PyQt6"
    exit 1
fi

# 运行应用
exec {python_exe} main.py
''')

    os.chmod(launch_script, 0o755)

    print(f"✓ 启动脚本已创建: {launch_script}")

    # 创建README
    print("5. 创建使用说明...")
    readme = dist_dir / "README.txt"
    with open(readme, 'w', encoding='utf-8') as f:
        f.write('''成语接龙游戏 v1.0.0
===================

快速开始：
--------
1. 双击 "成语接龙.app" 启动游戏
2. 如果提示缺少依赖，运行: pip3 install -r requirements.txt

命令行运行：
---------
cd "$(dirname "$0")"
python3 main.py

注意事项：
---------
- 确保已安装Python 3.10或更高版本
- 首次运行需要安装依赖: pip3 install -r requirements.txt

LM Studio配置（可选）：
---------------------
如果要使用完整AI功能：
1. 安装LM Studio: https://lmstudio.ai/
2. 加载中文语言模型
3. 启动API服务器
4. 在游戏设置中配置API地址

更多信息请查看项目文档。
''')

    # 创建安装脚本
    install_script = dist_dir / "install.sh"
    with open(install_script, 'w') as f:
        f.write('''#!/bin/bash
# 成语接龙游戏 - 依赖安装脚本

echo "成语接龙游戏 - 依赖安装"
echo "======================"
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python 3"
    echo "请先安装Python 3.10或更高版本"
    exit 1
fi

echo "Python版本: $(python3 --version)"
echo ""

# 安装依赖
echo "安装依赖包..."
pip3 install --user PyQt6 PyYAML requests pypinyin httpx

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ 依赖安装完成！"
    echo "现在可以运行 '成语接龙.app' 了"
else
    echo ""
    echo "✗ 依赖安装失败"
    echo "请检查网络连接或手动安装"
fi
''')
    os.chmod(install_script, 0o755)

    print("\n" + "=" * 60)
    print("构建完成！")
    print("=" * 60)
    print(f"输出目录: {dist_dir}")
    print()
    print("文件列表:")
    print(f"  - 成语接龙.app (macOS应用)")
    print(f"  - install.sh (依赖安装脚本)")
    print(f"  - README.txt (使用说明)")
    print()
    print("首次运行请先执行: ./install.sh")
    print("或手动安装: pip3 install PyQt6 PyYAML requests pypinyin httpx")


if __name__ == '__main__':
    build_app()
