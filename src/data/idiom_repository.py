"""
成语数据仓库
提供高级数据访问接口
"""

from typing import List, Optional
from src.data.database import IdiomDatabase
from src.data.models import Idiom


class IdiomRepository:
    """成语数据仓库类"""

    def __init__(self, database: IdiomDatabase):
        """
        初始化仓库

        Args:
            database: 数据库实例
        """
        self.database = database

    def find_by_word(self, word: str) -> Optional[Idiom]:
        """
        根据词语查找成语

        Args:
            word: 成语词语

        Returns:
            成语对象或None
        """
        return self.database.get_idiom_by_name(word)

    def find_by_starting_char(self, char: str) -> List[Idiom]:
        """
        根据首字查找成语

        Args:
            char: 首字

        Returns:
            成语列表
        """
        return self.database.get_idioms_by_starting_char(char)

    def find_random(self, difficulty: int = None) -> Optional[Idiom]:
        """
        查找随机成语

        Args:
            difficulty: 难度等级

        Returns:
            随机成语或None
        """
        return self.database.get_random_idiom(difficulty)

    def search(self, keyword: str, limit: int = 10) -> List[Idiom]:
        """
        搜索成语

        Args:
            keyword: 关键词
            limit: 数量限制

        Returns:
            成语列表
        """
        return self.database.search_idioms(keyword, limit)

    def exists(self, word: str) -> bool:
        """
        检查成语是否存在

        Args:
            word: 成语词语

        Returns:
            是否存在
        """
        return self.database.is_valid_idiom(word)

    def get_count(self) -> int:
        """
        获取成语总数

        Returns:
            成语总数
        """
        return self.database.get_total_count()

    def get_possible_following_idioms(self, last_char: str,
                                       exclude: set = None) -> List[Idiom]:
        """
        获取可能的接龙成语

        Args:
            last_char: 上一个成语的尾字
            exclude: 要排除的成语集合

        Returns:
            可用的成语列表
        """
        idioms = self.find_by_starting_char(last_char)
        if exclude:
            idioms = [idiom for idiom in idioms if idiom.word not in exclude]
        return idioms

    def has_possible_following(self, last_char: str, exclude: set = None) -> bool:
        """
        检查是否有可接龙的成语

        Args:
            last_char: 上一个成语的尾字
            exclude: 要排除的成语集合

        Returns:
            是否有可接龙的成语
        """
        return len(self.get_possible_following_idioms(last_char, exclude)) > 0

    def get_hints(self, starting_char: str, count: int = 3,
                  exclude: set = None) -> List[str]:
        """
        获取提示成语

        Args:
            starting_char: 起始字
            count: 提示数量
            exclude: 要排除的成语集合

        Returns:
            提示成语列表
        """
        idioms = self.find_by_starting_char(starting_char)
        if exclude:
            idioms = [idiom for idiom in idioms if idiom.word not in exclude]
        return [idiom.word for idiom in idioms[:count]]
