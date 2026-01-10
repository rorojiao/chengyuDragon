"""
配置管理器
负责加载、保存和管理应用程序配置
"""

import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from src.utils.exceptions import ConfigException


class ConfigManager:
    """配置管理器"""

    def __init__(self, config_path: str = "config.yaml"):
        """
        初始化配置管理器

        Args:
            config_path: 配置文件路径
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """
        加载配置文件

        Returns:
            配置字典
        """
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
            except Exception as e:
                raise ConfigException(f"加载配置文件失败: {str(e)}")
        else:
            return self._create_default_config()

    def _create_default_config(self) -> Dict[str, Any]:
        """
        创建默认配置

        Returns:
            默认配置字典
        """
        default = {
            'api': {
                'base_url': 'http://localhost:1234',
                'model_name': '',
                'timeout': 30,
                'max_retries': 3
            },
            'game': {
                'difficulty': 'normal',
                'time_limit': 60,
                'allow_homophone': False,
                'max_hints': 3
            },
            'ui': {
                'theme': 'default',
                'font_size': 16,
                'animation_enabled': True,
                'sound_enabled': True
            },
            'database': {
                'path': 'resources/idioms.db',
                'backup_enabled': True
            },
            'logging': {
                'level': 'INFO',
                'file': 'logs/game.log',
                'max_size': 10485760
            }
        }
        self.save_config(default)
        return default

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        获取配置值

        Args:
            key_path: 配置键路径，使用点号分隔（如 'api.base_url'）
            default: 默认值

        Returns:
            配置值
        """
        keys = key_path.split('.')
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    def set(self, key_path: str, value: Any) -> None:
        """
        设置配置值

        Args:
            key_path: 配置键路径，使用点号分隔
            value: 要设置的值
        """
        keys = key_path.split('.')
        config = self.config
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        config[keys[-1]] = value
        self.save_config()

    def save_config(self, config: Dict = None) -> None:
        """
        保存配置到文件

        Args:
            config: 要保存的配置字典，默认为当前配置
        """
        if config is None:
            config = self.config
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.safe_dump(config, f, allow_unicode=True, sort_keys=False)
        except Exception as e:
            raise ConfigException(f"保存配置文件失败: {str(e)}")

    def get_all(self) -> Dict[str, Any]:
        """
        获取所有配置

        Returns:
            完整的配置字典
        """
        return self.config.copy()

    def reset_to_default(self) -> None:
        """重置为默认配置"""
        self.config = self._create_default_config()
