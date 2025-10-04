
from dataclasses import dataclass
from enum import Flag, auto, Enum, unique
from typing import Optional, Tuple
from data.types import Color

@dataclass
class Style:
    def __init__(self):
        self.background = self.Background()
        self.stroke = self.Stroke()
        self.shadow = self.Shadow()

    @dataclass
    class Background:
        """背景"""
        color: Optional[Color] = None   # 颜色
        border_radius: int = 0          # 圆角(8)

    @dataclass
    class Stroke:
        """边缘"""
        enable: bool = False                    # 是否启用
        color: Color = Color(0, 0, 0)   # 颜色
        size: int = 1                           # 边缘大小

    @dataclass
    class Shadow:
        """阴影"""
        enable: bool = False                    # 是否启用
        color: Color = Color(0, 0, 0)   # 颜色
        opacity: float = 0.5                    # 不透明度
        ambiguity: float = 0.1                  # 模糊度
        distance: float = 8                     # 距本体距离
        angle: float = -45                      # 角度

@dataclass
class TextStyle(Style):
    def __init__(self, color: Optional[Color] = None):
        super().__init__()
        self.color = color or Color(0, 0, 0, 1)
        self.decoration = self.TextDecoration()

    @dataclass
    class TextDecoration:
        """字体装饰"""
        enable: bool = False                    # 是否启用
        dotted: bool = False                    # 虚线
        color: Color = Color(0, 0, 0)   # 颜色

