import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GObject, GLib

class IosStyleSwitch(Gtk.DrawingArea):
    __gsignals__ = {
        'state-set': (GObject.SIGNAL_RUN_FIRST, None, (bool,))
    }

    def __init__(self, active=False, size=(50, 25)):
        super().__init__()
        self.active = active
        self.size = size
        self.animation_progress = 1.0 if self.active else 0.0
        self.animating = False

        self.set_size_request(*self.size)
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.connect("draw", self.on_draw)
        self.connect("button-press-event", self.on_toggle)

    def on_draw(self, widget, cr):
        width, height = self.size
        radius = height / 2
        handle_radius = radius - 2

        # Фон переключателя
        bg_color_active = (0.3, 0.8, 0.4)
        bg_color_inactive = (0.6, 0.6, 0.6)
        bg_color = [
            bg_color_inactive[i] + (bg_color_active[i] - bg_color_inactive[i]) * self.animation_progress
            for i in range(3)
        ]

        cr.set_source_rgb(*bg_color)
        cr.arc(radius, radius, radius, 0, 2 * 3.14)
        cr.arc(width - radius, radius, radius, 0, 2 * 3.14)
        cr.rectangle(radius, 0, width - 2 * radius, height)
        cr.fill()

        # Ручка переключателя
        handle_x_start = radius
        handle_x_end = width - radius
        handle_x = handle_x_start + (handle_x_end - handle_x_start) * self.animation_progress

        cr.set_source_rgb(1, 1, 1)  # Белый цвет для ручки
        cr.arc(handle_x, radius, handle_radius, 0, 2 * 3.14)
        cr.fill()

    def on_toggle(self, widget, event):
        self.active = not self.active
        self.start_animation()
        self.emit('state-set', self.active)
        self.queue_draw()
        return True

    def start_animation(self):
        if self.animating:
            return

        self.animating = True
        target_progress = 1.0 if self.active else 0.0
        step = 0.05 if target_progress > self.animation_progress else -0.05

        def animate():
            self.animation_progress += step
            if (step > 0 and self.animation_progress >= target_progress) or \
            (step < 0 and self.animation_progress <= target_progress):
                self.animation_progress = target_progress
                self.queue_draw()
                self.animating = False
                return False  # Останавливаем таймер
            self.queue_draw()
            return True  # Продолжаем анимацию

        GLib.timeout_add(16, animate)  # Запускаем анимацию (примерно 60 FPS)