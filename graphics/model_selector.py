import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib


from config import CONFIG_OPTIONS


class ModelSelectorHandler:
    """
    Создаёт комбобокс для выбора конфигурации модели.
    При изменении выбранной модели вызывается set_configuration у SimulatorHandlers.
    """
    def __init__(self, app, handlers):
        self.app = app
        self.handlers = handlers
        self.combo = Gtk.ComboBoxText()
        for model_name in CONFIG_OPTIONS.keys():
            self.combo.append_text(model_name)
        self.combo.set_active(0)
        self.combo.connect("changed", self.on_model_changed)
        self.handlers.set_configuration(self.combo.get_active_text())

    def on_model_changed(self, widget):
        model_name = widget.get_active_text()
        if model_name:
            self.handlers.set_configuration(model_name)

    def get_widget(self):
        return self.combo