"""
计分系统
根据游戏表现计算得分
"""

from typing import Optional
from src.data.models import GameResult


class ScoreCalculator:
    """计分器"""

    # 基础分数
    BASE_SCORE_PER_IDIOM = 10  # 每个成语的基础分数
    BONUS_PER_IDIOM = 5  # 每个成语的额外分数

    # 难度加成
    DIFFICULTY_MULTIPLIER = {
        "easy": 1.0,
        "normal": 1.5,
        "hard": 2.0
    }

    # 时间奖励
    TIME_BONUS_PER_SECOND = 0.1  # 每秒的时间奖励

    # 特殊奖励
    FIRST_BLOOD_BONUS = 50  # 首次获胜奖励
    PERFECT_GAME_BONUS = 100  # 完美游戏奖励（无提示、无超时）
    SPEED_BONUS = 30  # 快速获胜奖励（<30秒）

    @staticmethod
    def calculate_score(result: GameResult, difficulty: str = "normal",
                       hints_used: int = 0, time_remaining: int = 0) -> dict:
        """
        计算得分

        Args:
            result: 游戏结果
            difficulty: 难度级别
            hints_used: 使用的提示次数
            time_remaining: 剩余时间（秒）

        Returns:
            得分详情
        """
        if result.winner != "player":
            # 玩家失败
            return {
                "total_score": 0,
                "is_winner": False,
                "message": "很遗憾，你输了！"
            }

        # 基础分数
        base_score = result.player_idiom_count * ScoreCalculator.BASE_SCORE_PER_IDIOM

        # 成语额外分数
        idiom_bonus = result.player_idiom_count * ScoreCalculator.BONUS_PER_IDIOM

        # 难度加成
        difficulty_multiplier = ScoreCalculator.DIFFICULTY_MULTIPLIER.get(
            difficulty, 1.0
        )

        # 时间奖励
        time_bonus = time_remaining * ScoreCalculator.TIME_BONUS_PER_SECOND

        # 提示惩罚
        hint_penalty = hints_used * 15

        # 计算总分
        total_score = int((base_score + idiom_bonus + time_bonus) * difficulty_multiplier)
        total_score = max(0, total_score - hint_penalty)

        # 特殊奖励
        special_bonuses = []

        if hints_used == 0:
            total_score += 20
            special_bonuses.append("无提示奖励 +20")

        if result.duration < 30:
            total_score += ScoreCalculator.SPEED_BONUS
            special_bonuses.append(f"快速获胜奖励 +{ScoreCalculator.SPEED_BONUS}")

        if result.ai_idiom_count == 0:
            total_score += ScoreCalculator.PERFECT_GAME_BONUS
            special_bonuses.append(f"完美游戏奖励 +{ScoreCalculator.PERFECT_GAME_BONUS}")

        # 评级
        rating = ScoreCalculator._get_rating(total_score, result.player_idiom_count)

        return {
            "total_score": total_score,
            "is_winner": True,
            "base_score": base_score,
            "idiom_bonus": idiom_bonus,
            "time_bonus": int(time_bonus),
            "hint_penalty": hint_penalty,
            "difficulty_multiplier": difficulty_multiplier,
            "special_bonuses": special_bonuses,
            "rating": rating,
            "player_idioms": result.player_idiom_count,
            "ai_idioms": result.ai_idiom_count,
            "duration": result.duration,
            "message": ScoreCalculator._get_victory_message(rating, total_score)
        }

    @staticmethod
    def _get_rating(score: int, idiom_count: int) -> str:
        """根据分数和成语数量获取评级"""
        if score >= 200 or idiom_count >= 10:
            return "S"
        elif score >= 150 or idiom_count >= 7:
            return "A"
        elif score >= 100 or idiom_count >= 5:
            return "B"
        elif score >= 50 or idiom_count >= 3:
            return "C"
        else:
            return "D"

    @staticmethod
    def _get_victory_message(rating: str, score: int) -> str:
        """获取胜利消息"""
        messages = {
            "S": f"太厉害了！S级评价！得分：{score}",
            "A": f"很棒！A级评价！得分：{score}",
            "B": f"不错！B级评价！得分：{score}",
            "C": f"还可以，继续努力！C级评价，得分：{score}",
            "D": f"再接再厉！D级评价，得分：{score}"
        }
        return messages.get(rating, f"恭喜获胜！得分：{score}")
