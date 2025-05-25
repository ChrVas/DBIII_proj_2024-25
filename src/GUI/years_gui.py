import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib, Gio
import matplotlib.pyplot as plt
import os
from matplotlib.figure import Figure
from Queries.year_queries import get_yr_stats, get_ctry_yr_stats, get_dist_rgns

class YrDataWndw(Gtk.Window):
    def __init__(self, yr_data, rgn_fltr="All Regions", sts_fltr="All"):
        super().__init__(title=f"Year {yr_data[0]} Statistics")
        self.set_default_size(1280, 720)
        
        v_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        v_box.set_margin_start(12)
        v_box.set_margin_end(12)
        v_box.set_margin_top(12)
        v_box.set_margin_bottom(12)
        
        fltr_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        
        rgn_store = Gtk.ListStore(str)
        rgns = get_dist_rgns()
        rgn_store.append(["All Regions"])
        for rgn in rgns:
            if rgn:
                rgn_store.append([rgn])
        
        self.rgn_cmb = Gtk.ComboBox(model=rgn_store)
        rndr = Gtk.CellRendererText()
        self.rgn_cmb.pack_start(rndr, True)
        self.rgn_cmb.add_attribute(rndr, "text", 0)
        self.rgn_cmb.set_active(0)
        self.rgn_cmb.connect("changed", self.upd_tbl)
        
        sts_store = Gtk.ListStore(str)
        sts_store.append(["All"])
        sts_store.append(["Developed"])
        sts_store.append(["Developing"])
        
        self.sts_cmb = Gtk.ComboBox(model=sts_store)
        rndr = Gtk.CellRendererText()
        self.sts_cmb.pack_start(rndr, True)
        self.sts_cmb.add_attribute(rndr, "text", 0)
        self.sts_cmb.set_active(0)
        self.sts_cmb.connect("changed", self.upd_tbl)
        
        fltr_box.append(Gtk.Label(label="Region:"))
        fltr_box.append(self.rgn_cmb)
        fltr_box.append(Gtk.Label(label="Status:"))
        fltr_box.append(self.sts_cmb)
        
        v_box.append(fltr_box)
        
        scrl_wndw = Gtk.ScrolledWindow()
        scrl_wndw.set_vexpand(True)
        
        self.store = Gtk.ListStore(str, str, str, int, int, int, int)
        self.tree = Gtk.TreeView(model=self.store)
        
        cols = ["Country", "Region", "Status", "Total Matches", "Wins", "Losses", "Draws"]
        for i, col_title in enumerate(cols):
            rndr = Gtk.CellRendererText()
            col = Gtk.TreeViewColumn(col_title, rndr, text=i)
            col.set_sort_column_id(i)
            self.tree.append_column(col)
        
        scrl_wndw.set_child(self.tree)
        v_box.append(scrl_wndw)
        
        self.set_child(v_box)
        
        self.yr = yr_data[0]
        self.curr_data = get_ctry_yr_stats(self.yr)
        self.upd_tbl()
        
    def fltr_data(self):
        if not self.curr_data:
            return []
            
        sel_rgn = "All Regions"
        if self.rgn_cmb.get_active_iter():
            sel_rgn = self.rgn_cmb.get_model()[self.rgn_cmb.get_active_iter()][0]
        
        sel_sts = "All"
        if self.sts_cmb.get_active_iter():
            sel_sts = self.sts_cmb.get_model()[self.sts_cmb.get_active_iter()][0]
        
        fltrd_data = []
        for row in self.curr_data:
            if (sel_rgn == "All Regions" or row[1] == sel_rgn) and (sel_sts == "All" or row[2] == sel_sts):
                fltrd_data.append(row)
        
        return fltrd_data
        
    def upd_tbl(self, widget=None):
        fltrd_data = self.fltr_data()
        self.store.clear()
        for row in fltrd_data:
            self.store.append(row)

class YrsTab:
    def __init__(self, tmp_dir):
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.curr_yr = None
        self.curr_data = None
        self.tmp_dir = tmp_dir
        self.setup_ui()
        
    def setup_ui(self):
        yrs_data = get_yr_stats()
        self.yrs_store = Gtk.ListStore(int, int, int, int)
        for yr, mtchs, drws, shots in yrs_data:
            self.yrs_store.append([int(yr), int(mtchs), int(drws), int(shots)])
        
        yr_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        yr_box.append(Gtk.Label(label="Select Year:"))
        
        self.yr_cmb = Gtk.ComboBox(model=self.yrs_store)
        rndr = Gtk.CellRendererText()
        self.yr_cmb.pack_start(rndr, True)
        self.yr_cmb.add_attribute(rndr, "text", 0)
        self.yr_cmb.connect("changed", self.on_yr_sel)
        yr_box.append(self.yr_cmb)
        
        self.stats_lbl = Gtk.Label()
        self.stats_lbl.set_margin_start(6)
        self.stats_lbl.set_margin_end(6)
        
        self.chrt_cont = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.chrt_cont.set_visible(False)
        
        self.show_tbl_btn = Gtk.Button(label="Show Table")
        self.show_tbl_btn.set_sensitive(False)
        self.show_tbl_btn.connect("clicked", self.on_show_tbl_clicked)
        self.show_tbl_btn.set_margin_top(10)
        self.show_tbl_btn.set_margin_bottom(10)
        self.show_tbl_btn.set_visible(False)
        
        self.box.append(yr_box)
        self.box.append(self.stats_lbl)
        self.box.append(self.chrt_cont)
        self.box.append(self.show_tbl_btn)
        
        self.box.set_margin_start(12)
        self.box.set_margin_end(12)
        self.box.set_margin_top(12)
        self.box.set_margin_bottom(12)
        
    def on_yr_sel(self, combo):
        itr = combo.get_active_iter()
        if itr is not None:
            yr_data = self.yrs_store[itr]
            self.curr_yr_data = yr_data
            yr, mtchs, drws, shots = yr_data
            
            self.stats_lbl.set_markup(
                f"<b>Year {yr} Statistics:</b>\n"
                f"Total Matches: {mtchs}\n"
                f"Draws: {drws}\n"
                f"Matches with Penalty Shootouts: {shots}"
            )
            
            self.chrt_cont.set_visible(True)
            self.show_tbl_btn.set_visible(True)
            self.show_tbl_btn.set_sensitive(True)
            
            self.upd_chrt()
            
    def on_show_tbl_clicked(self, btn):
        if self.curr_yr_data:
            wndw = YrDataWndw(self.curr_yr_data)
            wndw.present()
    
    def upd_chrt(self, widget=None):
        if not self.curr_yr_data:
            return
        while self.chrt_cont.get_first_child():
            self.chrt_cont.remove(self.chrt_cont.get_first_child())
            
        yr_data = get_ctry_yr_stats(self.curr_yr_data[0])
        if not yr_data:
            return
            
        yr_data.sort(key=lambda x: x[3], reverse=True)
        
        plt.figure(figsize=(12, 8))
        
        ctries = [stat[0] for stat in yr_data]
        wns = [stat[4] for stat in yr_data]
        lsss = [stat[5] for stat in yr_data]
        drws = [stat[6] for stat in yr_data]
        
        x = list(range(len(ctries)))
        width = 0.25
        
        wns_pos = [i - width for i in x]
        lsss_pos = x
        drws_pos = [i + width for i in x]
        
        plt.bar(wns_pos, wns, width, label='Wins', color='green')
        plt.bar(lsss_pos, lsss, width, label='Losses', color='red')
        plt.bar(drws_pos, drws, width, label='Draws', color='blue')
        
        plt.ylabel('Number of Matches')
        plt.title(f'Match Statistics by Country ({self.curr_yr_data[0]})')
        plt.xticks(x, ctries, rotation=90)
        plt.legend()
        
        plt.tight_layout()
        
        tmp_file = os.path.join(self.tmp_dir, f'year_{self.curr_yr_data[0]}_plot.png')
        plt.savefig(tmp_file, format='png', dpi=100, bbox_inches='tight')
        plt.close()
        
        img = Gtk.Picture.new_for_file(Gio.File.new_for_path(tmp_file))
        img.set_size_request(900, 600)
        
        self.chrt_cont.append(img)

def create_yr_tab(notebook, tmp_dir):
    yrs_tab = YrsTab(tmp_dir)
    yrs_lbl = Gtk.Label(label="Years")
    notebook.append_page(yrs_tab.box, yrs_lbl)