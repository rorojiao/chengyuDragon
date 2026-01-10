"""
成语卡片组件
用于显示单个成语的卡片
"""

from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont


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

        self.setLayout(layout)

        # 设置卡片样式
        self.set_card_style()

        # 设置固定大小
        self.setFixedHeight(120)

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

    def appear_animation(self):
        """出现动画"""
        self.setWindowOpacity(0)
        self.show()

        animation = QPropertyAnimation(self, b"windowOpacity")
        animation.setDuration(300)
        animation.setStartValue(0)
        animation.setEndValue(1)
        animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        animation.start()

    def mousePressEvent(self, event):
        """鼠标点击事件"""
        self.clicked.emit()
        super().mousePressEvent(event)
