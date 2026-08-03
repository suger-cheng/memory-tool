"""可翻转卡片 Widget。三种类型差异化渲染。"""

from __future__ import annotations

import math

from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Property, QRect, Signal
from PySide6.QtGui import QPainter, QColor, QFont, QPen, QFontMetrics
from PySide6.QtWidgets import QWidget

from ui.theme import get_color


class FlipCard(QWidget):
    """支持三种类型渲染模式的卡片 Widget。"""

    flipped = Signal(bool)  # 翻转后发射，参数为当前是否显示背面

    def __init__(self, parent=None):
        super().__init__(parent)
        self._front = ""
        self._back = ""
        self._extra = ""
        self._card_type = "card"  # card | note | quote
        self._flipped = False
        self._angle = 0.0  # 0..180 (用于翻转动画)
        self._scroll_offset = 0
        self._text_total_h = 0
        self.setMinimumHeight(320)
        self.setCursor(Qt.PointingHandCursor)

    def set_content(self, front: str, back: str, extra: str = "",
                    card_type: str = "card"):
        self._front = front
        self._back = back
        self._extra = extra
        self._card_type = card_type
        self._flipped = False
        self._angle = 0.0
        self._scroll_offset = 0
        self.update()

    def is_flipped(self) -> bool:
        return self._flipped

    def card_type(self) -> str:
        return self._card_type

    def flip(self):
        target = 180.0 if not self._flipped else 0.0
        self._anim = QPropertyAnimation(self, b"angle", self)
        duration = 250 if self._card_type == "note" else 350
        self._anim.setDuration(duration)
        self._anim.setStartValue(self._angle)
        self._anim.setEndValue(target)
        self._anim.setEasingCurve(QEasingCurve.InOutCubic)
        self._anim.valueChanged.connect(self._on_angle)
        self._anim.start()
        self._flipped = not self._flipped
        self._scroll_offset = 0
        self.flipped.emit(self._flipped)

    def _on_angle(self, v):
        self._angle = float(v)
        self.update()

    def get_angle(self) -> float:
        return self._angle

    def set_angle(self, v: float):
        self._angle = v
        self.update()

    angle = Property(float, get_angle, set_angle)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            if self._flipped:
                self._scroll_offset = 0
            self.flip()
            return
        super().mousePressEvent(e)

    def wheelEvent(self, e):
        if self._text_total_h <= 0:
            return
        delta = e.angleDelta().y()
        old = self._scroll_offset
        self._scroll_offset = max(0, min(
            self._text_total_h, self._scroll_offset - delta))
        if self._scroll_offset != old:
            self.update()

    def _draw_scrollbar(self, p: QPainter, r: QRect):
        if self._text_total_h <= 0:
            return
        track_h = r.height() - 20
        ratio = track_h / (track_h + self._text_total_h)
        thumb_h = max(24, int(track_h * ratio))
        progress = self._scroll_offset / self._text_total_h if self._text_total_h > 0 else 0
        thumb_y = r.y() + 10 + int(progress * (track_h - thumb_h))
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(200, 200, 200, 40))
        p.drawRoundedRect(r.right() - 8, r.y() + 10, 4, track_h, 2, 2)
        p.setBrush(QColor(160, 160, 160, 160))
        p.drawRoundedRect(r.right() - 8, thumb_y, 4, thumb_h, 2, 2)

    # ==================== 绘制 ====================
    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.TextAntialiasing)
        r = self.rect().adjusted(10, 10, -10, -10)

        if self._card_type == "note":
            self._paint_note(p, r)
        elif self._card_type == "quote":
            self._paint_quote(p, r)
        else:
            self._paint_card(p, r)

    # ---------- 记忆卡片：3D 翻转 ----------
    def _paint_card(self, p: QPainter, r: QRect):
        showing_front = self._angle < 90.0
        scale = abs(math.cos(math.radians(self._angle)))
        w = max(1, int(r.width() * scale))
        x = r.center().x() - w // 2
        draw_rect = QRect(x, r.y(), w, r.height())

        # 卡片背景
        p.setBrush(QColor(get_color("card", "#FFFFFF")))
        p.setPen(QColor(get_color("border", "#E0DED8")))
        p.drawRoundedRect(draw_rect, 16, 16)

        text = self._front if showing_front else self._back
        label = "🎴 问题" if showing_front else "🎴 答案"

        # 顶部标签
        p.setPen(QColor(get_color("subtext", "#9A9AB0")))
        f = QFont(); f.setPointSize(9); p.setFont(f)
        p.drawText(QRect(draw_rect.x(), draw_rect.y() + 14, draw_rect.width(), 20),
                   Qt.AlignCenter, label)

        # 主文本
        p.setPen(QColor(get_color("text", "#2D2D2D")))
        f = QFont(); f.setPointSize(18); f.setBold(True); p.setFont(f)
        text_rect = draw_rect.adjusted(24, 40, -24, -40)

        if not showing_front:
            fm = QFontMetrics(f)
            br = fm.boundingRect(
                QRect(0, 0, draw_rect.width() - 48, 10000),
                Qt.AlignCenter | Qt.TextWordWrap, self._back)
            extra_h = 32 if self._extra else 0
            content_bottom = 40 + br.height() + extra_h
            clip_bottom = draw_rect.height() - 40
            self._text_total_h = max(0, content_bottom - clip_bottom + 50)

            p.save()
            p.setClipRect(draw_rect.adjusted(2, 2, -2, -2))
            p.translate(0, -self._scroll_offset)
            back_text_rect = QRect(draw_rect.x() + 24, draw_rect.y() + 40,
                                   draw_rect.width() - 48, br.height() + 40)
            p.drawText(back_text_rect, Qt.AlignTop | Qt.AlignHCenter | Qt.TextWordWrap, self._back)
            if self._extra:
                p.setPen(QColor(get_color("subtext", "#6B6B6B")))
                f2 = QFont(); f2.setPointSize(10); f2.setItalic(True); p.setFont(f2)
                p.drawText(QRect(draw_rect.x(), back_text_rect.bottom() + 8,
                                 draw_rect.width(), 24),
                           Qt.AlignCenter, self._extra)
            p.restore()
            self._draw_scrollbar(p, draw_rect)
        else:
            self._text_total_h = 0
            p.drawText(text_rect, Qt.AlignCenter | Qt.TextWordWrap, text)
            if self._extra:
                p.setPen(QColor(get_color("subtext", "#6B6B6B")))
                f2 = QFont(); f2.setPointSize(10); f2.setItalic(True); p.setFont(f2)
                p.drawText(QRect(draw_rect.x(), draw_rect.bottom() - 36,
                                 draw_rect.width(), 24),
                           Qt.AlignCenter, self._extra)

    # ---------- 知识点：上下展开阅读布局 ----------
    def _paint_note(self, p: QPainter, r: QRect):
        showing_front = self._angle < 90.0
        scale = abs(math.cos(math.radians(self._angle)))
        # note 用纵向展开：正面高度缩小，背面展开全高
        if showing_front:
            # 正面：标题卡，居中偏上
            h = max(80, int(r.height() * 0.45))
            y = r.center().y() - h // 2
            draw_rect = QRect(r.x(), y, r.width(), h)
        else:
            # 背面：全高展开
            draw_rect = QRect(r.x(), r.y(), r.width(), r.height())

        # 左侧彩色条标识
        accent = QColor(get_color("accent_blue", "#7BAFD4"))

        # 卡片背景
        p.setBrush(QColor(get_color("card", "#FFFFFF")))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(draw_rect, 14, 14)

        # 左侧色条
        bar_rect = QRect(draw_rect.x(), draw_rect.y() + 8, 5, draw_rect.height() - 16)
        p.setBrush(accent)
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(bar_rect, 3, 3)

        # 边框
        p.setBrush(Qt.NoBrush)
        p.setPen(QColor(get_color("border", "#E0DED8")))
        p.drawRoundedRect(draw_rect, 14, 14)

        content_x = draw_rect.x() + 20
        content_w = draw_rect.width() - 40

        if showing_front:
            # 标签
            p.setPen(accent)
            f = QFont(); f.setPointSize(10); f.setBold(True); p.setFont(f)
            p.drawText(QRect(content_x, draw_rect.y() + 16, content_w, 20),
                       Qt.AlignLeft, "📝 知识点")

            # 标题（大字）
            p.setPen(QColor(get_color("text", "#2D2D2D")))
            f = QFont(); f.setPointSize(22); f.setBold(True); p.setFont(f)
            p.drawText(QRect(content_x, draw_rect.y() + 42, content_w,
                             draw_rect.height() - 80),
                       Qt.AlignCenter | Qt.TextWordWrap, self._front)

            # 提示
            p.setPen(QColor(get_color("subtext", "#9A9AB0")))
            f = QFont(); f.setPointSize(9); p.setFont(f)
            p.drawText(QRect(content_x, draw_rect.bottom() - 28, content_w, 18),
                       Qt.AlignCenter, "点击展开详细内容")
        else:
            # 标签（固定不滚动）
            p.setPen(accent)
            f = QFont(); f.setPointSize(10); f.setBold(True); p.setFont(f)
            p.drawText(QRect(content_x, draw_rect.y() + 14, content_w, 20),
                       Qt.AlignLeft, "📝 知识点")

            # 计算可滚动内容总高度
            tf = QFont(); tf.setPointSize(16); tf.setBold(True)
            tfm = QFontMetrics(tf)
            title_br = tfm.boundingRect(
                QRect(content_x, 0, content_w, 10000),
                Qt.AlignLeft | Qt.TextWordWrap, self._front)
            title_h = title_br.height()
            bf = QFont(); bf.setPointSize(13)
            bfm = QFontMetrics(bf)
            body_br = bfm.boundingRect(
                QRect(content_x, 0, content_w, 10000),
                Qt.AlignLeft | Qt.TextWordWrap, self._back)
            extra_h = 22 if self._extra else 0
            # 内容底端位置：标题(38开始) + 分隔线(6) + 正文前间隔(10) + 正文高 + 附加信息
            content_bottom = (38 + title_h + 6 + 10 + body_br.height()
                              + extra_h)
            clip_bottom = draw_rect.height() - 4
            self._text_total_h = max(0, content_bottom - clip_bottom + 50)

            # 可滚动区域：标题 + 分隔线 + 正文
            p.save()
            p.setClipRect(draw_rect.x(), draw_rect.y() + 38,
                          draw_rect.width(),
                          draw_rect.height() - 42)
            p.translate(0, -self._scroll_offset)

            # 标题
            p.setPen(QColor(get_color("text", "#2D2D2D")))
            p.setFont(tf)
            p.drawText(QRect(content_x, draw_rect.y() + 38, content_w, title_h),
                       Qt.AlignLeft | Qt.TextWordWrap, self._front)

            # 分隔线
            line_y = draw_rect.y() + 38 + title_h + 6
            p.setPen(QPen(QColor(get_color("border", "#E0DED8")), 1))
            p.drawLine(content_x, line_y, content_x + content_w, line_y)

            # 正文内容
            body_y = line_y + 10
            p.setPen(QColor(get_color("text", "#2D2D2D")))
            p.setFont(bf)
            body_rect = QRect(content_x, body_y, content_w, body_br.height() + 200)
            p.drawText(body_rect, Qt.AlignLeft | Qt.TextWordWrap, self._back)

            # 附加信息
            if self._extra:
                p.setPen(QColor(get_color("subtext", "#6B6B6B")))
                ef = QFont(); ef.setPointSize(10); ef.setItalic(True); p.setFont(ef)
                p.drawText(QRect(content_x, body_rect.bottom() + 4,
                                 content_w, 18),
                           Qt.AlignRight, self._extra)
            p.restore()
            self._draw_scrollbar(p, draw_rect)

    # ---------- 语录：大字居中 + 装饰引号 ----------
    def _paint_quote(self, p: QPainter, r: QRect):
        showing_front = self._angle < 90.0
        scale = abs(math.cos(math.radians(self._angle)))
        w = max(1, int(r.width() * scale))
        x = r.center().x() - w // 2
        draw_rect = QRect(x, r.y(), w, r.height())

        # 卡片背景（微暖色）
        bg = QColor(get_color("card", "#FFFFFF"))
        p.setBrush(bg)
        p.setPen(QColor(get_color("border", "#E0DED8")))
        p.drawRoundedRect(draw_rect, 16, 16)

        accent = QColor(get_color("accent_orange", "#D4A574"))
        content_rect = draw_rect.adjusted(40, 50, -40, -50)

        if showing_front:
            # 大引号装饰（左上）
            p.setPen(accent)
            f = QFont("Georgia", 60); f.setBold(True); p.setFont(f)
            p.drawText(QRect(draw_rect.x() + 16, draw_rect.y() + 4,
                             80, 70), Qt.AlignLeft | Qt.AlignTop, "\u201C")
            # 大引号装饰（右下）
            p.drawText(QRect(draw_rect.right() - 80, draw_rect.bottom() - 60,
                             80, 60), Qt.AlignRight | Qt.AlignBottom, "\u201D")

            # 语录正文（大字，楷体风格）
            p.setPen(QColor(get_color("text", "#2D2D2D")))
            f = QFont(); f.setPointSize(20); f.setBold(False); p.setFont(f)
            p.drawText(content_rect, Qt.AlignCenter | Qt.TextWordWrap, self._front)

            # 底部标签
            p.setPen(QColor(get_color("subtext", "#9A9AB0")))
            f = QFont(); f.setPointSize(9); p.setFont(f)
            p.drawText(QRect(draw_rect.x(), draw_rect.bottom() - 28,
                             draw_rect.width(), 18),
                       Qt.AlignCenter, "💬 语录 · 点击翻转查看感悟")
        else:
            # 背面：作者/出处 + 感悟（固定不滚动）
            p.setPen(accent)
            f = QFont(); f.setPointSize(10); f.setBold(True); p.setFont(f)
            p.drawText(QRect(draw_rect.x() + 20, draw_rect.y() + 16,
                             draw_rect.width() - 40, 20),
                       Qt.AlignLeft, "💬 感悟与出处")

            # 计算可滚动内容总高度
            qf = QFont(); qf.setPointSize(11); qf.setItalic(True)
            qfm = QFontMetrics(qf)
            quote_br = qfm.boundingRect(
                QRect(content_rect.x(), 0, content_rect.width(), 10000),
                Qt.AlignCenter | Qt.TextWordWrap,
                f"\u201C{self._front}\u201D")
            quote_h = quote_br.height()
            bf = QFont(); bf.setPointSize(15)
            bfm = QFontMetrics(bf)
            back_br = bfm.boundingRect(
                QRect(content_rect.x(), 0, content_rect.width(), 10000),
                Qt.AlignCenter | Qt.TextWordWrap, self._back)
            extra_h = 22 if self._extra else 0
            # 内容底端位置：quote 起始(50) + quote高 + 间隔(10) + 分隔线(2) + 间隔(16)
            #              + 感悟高 + 附加信息
            content_bottom = (50 + quote_h + 10 + 10 + 2 + 16
                              + back_br.height() + extra_h)
            clip_bottom = draw_rect.height() - 4
            self._text_total_h = max(0, content_bottom - clip_bottom + 50)

            # 可滚动区域
            p.save()
            p.setClipRect(draw_rect.x(), draw_rect.y() + 40,
                          draw_rect.width(),
                          draw_rect.height() - 44)
            p.translate(0, -self._scroll_offset)

            # 原文引用（小字）
            p.setPen(QColor(get_color("subtext", "#6B6B6B")))
            p.setFont(qf)
            quote_rect = QRect(content_rect.x(),
                               draw_rect.y() + content_rect.top() - draw_rect.top(),
                               content_rect.width(), quote_h + 10)
            p.drawText(quote_rect, Qt.AlignTop | Qt.AlignHCenter | Qt.TextWordWrap,
                       f"\u201C{self._front}\u201D")

            # 分隔线
            sep_y = quote_rect.bottom() + 10
            p.setPen(QPen(accent, 2))
            line_w = min(80, draw_rect.width() // 4)
            cx = draw_rect.center().x()
            p.drawLine(cx - line_w // 2, sep_y, cx + line_w // 2, sep_y)

            # 背面内容（感悟/出处）
            p.setPen(QColor(get_color("text", "#2D2D2D")))
            p.setFont(bf)
            back_rect = QRect(content_rect.x(), sep_y + 16,
                              content_rect.width(), back_br.height() + 200)
            p.drawText(back_rect, Qt.AlignTop | Qt.AlignHCenter | Qt.TextWordWrap, self._back)

            # 附加信息
            if self._extra:
                p.setPen(QColor(get_color("subtext", "#6B6B6B")))
                ef = QFont(); ef.setPointSize(10); ef.setItalic(True); p.setFont(ef)
                p.drawText(QRect(draw_rect.x(), back_rect.bottom() + 4,
                                 draw_rect.width(), 18),
                           Qt.AlignCenter, self._extra)
            p.restore()
            self._draw_scrollbar(p, draw_rect)
