import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
import tempfile
from GUI.countries_gui import create_ctry_tab
from GUI.years_gui import create_yr_tab
from GUI.overall_stats_gui import create_stats_tab
from GUI.players_gui import create_plyr_tab

class WndwMain(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)
        self.set_title("MYE030 Project - AM:4861")
        self.set_default_size(1280, 720)
        
        scrl_wndw = Gtk.ScrolledWindow()
        self.set_child(scrl_wndw)
        
        v_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        scrl_wndw.set_child(v_box)
        
        ntbk = Gtk.Notebook()
        v_box.append(ntbk)
        
        self.tmp_dir = tempfile.mkdtemp()
        
        create_ctry_tab(ntbk, self.tmp_dir)
        create_yr_tab(ntbk, self.tmp_dir)
        create_stats_tab(ntbk, self.tmp_dir)
        create_plyr_tab(ntbk, self.tmp_dir)

class AppMain(Gtk.Application):
    def __init__(self):
        super().__init__(application_id='org.mye030.project')
        self.connect('activate', self.on_actv)

    def on_actv(self, app):
        w = WndwMain(app)
        w.present()

def init_app():
    app = AppMain()
    return app.run(None)