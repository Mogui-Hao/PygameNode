import math

import pygame
from pygame import Rect, Vector3, Surface
from pygame.font import Font
from typing import Tuple, List, Callable

from .event import EventHandler, EventPriority
from .data.event import PointerClickEvent, PointerDownEvent, PointerUpEvent, PointerEvent, Event, PointerMoveEvent, WindowDropFileEvent
from .attribute.style import Style, TextStyle


class Node:
    font: Font = None

    def __init__(self,
                 name: str,                                 # 名字
                 parent: 'Node' = None,                     # 父对象
                 *,                                         # 后面必须位置传参
                 position: Vector3 = Vector3(0, 0, 0),      # 坐标
                 visible: bool = True,                      # 是否显示
                 rotation: float = 0.0,                     # 旋转
                 size: Tuple[int, int] = (0, 0),            # 大小
                 style: Style = Style()):
        self._name = name
        self._parent = parent
        self._style = style
        self.children: List['Node'] = []
        self._visible = visible
        self._rotation = rotation
        self._size = size
        self._position = position
        self._event = EventHandler()
        # self._surface = Surface((self.width, self.height), pygame.SRCALPHA)

    @property
    def name(self) -> str:
        """获取名字"""
        return self._name

    @name.setter
    def name(self, name: str):
        self._name = name

    @property
    def parent(self) -> 'Node':
        """获取父节点"""
        return self._parent

    @parent.setter
    def parent(self, parent: 'Node'):
        self._parent = parent
        parent.children.append(self)

    @property
    def style(self) -> Style:
        """获取样式"""
        return self._style

    @style.setter
    def style(self, style: Style):
        self._style = style

    @property
    def size(self) -> Tuple[int, int]:
        """获取大小"""
        return self._size

    @property
    def rect(self) -> Rect:
        """获取矩形区域"""
        return Rect(self._position.xy, self.size)

    @property
    def x(self) -> int:
        """获取 x 坐标"""
        return self._position.x

    @x.setter
    def x(self, x: int):
        offset = x - self.x
        for child in self.children:
            child.x += offset
        self._position.x = x

    @property
    def y(self) -> int:
        """获取 y 坐标"""
        return self._position.y

    @y.setter
    def y(self, y: int):
        offset = y - self.y
        for child in self.children:
            child.y += offset
        self._position.y = y

    @property
    def width(self) -> int:
        """获取宽"""
        return self._size[0]

    @property
    def height(self) -> int:
        """获取高"""
        return self._size[1]

    @property
    def visible(self) -> bool:
        """是否显示"""
        return self._visible

    @property
    def rotation(self) -> float:
        """获取旋转角度"""
        return self._rotation % 360

    @rotation.setter
    def rotation(self, rotation: float):
        self._rotation = rotation

    @property
    def surface(self) -> Surface:
        """获取区域"""
        return Surface((self.width, self.height), pygame.SRCALPHA)

    @property
    def mask(self):
        """获取实际内容区域"""
        return pygame.mask.from_surface(self.surface)

    @property
    def event(self) -> EventHandler:
        return self._event

    def draw(self, scene: Surface) -> None:
        if not self.visible:
            return
        if self.style.background.color is not None:
            pygame.draw.rect(self.surface, self.style.background.color.rgba, (0, 0, self.width, self.height), border_radius=self.style.background.border_radius)
            scene.blit(self.surface, (self.x, self.y))

    def update(self, dt: float) -> None:
        """更新状态"""
        for _node in self.children:
            _node.update(dt)

class TextNode(Node):
    def __init__(self,
                 text: str,                             # 文本
                 font: Font = None,                     # 字体
                 antialias: bool = False,               # 抗锯齿
                 name: str = None,
                 parent: 'Node' = None,
                 *,
                 position: Vector3 = Vector3(0, 0, 0),
                 visible: bool = True,
                 rotation: float = 0.0,
                 size: Tuple[int, int] = (0, 0),
                 style: Style = TextStyle()):
        super().__init__(name or "TextNode", parent, position=position, visible=visible, rotation=rotation, size=size, style=style)
        self._text = text
        self._font = font or Node.font
        self._antialias = antialias

    @property
    def text(self) -> str:
        """获取文本"""
        return self._text

    @text.setter
    def text(self, text: str):
        self._text = text

    @property
    def font(self) -> Font:
        """获取字体"""
        return self._font

    @font.setter
    def font(self, font: Font):
        self._font = font

    @property
    def style(self) -> TextStyle: return Node.style.fget(self)

    @property
    def antialias(self) -> bool:
        """获取抗锯齿"""
        return self._antialias

    @antialias.setter
    def antialias(self, antialias: bool):
        self._antialias = antialias

    @property
    def render(self):
        """获取渲染"""
        return self.font.render(self.text, self.antialias, self.style.color.rgb)

    @property
    def size(self):
        return self.render.get_size()

    def draw(self, scene: Surface) -> None:
        super().draw(scene)
        text = self.render
        if self.style.stroke.enable:
            text = self.text_stroke(text)
        if self.style.shadow.enable:
            scene.blit(*self.text_shadow(text))
        scene.blit(text, (self.x, self.y))

    def text_stroke(self, text_surface: Surface):
        """绘制带描边的文本"""
        stroke_size = self.style.stroke.size

        # 计算描边需要扩展的空间
        stroke_surface = pygame.Surface(self.size, pygame.SRCALPHA)

        # 在8个方向上绘制描边颜色
        offsets = [(-1, -1), (0, -1), (1, -1),
                   (-1,  0),          (1,  0),
                   (-1,  1), (0,  1), (1,  1)]

        for ox, oy in offsets:
            offset_x = stroke_size + ox * stroke_size
            offset_y = stroke_size + oy * stroke_size
            # 绘制描边颜色
            stroke_surface.blit(text_surface, (offset_x, offset_y))

        # 用描边颜色填充所有绘制过的区域
        for x in range(self.size[0]):
            for y in range(self.size[1]):
                if stroke_surface.get_at((x, y))[3] > 0:  # 如果有像素存在
                    stroke_surface.set_at((x, y), self.style.stroke.color.rgb)

        # 在描边Surface上绘制原始文本（覆盖中心部分）
        stroke_surface.blit(text_surface, (stroke_size, stroke_size))

        # 将带描边的文本绘制到场景
        # scene.blit(stroke_surface, (self.x - stroke_size, self.y - stroke_size))
        return stroke_surface

    def text_shadow(self, text_surface: Surface):
        """绘制带阴影和旋转的文本"""
        # 保存原始文本表面的尺寸和中心点
        original_rect = text_surface.get_rect(topleft=(self.x, self.y))

        # 1. 旋转文本表面（如果有旋转角度）
        # 使用rotozoom可以获得更平滑的旋转效果
        rotated_text_surface = pygame.transform.rotozoom(text_surface, self.rotation, 1)
        # 获取旋转后的矩形并保持中心点不变
        rotated_rect = rotated_text_surface.get_rect(center=original_rect.center)

        # 2. 计算阴影偏移量（根据角度和距离）
        angle_rad = math.radians(self.style.shadow.angle)
        shadow_offset_x = self.style.shadow.distance * math.cos(angle_rad)
        shadow_offset_y = self.style.shadow.distance * math.sin(angle_rad)

        # 3. 创建一个临时Surface来处理阴影的透明度
        shadow_surf = Surface(rotated_text_surface.get_size(), pygame.SRCALPHA)
        shadow_color_with_alpha = (*self.style.shadow.color.rgb, int(255 * self.style.shadow.opacity))
        shadow_surf.fill(shadow_color_with_alpha)

        # 4. 将旋转后文本的Alpha通道作为遮罩，应用到阴影Surface上
        text_surface_alpha = rotated_text_surface.copy().convert_alpha()
        shadow_surf.blit(text_surface_alpha, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        # 5. 计算阴影位置（考虑文本旋转后的新位置）
        shadow_x = rotated_rect.x + int(shadow_offset_x)
        shadow_y = rotated_rect.y + int(shadow_offset_y)

        # 6. 绘制阴影
        # scene.blit(shadow_surf, (shadow_x, shadow_y))
        return shadow_surf, (shadow_x, shadow_y)

        # 7. 绘制旋转后的原始文本（在阴影之上）
        # scene.blit(rotated_text_surface, rotated_rect.topleft)

class TextButtonNode(TextNode):
    def __init__(self,
                 text: str,
                 font: Font = None,
                 antialias: bool = False,
                 name: str = None,
                 parent: 'Node' = None,
                 *,
                 position: Vector3 = Vector3(0, 0, 0),
                 visible: bool = True,
                 rotation: float = 0.0,
                 size: Tuple[int, int] = (0, 0),
                 style: Style = TextStyle()):
        super().__init__(text, font, antialias, name, parent, position=position, visible=visible, rotation=rotation,
                         size=size, style=style)

        self.event(self.on_click)

    def on_click(self, event: WindowDropFileEvent):
        print(event.file)
        ...
