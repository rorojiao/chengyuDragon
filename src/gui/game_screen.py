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
from src.data.models import GameConfig, GameResult
from src.ai.lmstudio_client import LMStudioClient
from src.core.game_manager import GameManager
from src.core.score_calculator import ScoreCalculator
from src.gui.components.idiom_card import IdiomCard
from src.utils.exceptions import APIException
from src.utils.sound_manager import SoundManager


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

        # 初始化音效管理器
        self.sound_manager = SoundManager(parent=self)
        sound_enabled = self.config_manager.get('ui.sound_enabled', True)
        self.sound_manager.set_sound_enabled(sound_enabled)
        try:
            self.sound_manager.load_sounds()
        except Exception as e:
            logger.warning(f"音效加载失败: {e}")

        self.game_manager: Optional[GameManager] = None
        self.timer: Optional[QTimer] = None
        self.remaining_time = 0
        self.ai_thread = None  # AI线程引用
        self.current_game_config: Optional[GameConfig] = None  # 保存当前游戏配置

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

        # 保存游戏配置
        self.current_game_config = game_config

        # 创建游戏管理器（使用LLM验证器 - 支持任意成语）
        self.game_manager = GameManager(
            game_config,
            self.database,
            self.ai_client,
            use_llm_validator=True  # 使用LLM验证器，支持任意成语
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
        # 停止AI线程
        if self.ai_thread:
            try:
                if self.ai_thread.isRunning():
                    self.ai_thread.quit()
                    self.ai_thread.wait(1000)  # 等待最多1秒
            except RuntimeError:
                # 线程已被删除，忽略错误
                pass
            self.ai_thread = None

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
        # 确保在主线程中创建卡片（通过传递parent）
        card = IdiomCard(idiom, is_player, parent=self.idiom_container)

        # 尝试从数据库获取成语解释
        try:
            idiom_data = self.database.get_idiom_by_word(idiom)
            if idiom_data:
                card.set_explanation(
                    idiom_data.explanation,
                    idiom_data.pinyin
                )
        except Exception as e:
            logger.debug(f"无法获取成语解释: {e}")

        card.appear_animation()
        self.idiom_layout.addWidget(card)

        # 播放卡片出现音效
        if is_player:
            self.sound_manager.play_card_appear()

        # 滚动到底部
        scroll_area = self.idiom_container.parent()
        if hasattr(scroll_area, 'verticalScrollBar'):
            scrollbar = scroll_area.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())

    def _on_submit(self):
        """提交成语"""
        if not self.game_manager:
            return

        self.sound_manager.play_button_click()  # 播放按钮音效

        idiom = self.input_field.text().strip()
        if not idiom:
            self._show_message("请输入成语", "warning")
            return

        # 验证并提交
        result = self.game_manager.submit_player_idiom(idiom)

        if result.is_valid:
            self.sound_manager.play_submit()  # 播放提交音效
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
            self.sound_manager.play_error()  # 播放错误音效
            self._show_message(result.message, "error")
            self.input_field.setFocus()

    def _ai_turn(self):
        """AI回合"""
        if not self.game_manager:
            return

        try:
            # 获取AI响应（在后台线程中执行）
            from PyQt6.QtCore import QThread, Qt

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
            self.ai_thread = ai_thread  # 保存引用

            # 使用 QueuedConnection 确保在主线程中处理 UI 更新
            ai_thread.response_ready.connect(
                self._on_ai_idiom_received,
                Qt.ConnectionType.QueuedConnection
            )
            ai_thread.error_occurred.connect(
                self._on_ai_error,
                Qt.ConnectionType.QueuedConnection
            )

            # 线程完成后清理
            ai_thread.finished.connect(
                lambda: self._on_ai_thread_finished(),
                Qt.ConnectionType.QueuedConnection
            )

            ai_thread.start()

        except Exception as e:
            logger.error(f"AI回合出错: {str(e)}")
            self._show_message(f"AI出错: {str(e)}", "error")

    def _on_ai_thread_finished(self):
        """AI线程完成后的清理"""
        self.ai_thread = None

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
        self.sound_manager.play_ai_thinking()  # 播放AI思考音效
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

        self.sound_manager.play_button_click()  # 播放按钮音效

        hint = self.game_manager.use_hint()
        if hint:
            self.sound_manager.play_hint()  # 播放提示音效
            self._show_message(f"提示: {hint}", "info")
            self.input_field.setText(hint)
        else:
            self._show_message("没有可用的提示", "warning")

    def _on_forfeit(self):
        """认输"""
        if not self.game_manager:
            return

        self.sound_manager.play_button_click()  # 播放按钮音效

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

        # 播放结束音效
        if winner == 'player':
            self.sound_manager.play_victory()
        else:
            self.sound_manager.play_defeat()

        # 停止计时器
        if self.timer:
            self.timer.stop()

        # 禁用输入
        self.input_field.setEnabled(False)
        self.submit_button.setEnabled(False)
        self.hint_button.setEnabled(False)

        # 计算得分
        if winner == 'player':
            hints_used = self.current_game_config.max_hints - self.game_manager.get_game_state().player_hints_remaining
            score_details = ScoreCalculator.calculate_score(
                result,
                difficulty=self.current_game_config.difficulty,
                hints_used=hints_used,
                time_remaining=self.remaining_time
            )
            self._show_victory_dialog(score_details, result)
        else:
            self._show_defeat_dialog(result)

        logger.info(f"游戏结束: {winner} 获胜, 原因: {reason}")

    def _show_victory_dialog(self, score_details: dict, result: GameResult):
        """显示胜利对话框"""
        # 延迟一点显示，让用户看到最后一个成语
        QTimer.singleShot(1000, lambda: self._display_victory_dialog(score_details, result))

    def _display_victory_dialog(self, score_details: dict, result: GameResult):
        """实际显示胜利对话框"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QProgressBar
        from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve

        dialog = QDialog(self)
        dialog.setWindowTitle("恭喜获胜！")
        dialog.setMinimumSize(500, 400)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 评级
        rating_label = QLabel(f"评级: {score_details['rating']}")
        rating_label.setObjectName("victory_rating")
        rating_font = QFont()
        rating_font.setPointSize(48)
        rating_font.setBold(True)
        rating_label.setFont(rating_font)
        rating_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 根据评级设置颜色
        rating_colors = {
            "S": "#FFD700",  # 金色
            "A": "#C0C0C0",  # 银色
            "B": "#CD7F32",  # 铜色
            "C": "#87CEEB",  # 天蓝色
            "D": "#808080"   # 灰色
        }
        rating_color = rating_colors.get(score_details['rating'], "#FFD700")
        rating_label.setStyleSheet(f"QLabel {{ color: {rating_color}; }}")

        # 消息
        message_label = QLabel(score_details['message'])
        message_label.setObjectName("victory_message")
        message_font = QFont()
        message_font.setPointSize(18)
        message_label.setFont(message_font)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 统计信息
        stats_text = f"""
回合数: {result.total_rounds}
你的成语: {result.player_idiom_count} 个
AI成语: {result.ai_idiom_count} 个
游戏时长: {result.duration} 秒
总得分: {score_details['total_score']}

基础分: {score_details['base_score']}
难度加成: {score_details['difficulty_multiplier']}x
时间奖励: +{score_details['time_bonus']}
提示惩罚: -{score_details['hint_penalty']}
"""
        stats_label = QLabel(stats_text)
        stats_label.setObjectName("victory_stats")
        stats_font = QFont()
        stats_font.setPointSize(12)
        stats_label.setFont(stats_font)
        stats_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # 特殊奖励
        if score_details['special_bonuses']:
            bonuses_label = QLabel("特殊奖励:\n" + "\n".join(f"  • {bonus}" for bonus in score_details['special_bonuses']))
            bonuses_label.setObjectName("victory_bonuses")
            bonuses_font = QFont()
            bonuses_font.setPointSize(11)
            bonuses_label.setFont(bonuses_font)
            bonuses_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            layout.addWidget(bonuses_label)

        # 按钮
        button_layout = QHBoxLayout()

        main_menu_button = QPushButton("返回主菜单")
        main_menu_button.clicked.connect(lambda: (dialog.accept(), self._on_back_to_menu()))
        main_menu_button.setMinimumWidth(150)

        replay_button = QPushButton("再来一局")
        replay_button.clicked.connect(lambda: (dialog.accept(), self.start_new_game()))
        replay_button.setMinimumWidth(150)

        button_layout.addWidget(main_menu_button)
        button_layout.addWidget(replay_button)

        # 添加到布局
        layout.addWidget(rating_label)
        layout.addWidget(message_label)
        layout.addWidget(stats_label)
        layout.addLayout(button_layout)

        dialog.setLayout(layout)

        # 添加样式
        dialog.setStyleSheet("""
            QDialog {
                background-color: #FFF8E1;
            }
            QLabel#victory_message {
                color: #2E7D32;
                padding: 10px;
            }
            QLabel#victory_stats {
                color: #424242;
                padding: 15px;
                background-color: #FAFAFA;
                border-radius: 5px;
            }
            QLabel#victory_bonuses {
                color: #F57C00;
                padding: 10px;
            }
            QPushButton {
                font-size: 16px;
                padding: 10px 20px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45A049;
            }
        """)

        # 显示对话框
        dialog.exec()

    def _show_defeat_dialog(self, result: GameResult):
        """显示失败对话框"""
        reply = QMessageBox.question(
            self,
            "游戏结束",
            f"很遗憾，AI获胜了！\n\n"
            f"回合数: {result.total_rounds}\n"
            f"你的成语: {result.player_idiom_count} 个\n"
            f"AI成语: {result.ai_idiom_count} 个\n\n"
            f"是否再来一局？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.start_new_game()
        else:
            self._on_back_to_menu()

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
