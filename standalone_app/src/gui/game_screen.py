"""
游戏界面
主要游戏进行界面
"""

import logging
from typing import Optional
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QScrollArea, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QKeyEvent

from src.config.config_manager import ConfigManager
from src.data.database import IdiomDatabase
from src.data.models import GameConfig
from src.ai.lmstudio_client import LMStudioClient
from src.core.game_manager import GameManager
from src.gui.components.idiom_card import IdiomCard
from src.utils.exceptions import APIException


logger = logging.getLogger(__name__)


class GameScreen(QWidget):
    """游戏界面"""

    # 信号定义
    back_to_menu = pyqtSignal()

    def __init__(self, config_manager: ConfigManager,
                 database: IdiomDatabase,
                 ai_client: LMStudioClient,
                 parent=None):
        """
        初始化游戏界面

        Args:
            config_manager: 配置管理器
            database: 成语数据库
            ai_client: AI客户端
            parent: 父窗口
        """
        super().__init__(parent)

        self.config_manager = config_manager
        self.database = database
        self.ai_client = ai_client

        self.game_manager: Optional[GameManager] = None
        self.timer: Optional[QTimer] = None
        self.remaining_time = 0

        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # 顶部标题栏
        top_bar = QHBoxLayout()

        # 返回按钮
        self.back_button = QPushButton("返回主菜单")
        self.back_button.clicked.connect(self._on_back_to_menu)
        top_bar.addWidget(self.back_button)

        top_bar.addStretch()

        # 回合信息
        self.round_label = QLabel("第 0 回合")
        self.round_label.setObjectName("round_info")
        round_font = QFont()
        round_font.setPointSize(14)
        self.round_label.setFont(round_font)
        top_bar.addWidget(self.round_label)

        layout.addLayout(top_bar)

        # 成语显示区域（滚动）
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setObjectName("idiom_display_area")

        self.idiom_container = QWidget()
        self.idiom_layout = QVBoxLayout()
        self.idiom_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.idiom_container.setLayout(self.idiom_layout)
        scroll_area.setWidget(self.idiom_container)

        layout.addWidget(scroll_area, stretch=1)

        # 消息标签
        self.message_label = QLabel("")
        self.message_label.setObjectName("message_label")
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.hide()
        layout.addWidget(self.message_label)

        # 计时器标签
        self.timer_label = QLabel("")
        self.timer_label.setObjectName("timer_label")
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_label.hide()
        layout.addWidget(self.timer_label)

        # 输入区域
        input_area = QWidget()
        input_area.setObjectName("input_area")
        input_layout = QHBoxLayout()

        self.input_field = QLineEdit()
        self.input_field.setObjectName("input_field")
        self.input_field.setPlaceholderText("请输入成语...")
        self.input_field.setMaxLength(4)
        self.input_field.returnPressed.connect(self._on_submit)
        input_layout.addWidget(self.input_field)

        self.submit_button = QPushButton("提交")
        self.submit_button.setObjectName("submit_button")
        self.submit_button.clicked.connect(self._on_submit)
        input_layout.addWidget(self.submit_button)

        self.hint_button = QPushButton("提示")
        self.hint_button.setObjectName("hint_button")
        self.hint_button.clicked.connect(self._on_hint)
        input_layout.addWidget(self.hint_button)

        self.forfeit_button = QPushButton("认输")
        self.forfeit_button.setObjectName("forfeit_button")
        self.forfeit_button.clicked.connect(self._on_forfeit)
        input_layout.addWidget(self.forfeit_button)

        input_area.setLayout(input_layout)
        layout.addWidget(input_area)

        self.setLayout(layout)

        logger.info("游戏界面初始化完成")

    def start_new_game(self):
        """开始新游戏"""
        # 清理旧游戏
        self._cleanup_game()

        # 清空成语显示
        for i in reversed(range(self.idiom_layout.count())):
            self.idiom_layout.itemAt(i).widget().setParent(None)

        # 加载游戏配置
        game_config = GameConfig(
            difficulty=self.config_manager.get('game.difficulty', 'normal'),
            time_limit=self.config_manager.get('game.time_limit', 60),
            allow_homophone=self.config_manager.get('game.allow_homophone', False),
            max_hints=self.config_manager.get('game.max_hints', 3)
        )

        # 创建游戏管理器
        self.game_manager = GameManager(
            game_config,
            self.database,
            self.ai_client
        )

        # 设置回调
        self.game_manager.on_state_change = self._on_state_change
        self.game_manager.on_ai_thinking = self._on_ai_thinking
        self.game_manager.on_ai_response = self._on_ai_response

        # 开始游戏
        self.game_manager.start_game()

        # 更新UI
        self._update_ui()

        # 如果有时间限制，启动计时器
        if game_config.time_limit > 0:
            self.remaining_time = game_config.time_limit
            self.timer_label.setText(f"⏱ {self.remaining_time}秒")
            self.timer_label.show()
            self.timer = QTimer()
            self.timer.timeout.connect(self._on_timer_tick)
            self.timer.start(1000)

        # 启用输入
        self.input_field.setEnabled(True)
        self.input_field.setFocus()

        logger.info("新游戏开始")

    def _cleanup_game(self):
        """清理游戏状态"""
        if self.timer:
            self.timer.stop()
            self.timer = None

        self.timer_label.hide()
        self.message_label.hide()
        self.input_field.clear()

    def _update_ui(self):
        """更新UI显示"""
        if not self.game_manager:
            return

        state = self.game_manager.get_game_state()

        # 更新回合信息
        self.round_label.setText(f"第 {state.current_round} 回合")

        # 更新提示按钮
        hints_remaining = state.player_hints_remaining
        self.hint_button.setText(f"提示({hints_remaining})")
        self.hint_button.setEnabled(hints_remaining > 0)

        # 根据回合启用/禁用输入
        self.input_field.setEnabled(state.is_player_turn and not state.game_over)
        self.submit_button.setEnabled(state.is_player_turn and not state.game_over)

    def _add_idiom_card(self, idiom: str, is_player: bool):
        """添加成语卡片到显示区域"""
        card = IdiomCard(idiom, is_player)
        card.appear_animation()
        self.idiom_layout.addWidget(card)

        # 滚动到底部
        scroll_area = self.idiom_container.parent()
        if hasattr(scroll_area, 'verticalScrollBar'):
            scrollbar = scroll_area.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())

    def _on_submit(self):
        """提交成语"""
        if not self.game_manager:
            return

        idiom = self.input_field.text().strip()
        if not idiom:
            self._show_message("请输入成语", "warning")
            return

        # 验证并提交
        result = self.game_manager.submit_player_idiom(idiom)

        if result.is_valid:
            self.input_field.clear()
            self._add_idiom_card(idiom, is_player=True)
            self._show_message("正确！", "success")

            # 检查游戏是否结束
            winner = self.game_manager.check_game_over()
            if winner:
                self._end_game(winner, "对方无法接龙")
            else:
                # AI回合
                QTimer.singleShot(500, self._ai_turn)
        else:
            self._show_message(result.message, "error")
            self.input_field.setFocus()

    def _ai_turn(self):
        """AI回合"""
        if not self.game_manager:
            return

        try:
            # 获取AI响应（在后台线程中执行）
            from PyQt6.QtCore import QThread

            class AIThread(QThread):
                response_ready = pyqtSignal(str)
                error_occurred = pyqtSignal(str)

                def __init__(self, game_manager):
                    super().__init__()
                    self.game_manager = game_manager

                def run(self):
                    try:
                        idiom = self.game_manager.get_ai_response()
                        self.response_ready.emit(idiom)
                    except Exception as e:
                        self.error_occurred.emit(str(e))

            ai_thread = AIThread(self.game_manager)
            ai_thread.response_ready.connect(
                lambda idiom: self._on_ai_idiom_received(idiom)
            )
            ai_thread.error_occurred.connect(
                lambda error: self._on_ai_error(error)
            )
            ai_thread.start()

        except Exception as e:
            logger.error(f"AI回合出错: {str(e)}")
            self._show_message(f"AI出错: {str(e)}", "error")

    def _on_ai_idiom_received(self, idiom: str):
        """AI成语接收处理"""
        if idiom:
            self._add_idiom_card(idiom, is_player=False)
            self._show_message(f"AI: {idiom}", "info")

            # 检查游戏是否结束
            winner = self.game_manager.check_game_over()
            if winner:
                self._end_game(winner, "对方无法接龙")

    def _on_ai_error(self, error: str):
        """AI错误处理"""
        logger.error(f"AI错误: {error}")
        self._show_message(f"AI错误: {error}", "error")

    def _on_ai_thinking(self):
        """AI思考状态"""
        self._show_message("AI思考中...", "info")

    def _on_ai_response(self, idiom: str):
        """AI响应回调"""
        pass  # 已经在 _on_ai_idiom_received 中处理

    def _on_state_change(self):
        """游戏状态变化"""
        self._update_ui()

    def _on_hint(self):
        """使用提示"""
        if not self.game_manager:
            return

        hint = self.game_manager.use_hint()
        if hint:
            self._show_message(f"提示: {hint}", "info")
            self.input_field.setText(hint)
        else:
            self._show_message("没有可用的提示", "warning")

    def _on_forfeit(self):
        """认输"""
        if not self.game_manager:
            return

        reply = QMessageBox.question(
            self,
            "确认认输",
            "确定要认输吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self._end_game('ai', '玩家认输')

    def _on_timer_tick(self):
        """计时器滴答"""
        self.remaining_time -= 1
        self.timer_label.setText(f"⏱ {self.remaining_time}秒")

        if self.remaining_time <= 10:
            self.timer_label.setStyleSheet("color: red;")

        if self.remaining_time <= 0:
            self.timer.stop()
            self._end_game('ai', '超时')

    def _end_game(self, winner: str, reason: str):
        """结束游戏"""
        if not self.game_manager:
            return

        result = self.game_manager.end_game(winner, reason)

        # 停止计时器
        if self.timer:
            self.timer.stop()

        # 禁用输入
        self.input_field.setEnabled(False)
        self.submit_button.setEnabled(False)
        self.hint_button.setEnabled(False)

        # 显示结果
        if winner == 'player':
            message = f"🎉 恭喜你获胜！\n\n{self._get_result_summary(result)}"
            self._show_message(message, "success")
        else:
            message = f"😢 AI获胜\n\n{self._get_result_summary(result)}"
            self._show_message(message, "error")

        logger.info(f"游戏结束: {winner} 获胜, 原因: {reason}")

    def _get_result_summary(self, result) -> str:
        """获取结果摘要"""
        return (
            f"回合数: {result.total_rounds}\n"
            f"你的成语: {result.player_idiom_count}\n"
            f"AI成语: {result.ai_idiom_count}\n"
            f"游戏时长: {result.duration}秒"
        )

    def _on_back_to_menu(self):
        """返回主菜单"""
        if self.game_manager and not self.game_manager.get_game_state().game_over:
            reply = QMessageBox.question(
                self,
                "确认返回",
                "游戏正在进行中，确定要返回主菜单吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply != QMessageBox.StandardButton.Yes:
                return

        self._cleanup_game()
        self.back_to_menu.emit()

    def _show_message(self, message: str, msg_type: str = "info"):
        """显示消息"""
        self.message_label.setText(message)
        self.message_label.setProperty("type", msg_type)
        self.message_label.style().unpolish(self.message_label)
        self.message_label.style().polish(self.message_label)
        self.message_label.show()

        # 3秒后自动隐藏
        QTimer.singleShot(3000, self.message_label.hide)

    def keyPressEvent(self, event: QKeyEvent):
        """键盘事件"""
        if event.key() == Qt.Key.Key_Escape:
            self._on_back_to_menu()
        else:
            super().keyPressEvent(event)
