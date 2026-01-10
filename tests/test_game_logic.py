"""
游戏逻辑单元测试
"""

import unittest
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.models import GameConfig, GameState
from src.data.database import IdiomDatabase
from src.core.idiom_validator import IdiomValidator
from src.data.idiom_repository import IdiomRepository


class TestGameState(unittest.TestCase):
    """游戏状态测试"""

    def test_initial_state(self):
        """测试初始状态"""
        state = GameState()
        self.assertEqual(state.current_round, 0)
        self.assertIsNone(state.last_idiom)
        self.assertEqual(len(state.used_idioms), 0)
        self.assertTrue(state.is_player_turn)
        self.assertFalse(state.game_started)
        self.assertFalse(state.game_over)

    def test_add_idiom(self):
        """测试添加成语"""
        state = GameState()
        state.add_idiom("车水马龙")
        self.assertEqual(state.last_idiom, "车水马龙")
        self.assertIn("车水马龙", state.used_idioms)

    def test_switch_turn(self):
        """测试切换回合"""
        state = GameState()
        self.assertTrue(state.is_player_turn)
        state.switch_turn()
        self.assertFalse(state.is_player_turn)
        state.switch_turn()
        self.assertTrue(state.is_player_turn)

    def test_reset(self):
        """测试重置状态"""
        state = GameState()
        state.add_idiom("车水马龙")
        state.current_round = 5
        state.game_started = True
        state.reset()
        self.assertEqual(state.current_round, 0)
        self.assertIsNone(state.last_idiom)
        self.assertEqual(len(state.used_idioms), 0)


class TestIdiomValidator(unittest.TestCase):
    """成语验证器测试"""

    def setUp(self):
        """设置测试环境"""
        self.db = IdiomDatabase(":memory:")

        # 添加测试数据
        from src.data.models import Idiom
        test_idioms = [
            Idiom("车水马龙", "chē shuǐ mǎ lóng", "车", "龙",
                  "chē", "lóng", "形容车马往来繁华热闹的景象"),
            Idiom("龙马精神", "lóng mǎ jīng shén", "龙", "神",
                  "lóng", "shén", "比喻人精神旺盛"),
            Idiom("神采飞扬", "shén cǎi fēi yáng", "神", "扬",
                  "shén", "yáng", "形容精神饱满，神情昂扬"),
        ]
        for idiom in test_idioms:
            self.db.add_idiom(idiom)

        self.repository = IdiomRepository(self.db)
        self.validator = IdiomValidator(self.repository)

    def test_valid_idiom(self):
        """测试有效成语"""
        result = self.validator.validate("龙马精神", "车水马龙", set())
        self.assertTrue(result.is_valid)

    def test_invalid_idiom_not_exist(self):
        """测试不存在的成语"""
        result = self.validator.validate("测试测试", "", set())
        self.assertFalse(result.is_valid)

    def test_duplicate_idiom(self):
        """测试重复成语"""
        result = self.validator.validate(
            "车水马龙",
            "",
            {"车水马龙"}
        )
        self.assertFalse(result.is_valid)

    def test_chain_rule_exact_match(self):
        """测试精确匹配接龙规则"""
        result = self.validator.validate("龙马精神", "车水马龙", set())
        self.assertTrue(result.is_valid)

    def test_chain_rule_no_match(self):
        """测试不匹配接龙规则"""
        result = self.validator.validate("神采飞扬", "车水马龙", set())
        self.assertFalse(result.is_valid)


class TestIdiomRepository(unittest.TestCase):
    """成语仓库测试"""

    def setUp(self):
        """设置测试环境"""
        self.db = IdiomDatabase(":memory:")

        # 添加测试数据
        from src.data.models import Idiom
        test_idioms = [
            Idiom("车水马龙", "chē shuǐ mǎ lóng", "车", "龙",
                  "chē", "lóng", "形容车马往来繁华热闹的景象"),
            Idiom("龙马精神", "lóng mǎ jīng shén", "龙", "神",
                  "lóng", "shén", "比喻人精神旺盛"),
            Idiom("龙飞凤舞", "lóng fēi fèng wǔ", "龙", "舞",
                  "lóng", "wǔ", "形容山势蜿蜒雄壮，也形容书法笔势有力"),
        ]
        for idiom in test_idioms:
            self.db.add_idiom(idiom)

        self.repository = IdiomRepository(self.db)

    def test_find_by_word(self):
        """测试按词语查找"""
        idiom = self.repository.find_by_word("车水马龙")
        self.assertIsNotNone(idiom)
        self.assertEqual(idiom.word, "车水马龙")

    def test_find_by_starting_char(self):
        """测试按首字查找"""
        idioms = self.repository.find_by_starting_char("龙")
        self.assertEqual(len(idioms), 2)

    def test_exists(self):
        """测试成语是否存在"""
        self.assertTrue(self.repository.exists("车水马龙"))
        self.assertFalse(self.repository.exists("不存在"))

    def test_get_possible_following_idioms(self):
        """测试获取可接龙的成语"""
        idioms = self.repository.get_possible_following_idioms("龙")
        self.assertEqual(len(idioms), 2)

        idioms = self.repository.get_possible_following_idioms(
            "龙",
            exclude={"龙马精神"}
        )
        self.assertEqual(len(idioms), 1)


if __name__ == '__main__':
    unittest.main()
