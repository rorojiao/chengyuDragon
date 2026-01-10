# 成语接龙游戏 - 技术开发文档

## 1. 技术栈选型

### 1.1 核心技术
- **编程语言**: Python 3.10+
- **GUI框架**: PyQt6 / PySide6
- **HTTP客户端**: requests / httpx
- **数据存储**: SQLite3 + JSON
- **配置管理**: configparser / YAML

### 1.2 选型理由

#### PyQt6/PySide6
- **优势**:
  - 成熟的跨平台GUI框架
  - 丰富的组件库
  - 优秀的文档和社区支持
  - 支持QSS样式表，易于实现自定义UI
  - 信号槽机制便于事件处理

- **替代方案对比**:
  - Tkinter：界面过于简陋，不适合现代游戏UI
  - Electron：资源占用大，开发复杂度高
  - Unity/Godot：对于文字游戏过于重量级

#### SQLite3
- **优势**:
  - 轻量级，无需额外服务
  - 内置于Python标准库
  - 适合成语词典的结构化数据
  - 支持高效的查询和索引

## 2. 项目架构

### 2.1 整体架构
```
┌─────────────────────────────────────────────────────┐
│                   GUI Layer                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │MainMenu  │  │GameScreen│  │Settings  │          │
│  │  Window  │  │  Window  │  │  Panel   │          │
│  └──────────┘  └──────────┘  └──────────┘          │
└─────────────────────────────────────────────────────┘
                       ↓↑
┌─────────────────────────────────────────────────────┐
│                  Application Layer                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │ Game     │  │ AI       │  │Config    │          │
│  │ Manager  │  │ Service  │  │ Manager  │          │
│  └──────────┘  └──────────┘  └──────────┘          │
└─────────────────────────────────────────────────────┘
                       ↓↑
┌─────────────────────────────────────────────────────┐
│                   Service Layer                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │Idiom     │  │LM Studio │  │Storage   │          │
│  │Database  │  │  API     │  │Service   │          │
│  └──────────┘  └──────────┘  └──────────┘          │
└─────────────────────────────────────────────────────┘
                       ↓↑
┌─────────────────────────────────────────────────────┐
│                   Data Layer                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │ SQLite   │  │  JSON    │  │  Cache   │          │
│  │Database  │  │  Files   │  │  Memory  │          │
│  └──────────┘  └──────────┘  └──────────┘          │
└─────────────────────────────────────────────────────┘
```

### 2.2 目录结构
```
chengyuDragon/
├── main.py                      # 应用入口
├── requirements.txt             # 依赖列表
├── config.yaml                  # 配置文件
├── README.md                    # 项目说明
│
├── src/                         # 源代码目录
│   ├── __init__.py
│   │
│   ├── gui/                     # GUI模块
│   │   ├── __init__.py
│   │   ├── main_window.py      # 主窗口
│   │   ├── main_menu.py        # 主菜单界面
│   │   ├── game_screen.py      # 游戏界面
│   │   ├── settings_panel.py   # 设置面板
│   │   ├── components/         # 自定义组件
│   │   │   ├── __init__.py
│   │   │   ├── idiom_card.py   # 成语卡片组件
│   │   │   ├── input_box.py    # 输入框组件
│   │   │   └── timer_widget.py # 计时器组件
│   │   └── styles/             # 样式文件
│   │       └── style.qss       # QSS样式表
│   │
│   ├── core/                    # 核心逻辑模块
│   │   ├── __init__.py
│   │   ├── game_manager.py     # 游戏管理器
│   │   ├── game_state.py       # 游戏状态
│   │   ├── idiom_validator.py  # 成语验证器
│   │   └── game_rules.py       # 游戏规则
│   │
│   ├── ai/                      # AI模块
│   │   ├── __init__.py
│   │   ├── ai_service.py       # AI服务基类
│   │   ├── lmstudio_client.py  # LM Studio API客户端
│   │   └── prompt_templates.py # 提示词模板
│   │
│   ├── data/                    # 数据模块
│   │   ├── __init__.py
│   │   ├── database.py         # 数据库管理
│   │   ├── idiom_repository.py # 成语数据仓库
│   │   └── models.py           # 数据模型
│   │
│   ├── config/                  # 配置模块
│   │   ├── __init__.py
│   │   ├── config_manager.py   # 配置管理器
│   │   └── defaults.py         # 默认配置
│   │
│   └── utils/                   # 工具模块
│       ├── __init__.py
│       ├── pinyin.py           # 拼音转换工具
│       ├── timer.py            # 计时器工具
│       └── logger.py           # 日志工具
│
├── resources/                   # 资源文件
│   ├── idioms.db               # 成语数据库
│   ├── icons/                  # 图标资源
│   │   ├── app_icon.ico
│   │   ├── settings.png
│   │   └── ...
│   ├── sounds/                 # 音效文件
│   │   ├── success.wav
│   │   ├── fail.wav
│   │   └── ...
│   └── fonts/                  # 字体文件
│       └── chinese.ttf
│
├── data/                       # 数据文件目录
│   ├── idioms/                # 成语数据源
│   │   └── idioms.txt        # 成语源数据
│   └── exports/               # 导出文件
│
├── tests/                      # 测试目录
│   ├── __init__.py
│   ├── test_game_logic.py
│   ├── test_ai_service.py
│   └── test_database.py
│
└── docs/                       # 文档目录
    ├── GAME_DESIGN_DOC.md
    └── TECHNICAL_DOC.md
```

## 3. 核心模块设计

### 3.1 游戏管理器 (GameManager)

**职责**:
- 管理游戏流程和状态
- 协调玩家和AI的回合
- 判定游戏胜负
- 处理特殊情况

**接口设计**:
```python
class GameManager:
    def __init__(self, config: GameConfig):
        """初始化游戏管理器"""
        pass

    def start_game(self, starting_idiom: Optional[str] = None) -> None:
        """开始新游戏"""
        pass

    def submit_player_idiom(self, idiom: str) -> ValidationResult:
        """玩家提交成语"""
        pass

    def get_ai_response(self) -> str:
        """获取AI响应"""
        pass

    def end_game(self, winner: str) -> GameResult:
        """结束游戏"""
        pass

    def get_game_state(self) -> GameState:
        """获取当前游戏状态"""
        pass
```

### 3.2 成语验证器 (IdiomValidator)

**职责**:
- 验证成语是否合法
- 检查成语是否符合接龙规则
- 验证成语是否重复

**接口设计**:
```python
class IdiomValidator:
    def __init__(self, database: IdiomDatabase):
        """初始化验证器"""
        pass

    def is_valid_idiom(self, idiom: str) -> bool:
        """验证成语是否存在于数据库"""
        pass

    def check_chain_rule(self, prev_idiom: str, curr_idiom: str,
                        allow_homophone: bool = False) -> bool:
        """检查是否符合接龙规则"""
        pass

    def is_duplicate(self, idiom: str, used_idioms: Set[str]) -> bool:
        """检查成语是否重复使用"""
        pass

    def get_validation_error(self) -> Optional[str]:
        """获取验证错误信息"""
        pass
```

### 3.3 LM Studio API客户端 (LMStudioClient)

**职责**:
- 与LM Studio API通信
- 处理API请求和响应
- 管理连接状态

**接口设计**:
```python
class LMStudioClient:
    def __init__(self, base_url: str, model_name: str):
        """初始化客户端"""
        pass

    def test_connection(self) -> bool:
        """测试API连接"""
        pass

    def generate_idiom(self, prompt: str,
                      temperature: float = 0.7,
                      max_tokens: int = 100) -> str:
        """生成成语"""
        pass

    def set_model(self, model_name: str) -> None:
        """设置使用的模型"""
        pass

    def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        pass
```

**API调用示例**:
```python
# LM Studio API endpoint
POST http://localhost:1234/v1/chat/completions

Headers:
Content-Type: application/json

Body:
{
    "model": "model-name",
    "messages": [
        {
            "role": "system",
            "content": "你是一个成语接龙专家..."
        },
        {
            "role": "user",
            "content": "请用'龙'字开头接一个成语"
        }
    ],
    "temperature": 0.7,
    "max_tokens": 50
}
```

### 3.4 成语数据库 (IdiomDatabase)

**职责**:
- 管理成语数据
- 提供高效的查询接口
- 维护数据索引

**接口设计**:
```python
class IdiomDatabase:
    def __init__(self, db_path: str):
        """初始化数据库"""
        pass

    def get_idiom_by_name(self, name: str) -> Optional[Idiom]:
        """根据名称获取成语"""
        pass

    def get_idioms_by_starting_char(self, char: str) -> List[Idiom]:
        """根据首字获取成语列表"""
        pass

    def search_idioms(self, keyword: str,
                     limit: int = 10) -> List[Idiom]:
        """搜索成语"""
        pass

    def add_idiom(self, idiom: Idiom) -> bool:
        """添加成语"""
        pass

    def get_total_count(self) -> int:
        """获取成语总数"""
        pass
```

**数据库Schema**:
```sql
CREATE TABLE idioms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word TEXT NOT NULL UNIQUE,           -- 成语
    pinyin TEXT NOT NULL,                 -- 拼音
    first_char TEXT NOT NULL,             -- 首字
    last_char TEXT NOT NULL,              -- 尾字
    first_pinyin TEXT NOT NULL,           -- 首字拼音
    last_pinyin TEXT NOT NULL,            -- 尾字拼音
    explanation TEXT,                     -- 解释
    example TEXT,                         -- 例句
    difficulty INTEGER DEFAULT 1,          -- 难度 1-5
    frequency REAL DEFAULT 0.0,           -- 使用频率
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_first_char ON idioms(first_char);
CREATE INDEX idx_last_char ON idioms(last_char);
CREATE INDEX idx_first_pinyin ON idioms(first_pinyin);
CREATE INDEX idx_last_pinyin ON idioms(last_pinyin);
CREATE INDEX idx_difficulty ON idioms(difficulty);
```

## 4. 数据流设计

### 4.1 游戏流程数据流
```
用户输入成语
    ↓
GUI接收输入
    ↓
GameManager.submit_player_idiom()
    ↓
IdiomValidator验证
    ├─ 不合法 → 返回错误信息 → GUI显示错误
    └─ 合格 → 更新GameState → GUI更新显示
            ↓
        触发AI回合
            ↓
        LMStudioClient.generate_idiom()
            ↓
        AI返回成语
            ↓
        IValidator验证AI成语
            ├─ 不合法 → 重新生成
            └─ 合格 → 更新GameState → GUI更新显示
                    ↓
                等待玩家下一回合
```

### 4.2 配置数据流
```
用户修改配置
    ↓
SettingsPanel接收
    ↓
ConfigManager.update_config()
    ↓
验证配置有效性
    ├─ 无效 → 显示错误提示
    └─ 有效 → 保存到config.yaml
            ↓
        通知相关组件更新
            ↓
        应用新配置
```

## 5. 关键技术实现

### 5.1 成语验证逻辑

```python
class IdiomValidator:
    def validate(self, idiom: str, prev_idiom: str,
                 used_idioms: Set[str], config: GameConfig) -> ValidationResult:
        # 1. 检查是否为空
        if not idiom or not idiom.strip():
            return ValidationResult(False, "成语不能为空")

        # 2. 检查长度（通常成语为4字）
        if len(idiom) != 4:
            return ValidationResult(False, "成语必须是4个字")

        # 3. 检查是否存在于数据库
        if not self.db.is_valid_idiom(idiom):
            return ValidationResult(False, "这不是一个有效的成语")

        # 4. 检查是否重复
        if idiom in used_idioms:
            return ValidationResult(False, "这个成语已经使用过了")

        # 5. 检查接龙规则
        if prev_idiom:
            if config.allow_homophone:
                # 允许同音字
                if not self._check_homophone_match(prev_idiom, idiom):
                    return ValidationResult(False,
                        f"必须用'{prev_idiom[-1]}'的同音字开头")
            else:
                # 必须同字
                if idiom[0] != prev_idiom[-1]:
                    return ValidationResult(False,
                        f"必须用'{prev_idiom[-1]}'字开头")

        return ValidationResult(True, "")
```

### 5.2 AI提示词模板

```python
# 系统提示词
SYSTEM_PROMPT = """你是一个成语接龙专家。你需要：
1. 根据用户给出的字，说出一个以该字开头的成语
2. 只返回成语本身，不要任何解释
3. 确保成语准确有效
4. 选择常用的成语，避免过于生僻"""

# 用户提示词模板
USER_PROMPT_TEMPLATE = "请用'{char}'字开头接一个成语"

# 生成函数
def generate_ai_prompt(starting_char: str, difficulty: str) -> dict:
    temperature_map = {
        "easy": 0.9,      # 高随机性，选择多样化
        "normal": 0.7,    # 中等随机性
        "hard": 0.3       # 低随机性，选择精准
    }

    return {
        "model": "current_model",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT_TEMPLATE.format(char=starting_char)}
        ],
        "temperature": temperature_map.get(difficulty, 0.7),
        "max_tokens": 20
    }
```

### 5.3 异步API调用

```python
import asyncio
import httpx

class AsyncLMStudioClient:
    async def generate_idiom_async(self, prompt: str) -> str:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/v1/chat/completions",
                    json=prompt,
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"].strip()
            except httpx.TimeoutException:
                raise APIException("API请求超时")
            except httpx.HTTPError as e:
                raise APIException(f"API请求失败: {str(e)}")

# 在GUI中使用
class GameScreen(QWidget):
    def on_ai_turn(self):
        # 显示AI思考动画
        self.show_thinking_animation()

        # 创建后台线程
        worker = AIThread(self.ai_client, self.starting_char)
        worker.finished.connect(self.on_ai_response)
        worker.start()
```

### 5.4 拼音处理

```python
# 使用pypinyin库
from pypinyin import lazy_pinyin, Style

class PinyinUtils:
    @staticmethod
    def get_pinyin(text: str, style: str = 'normal') -> str:
        """获取文本的拼音"""
        pys = lazy_pinyin(text, style=Style.TONE)
        return ''.join(pys)

    @staticmethod
    def get_first_char_pinyin(char: str) -> str:
        """获取首字拼音"""
        pys = lazy_pinyin(char, style=Style.TONE)
        return pys[0] if pys else ""

    @staticmethod
    def compare_homophone(char1: str, char2: str) -> bool:
        """比较两个字的发音是否相同"""
        p1 = PinyinUtils.get_first_char_pinyin(char1)
        p2 = PinyinUtils.get_first_char_pinyin(char2)
        # 去掉声调比较
        return p1[:-1] == p2[:-1] if p1 and p2 else False
```

## 6. GUI实现细节

### 6.1 主窗口

```python
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("成语接龙")
        self.setFixedSize(1000, 700)

        # 创建中央堆叠窗口
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # 初始化各个界面
        self.init_screens()

        # 加载样式
        self.load_styles()

    def init_screens(self):
        from .main_menu import MainMenu
        from .game_screen import GameScreen
        from .settings_panel import SettingsPanel

        self.main_menu = MainMenu(self)
        self.game_screen = GameScreen(self)
        self.settings_panel = SettingsPanel(self)

        self.stacked_widget.addWidget(self.main_menu)
        self.stacked_widget.addWidget(self.game_screen)
        self.stacked_widget.addWidget(self.settings_panel)

    def show_main_menu(self):
        self.stacked_widget.setCurrentWidget(self.main_menu)

    def show_game_screen(self):
        self.stacked_widget.setCurrentWidget(self.game_screen)

    def show_settings(self):
        self.stacked_widget.setCurrentWidget(self.settings_panel)

    def load_styles(self):
        with open('src/gui/styles/style.qss', 'r', encoding='utf-8') as f:
            self.setStyleSheet(f.read())
```

### 6.2 成语卡片组件

```python
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve

class IdiomCard(QWidget):
    clicked = pyqtSignal()

    def __init__(self, idiom: str, is_player: bool = True):
        super().__init__()
        self.idiom = idiom
        self.is_player = is_player
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 15, 20, 15)

        # 角色标签
        role_label = QLabel("你" if self.is_player else "AI")
        role_label.setStyleSheet("font-size: 14px; color: #888;")

        # 成语文本
        idiom_label = QLabel(self.idiom)
        idiom_label.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: #333;
        """)
        idiom_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(role_label)
        layout.addWidget(idiom_label)
        self.setLayout(layout)

        # 设置卡片样式
        self.set_card_style()

    def set_card_style(self):
        bg_color = "#E8F5E9" if self.is_player else "#FFF3E0"
        border_color = "#4CAF50" if self.is_player else "#FF9800"

        self.setStyleSheet(f"""
            IdiomCard {{
                background-color: {bg_color};
                border: 2px solid {border_color};
                border-radius: 10px;
            }}
        """)

    def appear_animation(self):
        """出现动画"""
        self.setOpacity(0)
        animation = QPropertyAnimation(self, b"windowOpacity")
        animation.setDuration(300)
        animation.setStartValue(0)
        animation.setEndValue(1)
        animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        animation.start()
```

### 6.3 QSS样式表

```css
/* 全局样式 */
* {
    font-family: "Microsoft YaHei", "SimHei", sans-serif;
}

QWidget {
    background-color: #F5F5F5;
}

/* 主菜单 */
MainMenu {
    background-color: #FAFAFA;
}

#title_label {
    font-size: 64px;
    font-weight: bold;
    color: #D32F2F;
    qproperty-alignment: AlignCenter;
}

QPushButton {
    font-size: 20px;
    padding: 15px 50px;
    border-radius: 8px;
    background-color: #1976D2;
    color: white;
    border: none;
}

QPushButton:hover {
    background-color: #1565C0;
}

QPushButton:pressed {
    background-color: #0D47A1;
}

QPushButton:disabled {
    background-color: #BDBDBD;
}

/* 游戏界面 */
GameScreen {
    background-color: #FAFAFA;
}

#idiom_display_area {
    background-color: white;
    border-radius: 10px;
    border: 1px solid #E0E0E0;
}

#input_field {
    font-size: 24px;
    padding: 10px;
    border: 2px solid #9E9E9E;
    border-radius: 5px;
    background-color: white;
}

#input_field:focus {
    border: 2px solid #2196F3;
}

#submit_button {
    font-size: 18px;
    padding: 12px 40px;
    background-color: #4CAF50;
    color: white;
    border: none;
    border-radius: 5px;
}

#submit_button:hover {
    background-color: #45A049;
}

#hint_button {
    font-size: 18px;
    padding: 12px 30px;
    background-color: #FF9800;
    color: white;
    border: none;
    border-radius: 5px;
}

#timer_label {
    font-size: 20px;
    color: #F44336;
    qproperty-alignment: AlignCenter;
}
```

## 7. 配置管理

### 7.1 配置文件结构 (config.yaml)

```yaml
# API配置
api:
  base_url: "http://localhost:1234"
  model_name: "model-name"
  timeout: 30
  max_retries: 3

# 游戏配置
game:
  difficulty: "normal"  # easy, normal, hard
  time_limit: 60  # 秒，0表示无限制
  allow_homophone: false
  max_hints: 3

# 界面配置
ui:
  theme: "default"  # default, dark
  font_size: 16
  animation_enabled: true
  sound_enabled: true

# 数据库配置
database:
  path: "resources/idioms.db"
  backup_enabled: true

# 日志配置
logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR
  file: "logs/game.log"
  max_size: 10485760  # 10MB
```

### 7.2 配置管理器

```python
import yaml
from pathlib import Path
from typing import Any, Dict

class ConfigManager:
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        else:
            return self._create_default_config()

    def _create_default_config(self) -> Dict[str, Any]:
        """创建默认配置"""
        default = {
            'api': {
                'base_url': 'http://localhost:1234',
                'model_name': '',
                'timeout': 30,
                'max_retries': 3
            },
            'game': {
                'difficulty': 'normal',
                'time_limit': 60,
                'allow_homophone': False,
                'max_hints': 3
            },
            'ui': {
                'theme': 'default',
                'font_size': 16,
                'animation_enabled': True,
                'sound_enabled': True
            }
        }
        self.save_config(default)
        return default

    def get(self, key_path: str, default=None) -> Any:
        """获取配置值"""
        keys = key_path.split('.')
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    def set(self, key_path: str, value: Any) -> None:
        """设置配置值"""
        keys = key_path.split('.')
        config = self.config
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        config[keys[-1]] = value
        self.save_config()

    def save_config(self, config: Dict = None) -> None:
        """保存配置到文件"""
        if config is None:
            config = self.config
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(config, f, allow_unicode=True)
```

## 8. 错误处理

### 8.1 异常类设计

```python
class GameException(Exception):
    """游戏基础异常"""
    pass

class ValidationException(GameException):
    """成语验证异常"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)

class APIException(GameException):
    """API调用异常"""
    def __init__(self, message: str, retry_able: bool = False):
        self.message = message
        self.retry_able = retry_able
        super().__init__(message)

class DatabaseException(GameException):
    """数据库异常"""
    pass

class ConfigException(GameException):
    """配置异常"""
    pass
```

### 8.2 错误处理策略

```python
class ErrorHandler:
    @staticmethod
    def handle_error(error: Exception, parent_widget: QWidget = None) -> None:
        """处理错误并显示友好的错误提示"""
        if isinstance(error, ValidationException):
            ErrorHandler._show_warning(
                "验证错误",
                error.message,
                parent_widget
            )
        elif isinstance(error, APIException):
            ErrorHandler._show_critical(
                "API错误",
                f"无法连接到AI服务：{error.message}\n请检查API配置。",
                parent_widget
            )
        elif isinstance(error, DatabaseException):
            ErrorHandler._show_critical(
                "数据库错误",
                "数据库访问失败，请重新启动游戏。",
                parent_widget
            )
        else:
            ErrorHandler._show_critical(
                "未知错误",
                f"发生未知错误：{str(error)}",
                parent_widget
            )

        # 记录错误日志
        logging.error(f"Error occurred: {type(error).__name__}: {str(error)}")

    @staticmethod
    def _show_warning(title: str, message: str, parent: QWidget):
        from PyQt6.QtWidgets import QMessageBox
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec()

    @staticmethod
    def _show_critical(title: str, message: str, parent: QWidget):
        from PyQt6.QtWidgets import QMessageBox
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec()
```

## 9. 测试策略

### 9.1 单元测试

```python
import unittest
from src.core.idiom_validator import IdiomValidator
from src.data.database import IdiomDatabase

class TestIdiomValidator(unittest.TestCase):
    def setUp(self):
        self.db = IdiomDatabase(":memory:")
        self.validator = IdiomValidator(self.db)

    def test_valid_idiom(self):
        """测试有效成语"""
        # 添加测试数据
        self.db.add_idiom("车水马龙", "chē shuǐ mǎ lóng", "车", "龙")
        self.db.add_idiom("龙马精神", "lóng mǎ jīng shén", "龙", "神")

        result = self.validator.validate("龙马精神", "车水马龙", set())
        self.assertTrue(result.is_valid)

    def test_invalid_idiom(self):
        """测试无效成语"""
        result = self.validator.validate("测试测试", "", set())
        self.assertFalse(result.is_valid)

    def test_duplicate_idiom(self):
        """测试重复成语"""
        self.db.add_idiom("车水马龙", "chē shuǐ mǎ lóng", "车", "龙")
        used = {"车水马龙"}

        result = self.validator.validate("车水马龙", "", used)
        self.assertFalse(result.is_valid)
```

### 9.2 集成测试

```python
class TestGameIntegration(unittest.TestCase):
    def test_complete_game_flow(self):
        """测试完整游戏流程"""
        # 创建游戏管理器
        config = GameConfig()
        manager = GameManager(config)

        # 开始游戏
        manager.start_game("车水马龙")

        # 玩家回合
        result = manager.submit_player_idiom("龙马精神")
        self.assertTrue(result.success)

        # AI回合
        ai_idiom = manager.get_ai_response()
        self.assertIsNotNone(ai_idiom)
```

## 10. 部署和打包

### 10.1 依赖管理

**requirements.txt**:
```
PyQt6==6.6.1
PyYAML==6.0.1
requests==2.31.0
pypinyin==0.50.0
httpx==0.26.0
```

### 10.2 打包方案

使用PyInstaller打包：

```bash
# 安装PyInstaller
pip install pyinstaller

# 打包命令
pyinstaller --name "成语接龙" \
            --windowed \
            --icon=resources/icons/app_icon.ico \
            --add-data "resources:resources" \
            --add-data "src/gui/styles:src/gui/styles" \
            --hidden-import PyQt6 \
            --hidden-import pypinyin \
            main.py
```

**spec文件示例**:
```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('resources', 'resources'),
        ('src/gui/styles', 'src/gui/styles'),
        ('config.yaml', '.'),
    ],
    hiddenimports=[
        'PyQt6',
        'pypinyin',
        'yaml',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='成语接龙',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/icons/app_icon.ico',
)
```

## 11. 性能优化

### 11.1 数据库优化

1. **索引优化**: 为常用查询字段创建索引
2. **查询优化**: 使用预编译语句
3. **缓存机制**: 缓存常用成语数据

```python
class CachedIdiomDatabase(IdiomDatabase):
    def __init__(self, db_path: str, cache_size: int = 1000):
        super().__init__(db_path)
        self.cache = LRUCache(cache_size)

    def get_idiom_by_name(self, name: str) -> Optional[Idiom]:
        # 先查缓存
        if name in self.cache:
            return self.cache[name]

        # 查数据库
        idiom = super().get_idiom_by_name(name)
        if idiom:
            self.cache[name] = idiom
        return idiom
```

### 11.2 GUI优化

1. **懒加载**: 按需加载数据
2. **异步操作**: 耗时操作使用线程
3. **资源管理**: 及时释放资源

```python
class LazyGameScreen(GameScreen):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._idiom_database = None

    @property
    def idiom_database(self):
        if self._idiom_database is None:
            self._idiom_database = IdiomDatabase(
                config.get('database.path')
            )
        return self._idiom_database
```

## 12. 开发计划

### Phase 1: 基础架构 (Week 1)
- [x] 项目初始化
- [ ] 数据库设计和实现
- [ ] 基础UI框架搭建
- [ ] 配置管理系统

### Phase 2: 核心功能 (Week 2)
- [ ] 游戏逻辑实现
- [ ] 成语验证器
- [ ] LM Studio API集成
- [ ] 基本游戏界面

### Phase 3: 完善功能 (Week 3)
- [ ] 完整UI实现
- [ ] 设置面板
- [ ] 动画效果
- [ ] 音效系统

### Phase 4: 测试和优化 (Week 4)
- [ ] 单元测试
- [ ] 集成测试
- [ ] 性能优化
- [ ] Bug修复

### Phase 5: 打包发布 (Week 5)
- [ ] 打包配置
- [ ] 安装程序制作
- [ ] 用户文档
- [ ] 发布

## 13. 总结

本技术文档详细描述了成语接龙游戏的完整技术实现方案，包括：

1. **技术栈选型**: Python + PyQt6 + SQLite
2. **项目架构**: 分层架构，职责清晰
3. **核心模块**: 游戏管理、成语验证、AI集成
4. **数据设计**: 数据库Schema和API设计
5. **GUI实现**: PyQt6组件和样式
6. **配置管理**: YAML配置文件
7. **错误处理**: 完善的异常处理机制
8. **测试策略**: 单元测试和集成测试
9. **部署方案**: PyInstaller打包
10. **性能优化**: 缓存和异步处理

按照本文档进行开发，可以确保项目的可维护性、可扩展性和稳定性。
