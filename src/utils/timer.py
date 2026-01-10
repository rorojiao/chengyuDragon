"""
计时器工具
"""

import time
from typing import Optional, Callable


class Timer:
    """简单的计时器类"""

    def __init__(self, duration: float, callback: Optional[Callable] = None):
        """
        初始化计时器

        Args:
            duration: 计时时长（秒）
            callback: 超时回调函数
        """
        self.duration = duration
        self.callback = callback
        self.start_time: Optional[float] = None
        self.remaining_time = duration
        self.is_running = False

    def start(self) -> None:
        """开始计时"""
        self.start_time = time.time()
        self.is_running = True

    def stop(self) -> None:
        """停止计时"""
        if self.is_running and self.start_time:
            elapsed = time.time() - self.start_time
            self.remaining_time = max(0, self.remaining_time - elapsed)
        self.is_running = False
        self.start_time = None

    def reset(self, duration: Optional[float] = None) -> None:
        """
        重置计时器

        Args:
            duration: 新的计时时长，如果不指定则使用原时长
        """
        self.stop()
        if duration is not None:
            self.duration = duration
        self.remaining_time = self.duration

    def get_elapsed_time(self) -> float:
        """
        获取已过去的时间

        Returns:
            已经过去的秒数
        """
        if self.start_time is None:
            return 0.0
        return time.time() - self.start_time

    def get_remaining_time(self) -> float:
        """
        获取剩余时间

        Returns:
            剩余的秒数
        """
        if not self.is_running:
            return self.remaining_time
        elapsed = self.get_elapsed_time()
        return max(0, self.duration - elapsed)

    def is_expired(self) -> bool:
        """
        检查是否超时

        Returns:
            是否超时
        """
        return self.get_remaining_time() <= 0

    def update(self) -> None:
        """更新计时器状态，检查是否超时"""
        if self.is_running and self.is_expired() and self.callback:
            self.stop()
            self.callback()


class CountdownTimer:
    """倒计时器类，用于游戏回合计时"""

    def __init__(self, duration: int, on_tick: Optional[Callable[[int], None]] = None,
                 on_timeout: Optional[Callable[[], None]] = None):
        """
        初始化倒计时器

        Args:
            duration: 倒计时时长（秒）
            on_tick: 每秒回调函数，参数为剩余秒数
            on_timeout: 超时回调函数
        """
        self.duration = duration
        self.on_tick = on_tick
        self.on_timeout = on_timeout
        self.remaining = duration
        self.is_running = False

    def start(self) -> None:
        """开始倒计时"""
        self.is_running = True
        self.remaining = self.duration
        if self.on_tick:
            self.on_tick(self.remaining)

    def stop(self) -> None:
        """停止倒计时"""
        self.is_running = False

    def reset(self) -> None:
        """重置倒计时"""
        self.stop()
        self.remaining = self.duration

    def tick(self) -> None:
        """减少一秒"""
        if self.is_running:
            self.remaining -= 1
            if self.on_tick:
                self.on_tick(self.remaining)
            if self.remaining <= 0:
                self.is_running = False
                if self.on_timeout:
                    self.on_timeout()

    def get_remaining(self) -> int:
        """获取剩余秒数"""
        return max(0, self.remaining)
