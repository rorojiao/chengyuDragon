"""
成语验证器 - 使用LLM判断
完全依赖LLM来判断成语的有效性和接龙规则
"""

import logging
from typing import Optional, Set
from src.data.models import ValidationResult
from src.ai.lmstudio_client import LMStudioClient
from src.ai.prompt_templates import PromptTemplates


logger = logging.getLogger(__name__)


class LLMIdiomValidator:
    """基于LLM的成语验证器"""

    def __init__(self, ai_client: LMStudioClient):
        """
        初始化验证器

        Args:
            ai_client: LM Studio AI客户端
        """
        self.ai_client = ai_client
        self._last_error: str = ""
        self._cache = {}  # 缓存已验证的成语

    def validate(self, idiom: str, prev_idiom: Optional[str] = None,
                 used_idioms: Set[str] = None,
                 allow_homophone: bool = False) -> ValidationResult:
        """
        使用LLM验证成语

        Args:
            idiom: 要验证的成语
            prev_idiom: 前一个成语
            used_idioms: 已使用的成语集合
            allow_homophone: 是否允许同音字

        Returns:
            验证结果
        """
        # 1. 基本检查
        if not idiom or not idiom.strip():
            self._last_error = "成语不能为空"
            return ValidationResult(False, self._last_error)

        idiom = idiom.strip()

        # 2. 长度检查
        if len(idiom) != 4:
            self._last_error = "成语必须是4个字"
            return ValidationResult(False, self._last_error)

        # 3. 检查重复
        if used_idioms and idiom in used_idioms:
            self._last_error = f"'{idiom}' 已经使用过了"
            return ValidationResult(False, self._last_error)

        # 4. 使用LLM验证
        return self._validate_with_llm(idiom, prev_idiom, allow_homophone)

    def _validate_with_llm(self, idiom: str, prev_idiom: Optional[str],
                           allow_homophone: bool) -> ValidationResult:
        """使用LLM进行验证"""
        try:
            # 构建验证提示词
            if prev_idiom:
                prompt_data = self._build_validation_prompt_with_prev(
                    idiom, prev_idiom, allow_homophone
                )
            else:
                prompt_data = self._build_validation_prompt_simple(idiom)

            # 直接调用API，绕过generate_idiom方法
            request_data = {
                "model": self.ai_client.model_name or prompt_data.get("model", "default"),
                "messages": prompt_data.get("messages", []),
                "temperature": prompt_data.get("temperature", 0.1),
                "max_tokens": prompt_data.get("max_tokens", 10)
            }

            logger.debug(f"发送验证请求: {idiom}")

            response = self.ai_client.session.post(
                f"{self.ai_client.base_url}/v1/chat/completions",
                json=request_data,
                timeout=self.ai_client.timeout
            )
            response.raise_for_status()

            data = response.json()
            if 'choices' in data and len(data['choices']) > 0:
                content = data['choices'][0]['message']['content']
                # 解析响应
                return self._parse_llm_response(content, idiom)
            else:
                self._last_error = "AI返回格式错误"
                return ValidationResult(False, self._last_error)

        except Exception as e:
            logger.error(f"LLM验证失败: {str(e)}")
            # LLM失败时，使用宽松的验证
            self._last_error = f"AI验证失败: {str(e)}"
            return ValidationResult(False, self._last_error)

    def _build_validation_prompt_simple(self, idiom: str) -> dict:
        """构建简单的验证提示词"""
        return {
            "model": self.ai_client.model_name or "default",
            "messages": [
                {
                    "role": "system",
                    "content": """你是一个成语专家。请判断用户输入的成语是否有效。

验证标准：
1. 必须是一个有效的中文成语（四字词语）
2. 只回答"是"或"否"
3. 不要任何解释"""
                },
                {
                    "role": "user",
                    "content": f'"{idiom}" 是一个有效的中文成语吗？请只回答"是"或"否"。'
                }
            ],
            "temperature": 0.1,
            "max_tokens": 10
        }

    def _build_validation_prompt_with_prev(self, idiom: str, prev_idiom: str,
                                          allow_homophone: bool) -> dict:
        """构建带接龙规则的验证提示词"""
        homophone_hint = "或同音字" if allow_homophone else ""
        return {
            "model": self.ai_client.model_name or "default",
            "messages": [
                {
                    "role": "system",
                    "content": f"""你是一个成语接龙专家。请验证用户的成语是否有效。

验证标准：
1. 用户输入的成语必须是一个有效的中文成语
2. 用户成语的第一个字必须与前一个成语的最后一个字相同{homophone_hint}
3. 只回答"是"或"否"
4. 不要任何解释"""
                },
                {
                    "role": "user",
                    "content": f"""前一个成语：{prev_idiom}
用户成语：{idiom}

请判断：
1. "{idiom}" 是一个有效的成语吗？
2. "{idiom}" 能接 "{prev_idiom}" 吗？

请只回答"是"或"否"。"""
                }
            ],
            "temperature": 0.1,
            "max_tokens": 10
        }

    def _parse_llm_response(self, response: str, idiom: str) -> ValidationResult:
        """解析LLM的响应"""
        response = response.strip()

        # 清理响应中的标点和空白
        for char in '。，！？、""''《》（）【】\n\r\t ':
            response = response.replace(char, '')

        # 处理重复字符的情况（如"是是"、"否否"、"是否"）
        # 只取第一个字符来判断
        if len(response) > 0:
            first_char = response[0]
            if first_char in ['是', 'Y', 'y', '对', '正']:
                self._last_error = ""
                return ValidationResult(True, "")
            elif first_char in ['否', 'N', 'n', '错', '错', '不', '无']:
                self._last_error = f"'{idiom}' 不是有效的成语或不满足接龙规则"
                return ValidationResult(False, self._last_error)

        # 完整匹配
        if response in ['是', 'YES', 'Yes', 'yes', '对', '正确', 'Valid', 'valid']:
            self._last_error = ""
            return ValidationResult(True, "")
        elif response in ['否', 'NO', 'No', 'no', '错', '错误', 'Invalid', 'invalid']:
            self._last_error = f"'{idiom}' 不是有效的成语或不满足接龙规则"
            return ValidationResult(False, self._last_error)
        else:
            # 无法解析，假设有效（宽松模式）
            logger.warning(f"无法解析LLM响应: {response}，假设有效")
            return ValidationResult(True, "")

    def get_last_error(self) -> str:
        """获取最后一次验证错误信息"""
        return self._last_error

    def can_chain(self, from_idiom: str, to_idiom: str,
                  allow_homophone: bool = False) -> bool:
        """检查两个成语是否可以接龙"""
        try:
            request_data = {
                "model": self.ai_client.model_name or "default",
                "messages": [
                    {
                        "role": "system",
                        "content": "你是成语接龙专家。请判断两个成语能否接龙。只回答'是'或'否'。"
                    },
                    {
                        "role": "user",
                        "content": f'"{from_idiom}" 能接 "{to_idiom}" 吗？'
                    }
                ],
                "temperature": 0.1,
                "max_tokens": 10
            }

            response = self.ai_client.session.post(
                f"{self.ai_client.base_url}/v1/chat/completions",
                json=request_data,
                timeout=self.ai_client.timeout
            )
            response.raise_for_status()

            data = response.json()
            if 'choices' in data and len(data['choices']) > 0:
                content = data['choices'][0]['message']['content']
                response = content.strip().replace('。', '').replace('，', '')
                return response in ['是', 'YES', 'Yes', 'yes', '对', '正确']

            return False

        except Exception as e:
            logger.error(f"LLM接龙检查失败: {str(e)}")
            return False
