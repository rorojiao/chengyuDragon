"""
主窗口
应用程序的主窗口，包含所有子界面
"""

import logging
from PyQt6.QtWidgets import (QMainWindow, QStackedWidget, QVBoxLayout,
                             QWidget, QMessageBox, QStatusBar)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon

from src.gui.main_menu import MainMenu
from src.gui.game_screen import GameScreen
from src.gui.settings_panel import SettingsPanel
from src.config.config_manager import ConfigManager
from src.data.database import IdiomDatabase
from src.ai.lmstudio_client import LMStudioClient


logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """主窗口类"""

    def __init__(self, config_manager: ConfigManager,
                 database: IdiomDatabase,
                 ai_client: LMStudioClient):
        """
        初始化主窗口

        Args:
            config_manager: 配置管理器
            database: 成语数据库
            ai_client: AI客户端
        """
        super().__init__()

        self.config_manager = config_manager
        self.database = database
        self.ai_client = ai_client

        # 设置窗口
        self.init_window()

        # 创建中央窗口
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # 初始化各个界面
        self.init_screens()

        # 创建状态栏
        self.setStatusBar(QStatusBar())

        # 加载样式
        self.load_theme()

        logger.info("主窗口初始化完成")

    def init_window(self):
        """初始化窗口设置"""
        self.setWindowTitle("成语接龙")
        self.setMinimumSize(1000, 700)

        # 尝试设置窗口图标
        try:
            icon_path = "resources/icons/app_icon.ico"
            self.setWindowIcon(QIcon(icon_path))
        except Exception as e:
            logger.warning(f"无法加载窗口图标: {e}")

    def init_screens(self):
        """初始化各个界面"""
        # 主菜单
        self.main_menu = MainMenu(self)
        self.stacked_widget.addWidget(self.main_menu)

        # 游戏界面
        self.game_screen = GameScreen(
            self.config_manager,
            self.database,
            self.ai_client,
            self
        )
        self.stacked_widget.addWidget(self.game_screen)

        # 设置面板
        self.settings_panel = SettingsPanel(
            self.config_manager,
            self.ai_client,
            self
        )
        self.stacked_widget.addWidget(self.settings_panel)

        # 连接信号
        self.main_menu.start_game_clicked.connect(self.start_game)
        self.main_menu.settings_clicked.connect(self.show_settings)
        self.main_menu.quit_clicked.connect(self.close)

        self.game_screen.back_to_menu.connect(self.show_main_menu)
        self.settings_panel.back_clicked.connect(self.show_main_menu)

        # 默认显示主菜单
        self.show_main_menu()

    def load_theme(self):
        """加载主题"""
        theme = self.config_manager.get('ui.theme', 'default')
        if theme == 'dark':
            self.setProperty("theme", "dark")

    def show_main_menu(self):
        """显示主菜单"""
        self.stacked_widget.setCurrentWidget(self.main_menu)
        self.statusBar().showMessage("欢迎来到成语接龙！")

    def show_game_screen(self):
        """显示游戏界面"""
        self.stacked_widget.setCurrentWidget(self.game_screen)

    def show_settings(self):
        """显示设置面板"""
        self.stacked_widget.setCurrentWidget(self.settings_panel)

    def start_game(self):
        """开始游戏"""
        logger.info("开始新游戏")
        self.show_game_screen()
        self.game_screen.start_new_game()
        self.statusBar().showMessage("游戏进行中...")

    def closeEvent(self, event):
        """窗口关闭事件"""
        reply = QMessageBox.question(
            self,
            "确认退出",
            "确定要退出成语接龙吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # 关闭数据库连接
            self.database.close()
            logger.info("应用退出")
            event.accept()
        else:
            event.ignore()
