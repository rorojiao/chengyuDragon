"""
自定义异常类
"""


class GameException(Exception):
    """游戏基础异常"""

    pass


class ValidationException(GameException):
    """成语验证异常"""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class APIException(GameException):
    """API调用异常"""

    def __init__(self, message: str, retry_able: bool = False):
        self.message = message
        self.retry_able = retry_able
        super().__init__(message)


class DatabaseException(GameException):
    """数据库异常"""

    pass


class ConfigException(GameException):
    """配置异常"""

    pass


class TimeoutException(GameException):
    """超时异常"""

    pass
