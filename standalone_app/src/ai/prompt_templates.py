"""
提示词模板
用于生成AI请求的提示词
"""

from typing import Dict, Any, List, Set


class PromptTemplates:
    """提示词模板类"""

    # 系统提示词
    SYSTEM_PROMPT = """你是一个成语接龙专家。你的任务是根据给定的字，说出一个以该字开头的中文成语。

要求：
1. 只返回成语本身（4个字），不要任何解释或其他内容
2. 确保成语准确有效，是常见的中文成语
3. 避免使用过于生僻或不符合规范的成语
4. 不要使用已经使用过的成语

请严格按照要求回答，只输出成语的4个字。"""

    # 用户提示词模板
    USER_PROMPT_TEMPLATE = "请用'{char}'字开头接一个成语"

    # 带排除列表的提示词模板
    USER_PROMPT_WITH_EXCLUDE_TEMPLATE = """请用'{char}'字开头接一个成语。

已使用的成语（请避免使用）：
{used_list}"""

    # 温度参数映射
    TEMPERATURE_MAP = {
        "easy": 0.9,      # 高随机性，选择多样化
        "normal": 0.7,    # 中等随机性
        "hard": 0.3       # 低随机性，选择更精准
    }

    @staticmethod
    def generate_idiom_prompt(starting_char: str,
                             difficulty: str = "normal",
                             used_idioms: Set[str] = None) -> Dict[str, Any]:
        """
        生成成语接龙提示词

        Args:
            starting_char: 起始字
            difficulty: 难度等级 ('easy', 'normal', 'hard')
            used_idioms: 已使用的成语集合

        Returns:
            提示词字典
        """
        # 获取温度参数
        temperature = PromptTemplates.TEMPERATURE_MAP.get(
            difficulty, 0.7
        )

        # 构建用户提示词
        if used_idioms and len(used_idioms) > 0:
            # 如果有已使用的成语，加入提示词
            used_list = list(used_idioms)[-10:]  # 只显示最近10个
            user_prompt = PromptTemplates.USER_PROMPT_WITH_EXCLUDE_TEMPLATE.format(
                char=starting_char,
                used_list='、'.join(used_list)
            )
        else:
            user_prompt = PromptTemplates.USER_PROMPT_TEMPLATE.format(
                char=starting_char
            )

        return {
            "model": "",  # 将在客户端中设置
            "messages": [
                {
                    "role": "system",
                    "content": PromptTemplates.SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            "temperature": temperature,
            "max_tokens": 50
        }

    @staticmethod
    def generate_validation_prompt(idiom: str) -> Dict[str, Any]:
        """
        生成成语验证提示词

        Args:
            idiom: 要验证的成语

        Returns:
            提示词字典
        """
        system_prompt = """你是一个成语验证专家。请判断给定的词是否是一个有效的中文成语。

要求：
1. 只回答"是"或"否"
2. 不要任何解释或其他内容"""

        user_prompt = f"'{idiom}' 是一个有效的中文成语吗？"

        return {
            "model": "",
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            "temperature": 0.1,
            "max_tokens": 10
        }

    @staticmethod
    def generate_hint_prompt(starting_char: str,
                            used_idioms: Set[str] = None,
                            count: int = 3) -> Dict[str, Any]:
        """
        生成提示词提示

        Args:
            starting_char: 起始字
            used_idioms: 已使用的成语集合
            count: 提示数量

        Returns:
            提示词字典
        """
        system_prompt = f"""你是一个成语接龙专家。请提供{count}个以指定字开头的中文成语。

要求：
1. 每行一个成语
2. 只输出成语，不要编号或其他内容
3. 确保成语准确有效
4. 避免使用已使用的成语"""

        if used_idioms and len(used_idioms) > 0:
            used_list = list(used_idioms)[-20:]
            user_prompt = f"""请提供{count}个以'{starting_char}'字开头的成语。

已使用的成语：
{chr(10).join(used_list)}"""
        else:
            user_prompt = f"请提供{count}个以'{starting_char}'字开头的成语"

        return {
            "model": "",
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            "temperature": 0.8,
            "max_tokens": 100
        }

    @staticmethod
    def parse_idiom_response(response: str) -> str:
        """
        解析AI返回的成语

        Args:
            response: AI返回的文本

        Returns:
            提取的成语
        """
        # 去除空白
        response = response.strip()

        # 去除常见标点
        for char in '，。！？、""''《》（）【】':
            response = response.replace(char, '')

        # 提取前4个字
        if len(response) >= 4:
            return response[:4]

        return response

    @staticmethod
    def parse_hint_response(response: str, max_count: int = 3) -> List[str]:
        """
        解析AI返回的提示列表

        Args:
            response: AI返回的文本
            max_count: 最大返回数量

        Returns:
            成语列表
        """
        lines = response.strip().split('\n')
        hints = []

        for line in lines:
            # 去除编号和标点
            line = line.strip()
            for prefix in ['1.', '2.', '3.', '4.', '5.', '①', '②', '③', '④', '⑤']:
                if line.startswith(prefix):
                    line = line[1:].strip()
                    break

            # 去除标点
            for char in '，。！？、""''《》（）【】':
                line = line.replace(char, '')

            # 提取4字成语
            if len(line) >= 4:
                hint = line[:4]
                if hint not in hints:
                    hints.append(hint)
                    if len(hints) >= max_count:
                        break

        return hints
