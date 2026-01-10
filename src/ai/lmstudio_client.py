"""
LM Studio API客户端
用于与本地运行的LM Studio服务通信
"""

import requests
import logging
from typing import Optional, List, Dict, Any
from src.utils.exceptions import APIException


logger = logging.getLogger(__name__)


class LMStudioClient:
    """LM Studio API客户端类"""

    def __init__(self, base_url: str = "http://localhost:1234",
                 model_name: str = "", timeout: int = 30):
        """
        初始化客户端

        Args:
            base_url: LM Studio API基础URL
            model_name: 模型名称
            timeout: 请求超时时间（秒）
        """
        self.base_url = base_url.rstrip('/')
        self.model_name = model_name
        self.timeout = timeout
        self.session = requests.Session()

    def test_connection(self) -> bool:
        """
        测试API连接

        Returns:
            连接是否成功
        """
        try:
            response = self.session.get(
                f"{self.base_url}/v1/models",
                timeout=5
            )
            if response.status_code == 200:
                logger.info("API连接测试成功")
                return True
            else:
                logger.warning(f"API连接测试失败，状态码: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"API连接测试失败: {str(e)}")
            return False

    def get_available_models(self) -> List[str]:
        """
        获取可用模型列表

        Returns:
            模型名称列表
        """
        try:
            response = self.session.get(
                f"{self.base_url}/v1/models",
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()

            models = []
            if 'data' in data:
                models = [model['id'] for model in data['data']]

            logger.info(f"获取到 {len(models)} 个可用模型")
            return models
        except Exception as e:
            logger.error(f"获取模型列表失败: {str(e)}")
            return []

    def generate_idiom(self, prompt: Dict[str, Any],
                      temperature: float = 0.7,
                      max_tokens: int = 50) -> str:
        """
        生成成语

        Args:
            prompt: 提示词字典
            temperature: 温度参数
            max_tokens: 最大token数

        Returns:
            生成的成语

        Raises:
            APIException: API调用失败
        """
        if not self.model_name:
            # 尝试自动获取模型名称
            models = self.get_available_models()
            if not models:
                raise APIException("没有可用的模型，请先在LM Studio中加载模型")
            self.model_name = models[0]
            logger.info(f"自动选择模型: {self.model_name}")

        # 构建请求数据
        request_data = {
            "model": self.model_name,
            "messages": prompt.get("messages", []),
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        try:
            logger.debug(f"发送请求到 {self.base_url}/v1/chat/completions")
            response = self.session.post(
                f"{self.base_url}/v1/chat/completions",
                json=request_data,
                timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()

            # 提取生成的文本
            if 'choices' in data and len(data['choices']) > 0:
                content = data['choices'][0]['message']['content']
                # 清理结果，只保留成语
                idiom = self._extract_idiom(content)
                logger.info(f"AI生成成语: {idiom}")
                return idiom
            else:
                raise APIException("API返回的数据格式不正确")

        except requests.Timeout:
            logger.error("API请求超时")
            raise APIException("API请求超时", retry_able=True)
        except requests.RequestException as e:
            logger.error(f"API请求失败: {str(e)}")
            raise APIException(f"API请求失败: {str(e)}", retry_able=True)
        except Exception as e:
            logger.error(f"生成成语失败: {str(e)}")
            raise APIException(f"生成成语失败: {str(e)}")

    def _extract_idiom(self, text: str) -> str:
        """
        从生成的文本中提取成语

        Args:
            text: 生成的文本

        Returns:
            提取的成语
        """
        # 去除前后空白
        text = text.strip()

        # 去除常见的编号前缀
        prefixes_to_remove = ['1.', '2.', '3.', '•', '-', '*', '1、', '2、', '①', '②']
        for prefix in prefixes_to_remove:
            if text.startswith(prefix):
                text = text[1:].strip()
                break

        # 去除可能的标点符号和引号
        for char in '，。！？、""''《》（）【】.,!?;:':
            text = text.replace(char, '')

        # 去除换行符
        text = text.replace('\n', '').replace('\r', '')

        # 提取中文字符（只保留汉字）
        chinese_chars = []
        for char in text:
            if '\u4e00' <= char <= '\u9fff':  # 汉字范围
                chinese_chars.append(char)
            if len(chinese_chars) >= 4:
                break

        result = ''.join(chinese_chars)

        # 确保是4个字
        if len(result) >= 4:
            return result[:4]
        elif len(result) > 0:
            return result
        else:
            return "无法接龙"  # 失败时返回特殊标记

    def set_model(self, model_name: str) -> None:
        """
        设置使用的模型

        Args:
            model_name: 模型名称
        """
        self.model_name = model_name
        logger.info(f"设置模型: {model_name}")

    def set_base_url(self, base_url: str) -> None:
        """
        设置API基础URL

        Args:
            base_url: API基础URL
        """
        self.base_url = base_url.rstrip('/')
        logger.info(f"设置API地址: {self.base_url}")

    def set_timeout(self, timeout: int) -> None:
        """
        设置请求超时时间

        Args:
            timeout: 超时时间（秒）
        """
        self.timeout = timeout
        logger.info(f"设置超时时间: {timeout}秒")

    def __del__(self):
        """析构函数，关闭会话"""
        if hasattr(self, 'session'):
            self.session.close()
