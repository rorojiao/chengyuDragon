"""
数据模型定义
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Idiom:
    """成语数据模型"""

    word: str  # 成语
    pinyin: str  # 拼音
    first_char: str  # 首字
    last_char: str  # 尾字
    first_pinyin: str  # 首字拼音
    last_pinyin: str  # 尾字拼音
    explanation: Optional[str] = None  # 解释
    example: Optional[str] = None  # 例句
    difficulty: int = 1  # 难度 1-5
    frequency: float = 0.0  # 使用频率

    def __repr__(self) -> str:
        return f"Idiom(word='{self.word}', pinyin='{self.pinyin}')"


@dataclass
class ValidationResult:
    """验证结果数据模型"""

    is_valid: bool  # 是否有效
    message: str  # 错误或提示信息

    def __repr__(self) -> str:
        return f"ValidationResult(is_valid={self.is_valid}, message='{self.message}')"


@dataclass
class GameConfig:
    """游戏配置数据模型"""

    difficulty: str = "normal"  # easy, normal, hard
    time_limit: int = 60  # 秒
    allow_homophone: bool = False  # 是否允许同音字
    max_hints: int = 3  # 最大提示次数

    def __repr__(self) -> str:
        return (f"GameConfig(difficulty='{self.difficulty}', "
                f"time_limit={self.time_limit}, "
                f"allow_homophone={self.allow_homophone}, "
                f"max_hints={self.max_hints})")


@dataclass
class GameResult:
    """游戏结果数据模型"""

    winner: str  # 胜者 ('player' or 'ai')
    total_rounds: int  # 总回合数
    player_idiom_count: int  # 玩家使用的成语数
    ai_idiom_count: int  # AI使用的成语数
    end_reason: str  # 结束原因
    duration: int  # 游戏时长（秒）

    def __repr__(self) -> str:
        return (f"GameResult(winner='{self.winner}', "
                f"total_rounds={self.total_rounds}, "
                f"end_reason='{self.end_reason}')")


@dataclass
class GameState:
    """游戏状态数据模型"""

    current_round: int  # 当前回合数
    last_idiom: Optional[str]  # 上一个成语
    used_idioms: set  # 已使用的成语集合
    player_hints_remaining: int  # 玩家剩余提示次数
    is_player_turn: bool  # 是否玩家回合
    game_started: bool  # 游戏是否已开始
    game_over: bool  # 游戏是否结束

    def __init__(self):
        self.current_round = 0
        self.last_idiom = None
        self.used_idioms = set()
        self.player_hints_remaining = 3
        self.is_player_turn = True
        self.game_started = False
        self.game_over = False

    def add_idiom(self, idiom: str) -> None:
        """添加已使用的成语"""
        self.used_idioms.add(idiom)
        self.last_idiom = idiom

    def switch_turn(self) -> None:
        """切换回合"""
        self.is_player_turn = not self.is_player_turn
        if self.is_player_turn:
            self.current_round += 1

    def reset(self) -> None:
        """重置游戏状态"""
        self.current_round = 0
        self.last_idiom = None
        self.used_idioms.clear()
        self.player_hints_remaining = 3
        self.is_player_turn = True
        self.game_started = False
        self.game_over = False
