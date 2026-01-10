"""
默认配置定义
"""

# API配置默认值
DEFAULT_API_CONFIG = {
    'base_url': 'http://localhost:1234',
    'model_name': '',
    'timeout': 30,
    'max_retries': 3
}

# 游戏配置默认值
DEFAULT_GAME_CONFIG = {
    'difficulty': 'normal',  # easy, normal, hard
    'time_limit': 60,
    'allow_homophone': False,
    'max_hints': 3
}

# UI配置默认值
DEFAULT_UI_CONFIG = {
    'theme': 'default',
    'font_size': 16,
    'animation_enabled': True,
    'sound_enabled': True
}

# 数据库配置默认值
DEFAULT_DATABASE_CONFIG = {
    'path': 'resources/idioms.db',
    'backup_enabled': True
}

# 日志配置默认值
DEFAULT_LOGGING_CONFIG = {
    'level': 'INFO',
    'file': 'logs/game.log',
    'max_size': 10485760  # 10MB
}

# 难度级别
DIFFICULTY_LEVELS = ['easy', 'normal', 'hard']

# 主题选项
THEME_OPTIONS = ['default', 'dark']

# 时间限制选项（秒）
TIME_LIMIT_OPTIONS = [0, 30, 60, 120]  # 0表示无限制
