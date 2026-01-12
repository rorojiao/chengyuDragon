"""
音效管理器
负责游戏中的音效播放
"""

import logging
import os
from pathlib import Path
from typing import Optional
from PyQt6.QtCore import QObject, QUrl
from PyQt6.QtMultimedia import QSoundEffect

logger = logging.getLogger(__name__)


class SoundManager(QObject):
    """音效管理器"""

    # 音效类型
    BUTTON_CLICK = "button_click"
    SUBMIT = "submit"
    HINT = "hint"
    CARD_APPEAR = "card_appear"
    AI_THINKING = "ai_thinking"
    VICTORY = "victory"
    DEFEAT = "defeat"
    ERROR = "error"
    TIMEOUT = "timeout"

    def __init__(self, sound_enabled: bool = True, parent=None):
        """
        初始化音效管理器

        Args:
            sound_enabled: 是否启用音效
            parent: 父对象
        """
        super().__init__(parent)
        self.sound_enabled = sound_enabled
        self.effects: dict[str, QSoundEffect] = {}
        self.sound_files = {
            self.BUTTON_CLICK: "sounds/button_click.wav",
            self.SUBMIT: "sounds/submit.wav",
            self.HINT: "sounds/hint.wav",
            self.CARD_APPEAR: "sounds/card_appear.wav",
            self.AI_THINKING: "sounds/ai_thinking.wav",
            self.VICTORY: "sounds/victory.wav",
            self.DEFEAT: "sounds/defeat.wav",
            self.ERROR: "sounds/error.wav",
            self.TIMEOUT: "sounds/timeout.wav",
        }

    def set_sound_enabled(self, enabled: bool):
        """设置音效开关"""
        self.sound_enabled = enabled
        logger.info(f"音效已{'启用' if enabled else '禁用'}")

    def load_sounds(self, base_path: Optional[str] = None):
        """
        加载音效文件

        Args:
            base_path: 音效文件基础路径
        """
        if base_path:
            sound_dir = Path(base_path) / "sounds"
        else:
            # 默认使用项目根目录下的sounds文件夹
            sound_dir = Path(__file__).parent.parent.parent / "resources" / "sounds"

        self.sound_base_path = sound_dir

        # 预加载音效
        for sound_name, sound_file in self.sound_files.items():
            sound_path = sound_dir / sound_file
            if sound_path.exists():
                try:
                    effect = QSoundEffect(self)
                    effect.setSource(QUrl.fromLocalFile(str(sound_path)))
                    effect.setVolume(0.7)
                    self.effects[sound_name] = effect
                    logger.debug(f"加载音效: {sound_name}")
                except Exception as e:
                    logger.warning(f"无法加载音效 {sound_name}: {e}")
            else:
                logger.debug(f"音效文件不存在: {sound_path}")

        logger.info(f"音效加载完成，共加载 {len(self.effects)} 个音效")

    def play(self, sound_name: str):
        """
        播放音效

        Args:
            sound_name: 音效名称
        """
        if not self.sound_enabled:
            return

        if sound_name in self.effects:
            effect = self.effects[sound_name]
            if effect.isLoaded():
                effect.play()
            else:
                logger.debug(f"音效未加载: {sound_name}")
        else:
            logger.debug(f"音效不存在: {sound_name}")

    def play_button_click(self):
        """播放按钮点击音效"""
        self.play(self.BUTTON_CLICK)

    def play_submit(self):
        """播放提交音效"""
        self.play(self.SUBMIT)

    def play_hint(self):
        """播放提示音效"""
        self.play(self.HINT)

    def play_card_appear(self):
        """播放卡片出现音效"""
        self.play(self.CARD_APPEAR)

    def play_ai_thinking(self):
        """播放AI思考音效"""
        self.play(self.AI_THINKING)

    def play_victory(self):
        """播放胜利音效"""
        self.play(self.VICTORY)

    def play_defeat(self):
        """播放失败音效"""
        self.play(self.DEFEAT)

    def play_error(self):
        """播放错误音效"""
        self.play(self.ERROR)

    def play_timeout(self):
        """播放超时音效"""
        self.play(self.TIMEOUT)

    def set_volume(self, volume: float):
        """
        设置音量

        Args:
            volume: 音量 (0.0 - 1.0)
        """
        volume = max(0.0, min(1.0, volume))
        for effect in self.effects.values():
            effect.setVolume(volume)
        logger.info(f"音量设置为: {volume}")

    def cleanup(self):
        """清理音效资源"""
        for effect in self.effects.values():
            effect.stop()
        self.effects.clear()
