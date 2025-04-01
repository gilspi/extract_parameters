import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib


from config import CONFIG_OPTIONS
from graphics.factory.model_selector import ModelSelectorHandler


class GtkModelSelectorHandler(ModelSelectorHandler):
    """
    Реализация селектора модели для GTK
    """
    def __init__(self, app, handlers):
        super().__init__(app, handlers)
        self.combo = self.create_combo()
        self.setup_combo()
        self.handlers.set_configuration(self.get_active_text())

    def create_combo(self) -> Gtk.ComboBoxText:
        return Gtk.ComboBoxText()

    def setup_combo(self) -> None:
        for model_name in CONFIG_OPTIONS.keys():
            self.combo.append_text(model_name)
        self.combo.set_active(0)
        self.combo.connect("changed", self.on_model_changed)

    def get_active_text(self) -> str:
        return self.combo.get_active_text()

    def on_model_changed(self, widget):
        model_name = widget.get_active_text()
        if model_name:
            self.handlers.set_configuration(model_name)

    def get_widget(self):
        return self.combo