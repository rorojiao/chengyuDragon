"""
成语接龙游戏 - 主入口
"""

import sys
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from src.gui.main_window import MainWindow
from src.config.config_manager import ConfigManager
from src.data.database import IdiomDatabase
from src.ai.lmstudio_client import LMStudioClient


def setup_logging(config_manager: ConfigManager):
    """
    设置日志

    Args:
        config_manager: 配置管理器
    """
    log_level = config_manager.get('logging.level', 'INFO')
    log_file = config_manager.get('logging.file', 'logs/game.log')
    log_max_size = config_manager.get('logging.max_size', 10485760)

    # 确保日志目录存在
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)

    # 配置日志
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )


def main():
    """主函数"""
    # 创建应用
    app = QApplication(sys.argv)
    app.setApplicationName("成语接龙")
    app.setOrganizationName("YourCompany")

    # 加载配置
    config_manager = ConfigManager()

    # 设置日志
    setup_logging(config_manager)
    logger = logging.getLogger(__name__)
    logger.info("=" * 50)
    logger.info("成语接龙游戏启动")
    logger.info("=" * 50)

    # 初始化数据库
    db_path = config_manager.get('database.path', 'resources/idioms.db')
    logger.info(f"数据库路径: {db_path}")
    database = IdiomDatabase(db_path)

    # 检查数据库是否为空
    if database.get_total_count() == 0:
        logger.warning("数据库为空，请导入成语数据")
        # TODO: 可以在这里添加自动导入逻辑

    # 初始化AI客户端
    api_base_url = config_manager.get('api.base_url', 'http://localhost:1234')
    model_name = config_manager.get('api.model_name', '')
    api_timeout = config_manager.get('api.timeout', 30)

    logger.info(f"API地址: {api_base_url}")
    ai_client = LMStudioClient(
        base_url=api_base_url,
        model_name=model_name,
        timeout=api_timeout
    )

    # 创建主窗口
    main_window = MainWindow(
        config_manager=config_manager,
        database=database,
        ai_client=ai_client
    )

    # 加载样式
    style_file = Path(__file__).parent / "src/gui/styles/style.qss"
    if style_file.exists():
        with open(style_file, 'r', encoding='utf-8') as f:
            app.setStyleSheet(f.read())
            logger.info("加载样式表成功")

    # 显示窗口
    main_window.show()

    logger.info("应用启动完成")

    # 运行应用
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
