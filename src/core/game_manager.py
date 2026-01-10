"""
游戏管理器
负责游戏流程控制和状态管理
"""

import time
import logging
from typing import Optional, Callable
from src.data.models import GameState, GameConfig, GameResult, ValidationResult
from src.data.database import IdiomDatabase
from src.data.idiom_repository import IdiomRepository
from src.core.idiom_validator import IdiomValidator
from src.core.llm_idiom_validator import LLMIdiomValidator
from src.ai.lmstudio_client import LMStudioClient
from src.ai.prompt_templates import PromptTemplates
from src.utils.exceptions import ValidationException, APIException


logger = logging.getLogger(__name__)


class GameManager:
    """游戏管理器类"""

    def __init__(self, config: GameConfig, database: IdiomDatabase,
                 ai_client: LMStudioClient, use_llm_validator: bool = True):
        """
        初始化游戏管理器

        Args:
            config: 游戏配置
            database: 成语数据库
            ai_client: AI客户端
            use_llm_validator: 是否使用LLM验证器
        """
        self.config = config
        self.repository = IdiomRepository(database)
        self.ai_client = ai_client
        self.use_llm_validator = use_llm_validator

        # 选择验证器
        if use_llm_validator:
            self.validator = LLMIdiomValidator(ai_client)
            logger.info("使用LLM验证器")
        else:
            self.validator = IdiomValidator(self.repository)
            logger.info("使用数据库验证器")

        self.game_state = GameState()
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None

        # 回调函数
        self.on_state_change: Optional[Callable] = None
        self.on_ai_thinking: Optional[Callable] = None
        self.on_ai_response: Optional[Callable[[str], None]] = None

    def start_game(self, starting_idiom: Optional[str] = None) -> None:
        """
        开始新游戏

        Args:
            starting_idiom: 起始成语，None表示随机选择
        """
        logger.info("开始新游戏")
        self.game_state.reset()
        self.start_time = time.time()
        self.end_time = None

        # 选择起始成语
        if starting_idiom:
            if not self.repository.exists(starting_idiom):
                logger.warning(f"指定的起始成语不存在: {starting_idiom}")
                starting_idiom = None
        else:
            random_idiom = self.repository.find_random()
            starting_idiom = random_idiom.word if random_idiom else None

        if starting_idiom:
            self.game_state.add_idiom(starting_idiom)
            self.game_state.game_started = True
            logger.info(f"起始成语: {starting_idiom}")

        if self.on_state_change:
            self.on_state_change()

    def submit_player_idiom(self, idiom: str) -> ValidationResult:
        """
        玩家提交成语

        Args:
            idiom: 玩家输入的成语

        Returns:
            验证结果
        """
        if not self.game_state.game_started or self.game_state.game_over:
            return ValidationResult(False, "游戏未开始或已结束")

        if not self.game_state.is_player_turn:
            return ValidationResult(False, "现在不是你的回合")

        # 验证成语
        result = self.validator.validate(
            idiom,
            self.game_state.last_idiom,
            self.game_state.used_idioms,
            self.config.allow_homophone
        )

        if not result.is_valid:
            logger.warning(f"玩家提交失败: {result.message}")
            return result

        # 添加到已使用列表
        self.game_state.add_idiom(idiom)
        logger.info(f"玩家提交成语: {idiom}")

        # 切换到AI回合
        self.game_state.switch_turn()

        if self.on_state_change:
            self.on_state_change()

        return ValidationResult(True, "")

    def get_ai_response(self) -> str:
        """
        获取AI响应

        Returns:
            AI返回的成语

        Raises:
            APIException: AI调用失败
        """
        if not self.game_state.game_started or self.game_state.game_over:
            raise APIException("游戏未开始或已结束")

        if self.game_state.is_player_turn:
            raise APIException("现在不是AI的回合")

        if not self.game_state.last_idiom:
            raise APIException("没有前一个成语")

        # 获取起始字
        starting_char = self.game_state.last_idiom[-1]

        logger.info(f"AI思考中... 起始字: {starting_char}")

        if self.on_ai_thinking:
            self.on_ai_thinking()

        # 生成提示词
        prompt = PromptTemplates.generate_idiom_prompt(
            starting_char,
            self.config.difficulty,
            self.game_state.used_idioms
        )

        try:
            # 调用AI
            ai_idiom = self.ai_client.generate_idiom(prompt)
            logger.info(f"AI返回: {ai_idiom}")

            # 验证AI返回的成语
            result = self.validator.validate(
                ai_idiom,
                self.game_state.last_idiom,
                self.game_state.used_idioms,
                self.config.allow_homophone
            )

            if not result.is_valid:
                logger.warning(f"AI返回的成语无效: {result.message}")
                # 如果是"无法接龙"，AI失败
                if ai_idiom == "无法接龙" or not ai_idiom or len(ai_idiom) < 4:
                    self.end_game('player', 'AI无法接龙')
                    return ""
                # 否则尝试重新生成或使用数据库中的成语
                ai_idiom = self._fallback_idiom(starting_char)
                if not ai_idiom:
                    self.end_game('player', 'AI无法接龙')
                    return ""

            # 添加到已使用列表
            self.game_state.add_idiom(ai_idiom)

            # 切换到玩家回合
            self.game_state.switch_turn()

            if self.on_state_change:
                self.on_state_change()

            if self.on_ai_response:
                self.on_ai_response(ai_idiom)

            return ai_idiom

        except Exception as e:
            logger.error(f"AI调用失败: {str(e)}")
            # AI失败，玩家获胜
            self.end_game('player', 'AI连接失败')
            return ""

    def _fallback_idiom(self, starting_char: str) -> Optional[str]:
        """
        备选成语（当AI失败时使用）

        Args:
            starting_char: 起始字

        Returns:
            备选成语或None
        """
        idioms = self.repository.get_possible_following_idioms(
            starting_char,
            self.game_state.used_idioms
        )

        if not idioms:
            return None

        # 根据难度选择成语
        if self.config.difficulty == 'easy':
            # 简单：选择最常用的
            return idioms[0].word if idioms else None
        elif self.config.difficulty == 'normal':
            # 普通：随机选择
            import random
            return random.choice(idioms).word if idioms else None
        else:
            # 困难：选择较少用的
            return idioms[-1].word if idioms else None

    def use_hint(self) -> Optional[str]:
        """
        使用提示

        Returns:
            提示的成语或None（没有提示次数）
        """
        if not self.game_state.game_started or self.game_state.game_over:
            return None

        if not self.game_state.is_player_turn:
            return None

        if self.game_state.player_hints_remaining <= 0:
            return None

        if not self.game_state.last_idiom:
            return None

        starting_char = self.game_state.last_idiom[-1]
        hints = self.repository.get_hints(
            starting_char,
            count=1,
            exclude=self.game_state.used_idioms
        )

        if hints:
            self.game_state.player_hints_remaining -= 1
            logger.info(f"玩家使用提示: {hints[0]}")
            return hints[0]

        return None

    def check_game_over(self) -> Optional[str]:
        """
        检查游戏是否结束

        Returns:
            胜者 ('player' or 'ai')，游戏未结束返回None
        """
        if not self.game_state.last_idiom:
            return None

        # 使用LLM验证器时，不主动检查游戏结束
        # 让游戏自然进行，直到AI或玩家主动认输/超时
        if self.use_llm_validator:
            return None

        # 检查玩家是否无法接龙
        if self.game_state.is_player_turn:
            if not self.repository.has_possible_following(
                self.game_state.last_idiom[-1],
                self.game_state.used_idioms
            ):
                return 'ai'

        # 检查AI是否无法接龙
        else:
            if not self.repository.has_possible_following(
                self.game_state.last_idiom[-1],
                self.game_state.used_idioms
            ):
                return 'player'

        return None

    def end_game(self, winner: str, reason: str) -> GameResult:
        """
        结束游戏

        Args:
            winner: 胜者 ('player' or 'ai')
            reason: 结束原因

        Returns:
            游戏结果
        """
        logger.info(f"游戏结束，胜者: {winner}，原因: {reason}")

        self.game_state.game_over = True
        self.end_time = time.time()

        duration = int(self.end_time - self.start_time) if self.start_time else 0

        # 计算双方使用的成语数
        player_count = sum(1 for i, idiom in enumerate(self.game_state.used_idioms)
                          if i % 2 == 0)  # 假设玩家先手
        ai_count = len(self.game_state.used_idioms) - player_count

        result = GameResult(
            winner=winner,
            total_rounds=self.game_state.current_round,
            player_idiom_count=player_count,
            ai_idiom_count=ai_count,
            end_reason=reason,
            duration=duration
        )

        if self.on_state_change:
            self.on_state_change()

        return result

    def forfeit(self) -> GameResult:
        """
        玩家认输

        Returns:
            游戏结果
        """
        return self.end_game('ai', '玩家认输')

    def get_game_state(self) -> GameState:
        """
        获取当前游戏状态

        Returns:
            游戏状态
        """
        return self.game_state

    def get_history(self) -> list:
        """
        获取游戏历史

        Returns:
            成语列表
        """
        return list(self.game_state.used_idioms)

    def reset(self) -> None:
        """重置游戏"""
        self.game_state.reset()
        self.start_time = None
        self.end_time = None
        logger.info("游戏已重置")

        if self.on_state_change:
            self.on_state_change()
