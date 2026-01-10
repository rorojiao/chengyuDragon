"""
成语验证器
负责验证成语的合法性
"""

from typing import Optional, Set
from src.data.models import ValidationResult, Idiom
from src.data.idiom_repository import IdiomRepository
from src.utils.pinyin import PinyinUtils
from src.utils.exceptions import ValidationException


class IdiomValidator:
    """成语验证器类"""

    def __init__(self, repository: IdiomRepository):
        """
        初始化验证器

        Args:
            repository: 成语数据仓库
        """
        self.repository = repository
        self._last_error: str = ""

    def validate(self, idiom: str, prev_idiom: Optional[str] = None,
                 used_idioms: Set[str] = None,
                 allow_homophone: bool = False) -> ValidationResult:
        """
        验证成语

        Args:
            idiom: 要验证的成语
            prev_idiom: 前一个成语
            used_idioms: 已使用的成语集合
            allow_homophone: 是否允许同音字

        Returns:
            验证结果
        """
        # 1. 检查是否为空
        if not idiom or not idiom.strip():
            self._last_error = "成语不能为空"
            return ValidationResult(False, self._last_error)

        idiom = idiom.strip()

        # 2. 检查长度（通常成语为4字）
        if len(idiom) != 4:
            self._last_error = "成语必须是4个字"
            return ValidationResult(False, self._last_error)

        # 3. 检查是否存在于数据库
        if not self.repository.exists(idiom):
            self._last_error = f"'{idiom}' 不是一个有效的成语"
            return ValidationResult(False, self._last_error)

        # 4. 检查是否重复
        if used_idioms and idiom in used_idioms:
            self._last_error = f"'{idiom}' 已经使用过了"
            return ValidationResult(False, self._last_error)

        # 5. 检查接龙规则
        if prev_idiom:
            if allow_homophone:
                # 允许同音字
                if not self._check_homophone_match(prev_idiom, idiom):
                    self._last_error = (f"必须用 '{prev_idiom[-1]}' 的同音字开头，"
                                       f"而不是 '{idiom[0]}'")
                    return ValidationResult(False, self._last_error)
            else:
                # 必须同字
                if idiom[0] != prev_idiom[-1]:
                    self._last_error = (f"必须用 '{prev_idiom[-1]}' 字开头，"
                                       f"而不是 '{idiom[0]}'")
                    return ValidationResult(False, self._last_error)

        return ValidationResult(True, "")

    def _check_homophone_match(self, prev_idiom: str, curr_idiom: str) -> bool:
        """
        检查两个成语是否同音匹配

        Args:
            prev_idiom: 前一个成语
            curr_idiom: 当前成语

        Returns:
            是否同音匹配
        """
        prev_last_char = prev_idiom[-1]
        curr_first_char = curr_idiom[0]

        # 如果字相同，直接返回True
        if prev_last_char == curr_first_char:
            return True

        # 检查是否同音
        return PinyinUtils.compare_homophone(prev_last_char, curr_first_char)

    def get_last_error(self) -> str:
        """
        获取最后一次验证错误信息

        Returns:
            错误信息
        """
        return self._last_error

    def validate_and_get_idiom(self, idiom: str) -> Optional[Idiom]:
        """
        验证并获取成语对象

        Args:
            idiom: 成语字符串

        Returns:
            成语对象，验证失败返回None
        """
        # 简单验证
        if not idiom or len(idiom) != 4:
            return None

        # 从数据库获取
        return self.repository.find_by_word(idiom)

    def can_chain(self, from_idiom: str, to_idiom: str,
                  allow_homophone: bool = False) -> bool:
        """
        检查两个成语是否可以接龙

        Args:
            from_idiom: 源成语
            to_idiom: 目标成语
            allow_homophone: 是否允许同音字

        Returns:
            是否可以接龙
        """
        if not from_idiom or not to_idiom:
            return False

        if allow_homophone:
            return self._check_homophone_match(from_idiom, to_idiom)
        else:
            return from_idiom[-1] == to_idiom[0]

    def is_dead_end(self, idiom: str, used_idioms: Set[str] = None) -> bool:
        """
        检查成语是否是死胡同（没有可接龙的成语）

        Args:
            idiom: 成语
            used_idioms: 已使用的成语集合

        Returns:
            是否是死胡同
        """
        if not idiom:
            return True

        last_char = idiom[-1]
        if used_idioms is None:
            used_idioms = set()

        return not self.repository.has_possible_following(last_char, used_idioms)
