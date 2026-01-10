"""
设置面板
用于配置游戏和API设置
"""

import logging
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QSpinBox, QComboBox,
                             QCheckBox, QGroupBox, QFormLayout, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal

from src.config.config_manager import ConfigManager
from src.config.defaults import (
    DIFFICULTY_LEVELS, THEME_OPTIONS, TIME_LIMIT_OPTIONS
)
from src.ai.lmstudio_client import LMStudioClient


logger = logging.getLogger(__name__)


class SettingsPanel(QWidget):
    """设置面板"""

    # 信号定义
    back_clicked = pyqtSignal()

    def __init__(self, config_manager: ConfigManager,
                 ai_client: LMStudioClient,
                 parent=None):
        """
        初始化设置面板

        Args:
            config_manager: 配置管理器
            ai_client: AI客户端
            parent: 父窗口
        """
        super().__init__(parent)

        self.config_manager = config_manager
        self.ai_client = ai_client

        self.init_ui()
        self.load_settings()

    def init_ui(self):
        """初始化UI"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 创建滚动区域
        from PyQt6.QtWidgets import QScrollArea, QWidget
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # 滚动内容
        scroll_content = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # 标题
        title_label = QLabel("设置")
        title_label.setObjectName("settings_title")
        layout.addWidget(title_label)

        # API设置组
        api_group = QGroupBox("API 设置")
        api_layout = QFormLayout()

        self.api_url_input = QLineEdit()
        api_layout.addRow("API 地址:", self.api_url_input)

        self.model_name_input = QLineEdit()
        api_layout.addRow("模型名称:", self.model_name_input)

        api_button_layout = QHBoxLayout()
        self.test_connection_button = QPushButton("测试连接")
        self.test_connection_button.clicked.connect(self._test_connection)
        api_button_layout.addWidget(self.test_connection_button)

        self.connection_status_label = QLabel()
        self.connection_status_label.setObjectName("status_indicator")
        api_button_layout.addWidget(self.connection_status_label)

        api_button_layout.addStretch()
        api_layout.addRow("", api_button_layout)

        api_group.setLayout(api_layout)
        layout.addWidget(api_group)

        # 游戏设置组
        game_group = QGroupBox("游戏设置")
        game_layout = QFormLayout()

        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItems(["简单", "普通", "困难"])
        game_layout.addRow("难度:", self.difficulty_combo)

        self.time_limit_spin = QSpinBox()
        self.time_limit_spin.setRange(0, 300)
        self.time_limit_spin.setSuffix(" 秒")
        self.time_limit_spin.setSpecialValueText("无限制")
        game_layout.addRow("时间限制:", self.time_limit_spin)

        self.allow_homophone_check = QCheckBox("允许同音字")
        game_layout.addRow("", self.allow_homophone_check)

        self.max_hints_spin = QSpinBox()
        self.max_hints_spin.setRange(0, 10)
        self.max_hints_spin.setSuffix(" 次")
        game_layout.addRow("最大提示次数:", self.max_hints_spin)

        game_group.setLayout(game_layout)
        layout.addWidget(game_group)

        # 界面设置组
        ui_group = QGroupBox("界面设置")
        ui_layout = QFormLayout()

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["默认", "暗色"])
        ui_layout.addRow("主题:", self.theme_combo)

        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(12, 24)
        self.font_size_spin.setSuffix(" pt")
        ui_layout.addRow("字体大小:", self.font_size_spin)

        self.animation_check = QCheckBox("启用动画")
        self.animation_check.setChecked(True)
        ui_layout.addRow("", self.animation_check)

        self.sound_check = QCheckBox("启用音效")
        self.sound_check.setChecked(True)
        ui_layout.addRow("", self.sound_check)

        ui_group.setLayout(ui_layout)
        layout.addWidget(ui_group)

        layout.addStretch()

        scroll_content.setLayout(layout)
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

        # 按钮区域（固定在底部）
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(20, 10, 20, 20)

        self.save_button = QPushButton("保存")
        self.save_button.clicked.connect(self._save_settings)
        button_layout.addWidget(self.save_button)

        self.reset_button = QPushButton("重置默认")
        self.reset_button.clicked.connect(self._reset_defaults)
        button_layout.addWidget(self.reset_button)

        self.back_button = QPushButton("返回")
        self.back_button.clicked.connect(self._on_back)
        button_layout.addWidget(self.back_button)

        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        logger.info("设置面板初始化完成")

    def load_settings(self):
        """加载设置"""
        # API设置
        self.api_url_input.setText(
            self.config_manager.get('api.base_url', 'http://localhost:1234')
        )
        self.model_name_input.setText(
            self.config_manager.get('api.model_name', '')
        )

        # 游戏设置
        difficulty = self.config_manager.get('game.difficulty', 'normal')
        difficulty_map = {'easy': 0, 'normal': 1, 'hard': 2}
        self.difficulty_combo.setCurrentIndex(difficulty_map.get(difficulty, 1))

        self.time_limit_spin.setValue(
            self.config_manager.get('game.time_limit', 60)
        )

        self.allow_homophone_check.setChecked(
            self.config_manager.get('game.allow_homophone', False)
        )

        self.max_hints_spin.setValue(
            self.config_manager.get('game.max_hints', 3)
        )

        # 界面设置
        theme = self.config_manager.get('ui.theme', 'default')
        self.theme_combo.setCurrentIndex(0 if theme == 'default' else 1)

        self.font_size_spin.setValue(
            self.config_manager.get('ui.font_size', 16)
        )

        self.animation_check.setChecked(
            self.config_manager.get('ui.animation_enabled', True)
        )

        self.sound_check.setChecked(
            self.config_manager.get('ui.sound_enabled', True)
        )

        logger.info("设置已加载")

    def _save_settings(self):
        """保存设置"""
        try:
            # API设置
            self.config_manager.set('api.base_url', self.api_url_input.text())
            self.config_manager.set('api.model_name', self.model_name_input.text())

            # 游戏设置
            difficulty_map = {0: 'easy', 1: 'normal', 2: 'hard'}
            self.config_manager.set(
                'game.difficulty',
                difficulty_map.get(self.difficulty_combo.currentIndex(), 'normal')
            )
            self.config_manager.set('game.time_limit', self.time_limit_spin.value())
            self.config_manager.set(
                'game.allow_homophone',
                self.allow_homophone_check.isChecked()
            )
            self.config_manager.set('game.max_hints', self.max_hints_spin.value())

            # 界面设置
            theme_map = {0: 'default', 1: 'dark'}
            self.config_manager.set(
                'ui.theme',
                theme_map.get(self.theme_combo.currentIndex(), 'default')
            )
            self.config_manager.set('ui.font_size', self.font_size_spin.value())
            self.config_manager.set(
                'ui.animation_enabled',
                self.animation_check.isChecked()
            )
            self.config_manager.set('ui.sound_enabled', self.sound_check.isChecked())

            # 更新AI客户端配置
            self.ai_client.set_base_url(self.api_url_input.text())
            if self.model_name_input.text():
                self.ai_client.set_model(self.model_name_input.text())

            logger.info("设置已保存")
            self._show_message("设置已保存", "success")

        except Exception as e:
            logger.error(f"保存设置失败: {str(e)}")
            self._show_message(f"保存设置失败: {str(e)}", "error")

    def _reset_defaults(self):
        """重置为默认设置"""
        reply = QMessageBox.question(
            self,
            "确认重置",
            "确定要重置为默认设置吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.config_manager.reset_to_default()
            self.load_settings()
            self._show_message("已重置为默认设置", "info")

    def _test_connection(self):
        """测试API连接"""
        api_url = self.api_url_input.text()

        if not api_url:
            self._show_message("请输入API地址", "warning")
            return

        self.connection_status_label.setText("连接中...")
        self.connection_status_label.setProperty("state", "connecting")
        self.connection_status_label.style().unpolish(self.connection_status_label)
        self.connection_status_label.style().polish(self.connection_status_label)

        # 更新AI客户端地址
        self.ai_client.set_base_url(api_url)

        # 测试连接
        if self.model_name_input.text():
            self.ai_client.set_model(self.model_name_input.text())

        success = self.ai_client.test_connection()

        if success:
            self.connection_status_label.setText("已连接")
            self.connection_status_label.setProperty("state", "connected")
            self._show_message("API连接成功！", "success")

            # 获取可用模型
            models = self.ai_client.get_available_models()
            if models and not self.model_name_input.text():
                self.model_name_input.setText(models[0])
        else:
            self.connection_status_label.setText("未连接")
            self.connection_status_label.setProperty("state", "disconnected")
            self._show_message("API连接失败，请检查设置", "error")

        self.connection_status_label.style().unpolish(self.connection_status_label)
        self.connection_status_label.style().polish(self.connection_status_label)

    def _on_back(self):
        """返回按钮点击事件"""
        self.back_clicked.emit()

    def _show_message(self, message: str, msg_type: str = "info"):
        """显示消息"""
        QMessageBox.information(self, "提示", message)
