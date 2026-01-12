"""
成语卡片组件
用于显示单个成语的卡片
"""

from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QToolTip
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QPoint
from PyQt6.QtGui import QFont, QCursor


class IdiomCard(QWidget):
    """成语卡片组件"""

    clicked = pyqtSignal()

    def __init__(self, idiom: str, is_player: bool = True, parent=None):
        """
        初始化成语卡片

        Args:
            idiom: 成语文本
            is_player: 是否是玩家的成语
            parent: 父窗口
        """
        super().__init__(parent)
        self.idiom = idiom
        self.is_player = is_player
        self._animation = None  # 保存动画对象的引用
        self.explanation = None  # 成语解释
        self.pinyin = None  # 拼音
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(10)

        # 角色标签
        self.role_label = QLabel("你" if self.is_player else "AI")
        self.role_label.setObjectName("player_label")
        self.role_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.role_label)

        # 成语文本
        self.idiom_label = QLabel(self.idiom)
        self.idiom_label.setObjectName("idiom_text")
        font = QFont()
        font.setPointSize(24)
        font.setBold(True)
        self.idiom_label.setFont(font)
        self.idiom_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.idiom_label)

        # 拼音标签
        self.pinyin_label = QLabel()
        self.pinyin_label.setObjectName("pinyin_label")
        pinyin_font = QFont()
        pinyin_font.setPointSize(12)
        self.pinyin_label.setFont(pinyin_font)
        self.pinyin_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pinyin_label.setVisible(False)  # 默认隐藏
        layout.addWidget(self.pinyin_label)

        self.setLayout(layout)

        # 设置卡片样式
        self.set_card_style()

        # 设置固定大小
        self.setFixedHeight(140)

        # 启用鼠标追踪和点击
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

    def set_card_style(self):
        """设置卡片样式"""
        self.setProperty("player", "true" if self.is_player else "false")
        self.style().unpolish(self)
        self.style().polish(self)

    def set_idiom(self, idiom: str):
        """
        设置成语

        Args:
            idiom: 新的成语
        """
        self.idiom = idiom
        self.idiom_label.setText(idiom)

    def set_explanation(self, explanation: str, pinyin: str = None):
        """
        设置成语解释

        Args:
            explanation: 成语解释
            pinyin: 拼音
        """
        self.explanation = explanation
        if pinyin:
            self.pinyin = pinyin
            self.pinyin_label.setText(pinyin)
            self.pinyin_label.setVisible(True)

    def appear_animation(self):
        """出现动画（使用 QTimer 延迟执行，避免线程问题）"""
        from PyQt6.QtCore import QTimer

        self.show()

        # 使用单次定时器在下一帧执行淡入动画
        QTimer.singleShot(10, self._start_fade_animation)

    def _start_fade_animation(self):
        """开始淡入动画"""
        # 使用 QGraphicsEffect 实现淡入效果
        from PyQt6.QtWidgets import QGraphicsOpacityEffect

        self._opacity_effect = QGraphicsOpacityEffect(self)
        self._opacity_effect.setOpacity(0)
        self.setGraphicsEffect(self._opacity_effect)

        # 创建动画
        self._animation = QPropertyAnimation(self._opacity_effect, b"opacity")
        self._animation.setDuration(400)
        self._animation.setStartValue(0)
        self._animation.setEndValue(1)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        # 动画结束后清理
        self._animation.finished.connect(self._on_animation_finished)
        self._animation.start()

    def _on_animation_finished(self):
        """动画完成处理"""
        # 保留效果但不保留动画对象
        self._animation = None

    def enterEvent(self, event):
        """鼠标进入事件"""
        # 显示工具提示
        if self.explanation:
            tooltip_text = f"<b>{self.idiom}</b>"
            if self.pinyin:
                tooltip_text += f"<br><i>{self.pinyin}</i>"
            tooltip_text += f"<br><br>{self.explanation}"

            # 设置工具提示样式
            QToolTip.showText(
                self.mapToGlobal(self.rect().bottomLeft()),
                tooltip_text,
                self
            )
        super().enterEvent(event)

    def leaveEvent(self, event):
        """鼠标离开事件"""
        QToolTip.hideText()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        """鼠标点击事件"""
        self.clicked.emit()
        super().mousePressEvent(event)
