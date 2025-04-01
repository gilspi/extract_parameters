import os
import math
import cairo
import gi

gi.require_version("Gtk", "3.0")  # Требуемая версия GTK
from gi.repository import Gtk, GLib

from graphics.factory.progress_bar import BaseProgressBar


class GtkProgressBar(Gtk.DrawingArea):
    def __init__(self, *args, **kwargs):
        Gtk.DrawingArea.__init__(self, *args, **kwargs)
        
        self.dot_phase = 0.0          # Фаза анимации для индикатора
        self.animation_id = None      # ID таймера анимации
        self._cached_background = None
        self._cached_width = None
        self._cached_height = None
        
        self.connect("draw", self.on_draw)
        self.connect("configure-event", self.on_configure)

    def set_fraction(self, fraction: float) -> None:
        self.progress_fraction = fraction
        self.queue_draw()

    def start_animation(self) -> None:
        if not self.animating:
            self.animating = True
            self.animation_id = GLib.timeout_add(100, self.update_animation)

    def stop_animation(self) -> None:
        self.animating = False
        if self.animation_id is not None:
            GLib.source_remove(self.animation_id)
            self.animation_id = None

    def get_widget(self) -> Gtk.DrawingArea:
        return self

    def update_animation(self) -> bool:
        if not self.animating:
            return False
        self.dot_phase += 0.1
        self.queue_draw()
        return True

    def on_configure(self, widget, event):
        self._cached_background = None
        return False

    def draw_rounded_rect(self, cr, x, y, w, h, r):
        # Рисует прямоугольник с округлёнными углами с радиусом r
        cr.new_sub_path()
        cr.arc(x + w - r, y + r, r, -math.pi/2, 0)
        cr.arc(x + w - r, y + h - r, r, 0, math.pi/2)
        cr.arc(x + r, y + h - r, r, math.pi/2, math.pi)
        cr.arc(x + r, y + r, r, math.pi, 3*math.pi/2)
        cr.close_path()

    def on_draw(self, widget, cr):
        width = widget.get_allocated_width()
        height = widget.get_allocated_height()

        # Кэширование статического фона прогресс-бара
        if self._cached_background is None or self._cached_width != width or self._cached_height != height:
            self._cached_width = width
            self._cached_height = height
            self._cached_background = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
            bg_cr = cairo.Context(self._cached_background)
            radius = height / 2
            bg_cr.set_source_rgb(0.85, 0.85, 0.85)
            bg_cr.arc(radius, radius, radius, math.pi, 1.5 * math.pi)
            bg_cr.arc(width - radius, radius, radius, 1.5 * math.pi, 0)
            bg_cr.arc(width - radius, height - radius, radius, 0, 0.5 * math.pi)
            bg_cr.arc(radius, height - radius, radius, 0.5 * math.pi, math.pi)
            bg_cr.close_path()
            bg_cr.fill()

        # Рисуем кэшированный фон
        cr.set_source_surface(self._cached_background, 0, 0)
        cr.paint()

        # Рисуем динамическую заполненную часть прогресс-бара
        radius = height / 2
        fill_width = max(radius * 2, width * self.progress_fraction)
        cr.set_source_rgb(0.66, 0.87, 0.68)
        cr.arc(radius, radius, radius, math.pi, 1.5 * math.pi)
        cr.arc(fill_width - radius, radius, radius, 1.5 * math.pi, 0)
        cr.arc(fill_width - radius, height - radius, radius, 0, 0.5 * math.pi)
        cr.arc(radius, height - radius, radius, 0.5 * math.pi, math.pi)
        cr.close_path()
        cr.fill()

        # Отрисовка процентного значения по центру
        cr.set_source_rgb(0, 0, 0)
        cr.select_font_face("Code", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        cr.set_font_size(16)
        progress_text = f"{int(self.progress_fraction * 100)}%"
        text_extents = cr.text_extents(progress_text)
        text_x = (width - text_extents.width) / 2
        text_y = (height - text_extents.height) / 2 - text_extents.y_bearing
        cr.move_to(text_x, text_y)
        cr.show_text(progress_text)

        # Анимированный индикатор под процентами
        indicator_margin = 5
        indicator_height = 6
        indicator_y = text_y + text_extents.height + indicator_margin
        if indicator_y + indicator_height > height:
            indicator_y = height - indicator_height - 1

        full_width = text_extents.width
        dot_diameter = 6

        t = (1 - math.cos(self.dot_phase)) / 2
        current_width = dot_diameter + (full_width - dot_diameter) * math.sin(math.pi * t)

        text_center = text_x + full_width / 2
        indicator_x = text_center - current_width / 2

        cr.set_source_rgb(0.6, 0.6, 0.6)
        corner_radius = indicator_height / 2
        self.draw_rounded_rect(cr, indicator_x, indicator_y, current_width, indicator_height, corner_radius)
        cr.fill()

        return False