"""
拼音处理工具
使用pypinyin库进行拼音转换
"""

from pypinyin import lazy_pinyin, Style


class PinyinUtils:
    """拼音工具类"""

    @staticmethod
    def get_pinyin(text: str, style: str = 'tone') -> str:
        """
        获取文本的拼音

        Args:
            text: 输入文本
            style: 拼音样式 ('normal', 'tone', 'tone2', 'initial', 'first_letter')

        Returns:
            拼音字符串
        """
        style_map = {
            'normal': Style.NORMAL,
            'tone': Style.TONE,
            'tone2': Style.TONE2,
            'initial': Style.INITIALS,
            'first_letter': Style.FIRST_LETTER
        }
        pys = lazy_pinyin(text, style=style_map.get(style, Style.TONE))
        return ''.join(pys)

    @staticmethod
    def get_first_char_pinyin(char: str) -> str:
        """
        获取首字拼音

        Args:
            char: 单个汉字

        Returns:
            拼音字符串（带声调）
        """
        if not char:
            return ""
        pys = lazy_pinyin(char, style=Style.TONE)
        return pys[0] if pys else ""

    @staticmethod
    def get_first_char_pinyin_without_tone(char: str) -> str:
        """
        获取首字拼音（不带声调）

        Args:
            char: 单个汉字

        Returns:
            拼音字符串（不带声调）
        """
        if not char:
            return ""
        pys = lazy_pinyin(char, style=Style.NORMAL)
        return pys[0] if pys else ""

    @staticmethod
    def compare_homophone(char1: str, char2: str) -> bool:
        """
        比较两个字的发音是否相同（不考虑声调）

        Args:
            char1: 第一个字
            char2: 第二个字

        Returns:
            是否同音
        """
        p1 = PinyinUtils.get_first_char_pinyin_without_tone(char1)
        p2 = PinyinUtils.get_first_char_pinyin_without_tone(char2)
        return p1 == p2 if p1 and p2 else False

    @staticmethod
    def get_pinyin_list(text: str) -> list:
        """
        获取文本的拼音列表

        Args:
            text: 输入文本

        Returns:
            拼音列表
        """
        return lazy_pinyin(text, style=Style.TONE)

    @staticmethod
    def get_initials(text: str) -> str:
        """
        获取文本的声母

        Args:
            text: 输入文本

        Returns:
            声母字符串
        """
        pys = lazy_pinyin(text, style=Style.INITIALS)
        return ''.join([p for p in pys if p])
