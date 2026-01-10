# 成语接龙游戏

一个基于Python和PyQt6开发的成语接龙游戏，支持与本地大语言模型（通过LM Studio API）进行对战。

## 功能特性

- 🎮 **图形化界面**: 新中式风格的美观界面
- 🤖 **AI对战**: 集成本地大语言模型，智能接龙
- ⚙️ **灵活配置**: 图形化配置API和游戏参数
- 📚 **成语数据库**: 内置丰富的成语数据
- 🎯 **多种难度**: 简单/普通/困难三种模式
- ⏱️ **计时功能**: 可选的回合时间限制
- 💡 **提示系统**: 有限的提示次数帮助玩家

## 系统要求

- Python 3.10+
- Windows 10/11, macOS 10.15+, 或 Linux
- 4GB+ RAM
- LM Studio（用于本地AI）

## 安装

### 1. 克隆仓库

```bash
git clone https://github.com/yourusername/chengyuDragon.git
cd chengyuDragon
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置LM Studio

1. 下载并安装 [LM Studio](https://lmstudio.ai/)
2. 在LM Studio中加载一个中文语言模型
3. 启动LM Studio API服务器（默认端口：1234）
4. 在游戏设置中配置API地址和模型名称

## 运行

```bash
python main.py
```

## 游戏规则

1. 游戏开始时，由系统或玩家随机出一个成语
2. 玩家需要在限时内输入一个成语，其第一个字必须与前一个成语的最后一个字相同
3. AI会根据玩家给出的成语进行接龙
4. 无法给出合法成语或重复使用成语的一方判负

## 配置说明

配置文件位于 `config.yaml`，可配置以下选项：

- **API设置**: LM Studio API地址和模型名称
- **游戏设置**: 难度、时间限制、是否允许同音字、提示次数
- **界面设置**: 主题、字体大小、动画和音效开关

## 项目结构

```
chengyuDragon/
├── main.py              # 应用入口
├── requirements.txt     # 依赖列表
├── config.yaml          # 配置文件
├── src/                 # 源代码
│   ├── gui/            # GUI模块
│   ├── core/           # 核心逻辑
│   ├── ai/             # AI服务
│   ├── data/           # 数据管理
│   ├── config/         # 配置管理
│   └── utils/          # 工具函数
├── resources/          # 资源文件
│   ├── idioms.db      # 成语数据库
│   ├── icons/         # 图标
│   ├── sounds/        # 音效
│   └── fonts/         # 字体
└── tests/             # 测试代码
```

## 开发

### 运行测试

```bash
pytest tests/
```

### 打包

使用PyInstaller打包：

```bash
pyinstaller chengyuDragon.spec
```

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

MIT License

## 致谢

- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/)
- [LM Studio](https://lmstudio.ai/)
- [pypinyin](https://github.com/mozillazg/pypinyin)
