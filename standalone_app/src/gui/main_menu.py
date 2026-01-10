"""
主菜单界面
游戏的起始界面
"""

import logging
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton,
                             QHBoxLayout)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


logger = logging.getLogger(__name__)


class MainMenu(QWidget):
    """主菜单界面"""

    # 信号定义
    start_game_clicked = pyqtSignal()
    settings_clicked = pyqtSignal()
    quit_clicked = pyqtSignal()

    def __init__(self, parent=None):
        """
        初始化主菜单

        Args:
            parent: 父窗口
        """
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(30)

        # 标题
        title_label = QLabel("成语接龙")
        title_label.setObjectName("title_label")
        title_font = QFont()
        title_font.setPointSize(48)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # 副标题
        subtitle_label = QLabel("与AI进行智慧对决")
        subtitle_label.setObjectName("subtitle_label")
        subtitle_font = QFont()
        subtitle_font.setPointSize(14)
        subtitle_label.setFont(subtitle_font)
        layout.addWidget(subtitle_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # 按钮容器
        button_layout = QVBoxLayout()
        button_layout.setSpacing(20)

        # 开始游戏按钮
        self.start_button = QPushButton("开始游戏")
        self.start_button.setMinimumWidth(200)
        self.start_button.clicked.connect(self._on_start_game)
        button_layout.addWidget(
            self.start_button,
            alignment=Qt.AlignmentFlag.AlignCenter
        )

        # 设置按钮
        self.settings_button = QPushButton("设置")
        self.settings_button.setMinimumWidth(200)
        self.settings_button.clicked.connect(self._on_settings)
        button_layout.addWidget(
            self.settings_button,
            alignment=Qt.AlignmentFlag.AlignCenter
        )

        # 退出按钮
        self.quit_button = QPushButton("退出")
        self.quit_button.setMinimumWidth(200)
        self.quit_button.clicked.connect(self._on_quit)
        button_layout.addWidget(
            self.quit_button,
            alignment=Qt.AlignmentFlag.AlignCenter
        )

        layout.addLayout(button_layout)
        layout.addStretch()

        self.setLayout(layout)

        logger.info("主菜单初始化完成")

    def _on_start_game(self):
        """开始游戏按钮点击事件"""
        logger.info("点击开始游戏")
        self.start_game_clicked.emit()

    def _on_settings(self):
        """设置按钮点击事件"""
        logger.info("点击设置")
        self.settings_clicked.emit()

    def _on_quit(self):
        """退出按钮点击事件"""
        logger.info("点击退出")
        self.quit_clicked.emit()
