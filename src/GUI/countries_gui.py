import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gio, GObject
import matplotlib.pyplot as plt
import os
from Queries.country_queries import (
    get_ctry_yr_rng,
    get_ctry_stats,
    get_all_ctry,
    get_ctry_yr_info,
    get_ctry_yrly_stats
)

class CtryDataWndw(Gtk.Window):
    def __init__(self, ctry_name):
        super().__init__(title=f"{ctry_name} Table")
        self.set_default_size(1280, 720)
        
        m_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.set_child(m_box)
        
        flt_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        flt_box.set_margin_start(10)
        flt_box.set_margin_end(10)
        flt_box.set_margin_top(10)
        
        yr_range = get_ctry_yr_rng(ctry_name)
        
        st_yr_lbl = Gtk.Label(label="Start Year:")
        self.st_yr_entry = Gtk.Entry()
        self.st_yr_entry.set_text(str(yr_range['min_year']))
        
        end_yr_lbl = Gtk.Label(label="End Year:")
        self.end_yr_entry = Gtk.Entry()
        self.end_yr_entry.set_text(str(yr_range['max_year']))
        
        apply_btn = Gtk.Button(label="Apply")
        apply_btn.connect('clicked', self.on_flt_apply, ctry_name)
        
        flt_box.append(st_yr_lbl)
        flt_box.append(self.st_yr_entry)
        flt_box.append(end_yr_lbl)
        flt_box.append(self.end_yr_entry)
        flt_box.append(apply_btn)
        
        scrl = Gtk.ScrolledWindow()
        scrl.set_margin_start(10)
        scrl.set_margin_end(10)
        scrl.set_margin_top(10)
        scrl.set_margin_bottom(10)
        scrl.set_vexpand(True)
        
        self.col_names = ['Year', 'Matches', 'Wins', 'Losses', 'Draws', 'Home Matches', 'Home Wins', 'Home Losses', 'Away Matches', 'Away Wins', 'Away Losses']
        self.lst_store = Gtk.ListStore(*[str] * len(self.col_names))
        
        self.tree_v = Gtk.TreeView(model=self.lst_store)
        for i, title in enumerate(self.col_names):
            rnd = Gtk.CellRendererText()
            col = Gtk.TreeViewColumn(title, rnd, text=i)
            col.set_resizable(True)
            col.set_sort_column_id(i)
            self.tree_v.append_column(col)
        
        scrl.set_child(self.tree_v)
        
        m_box.append(flt_box)
        m_box.append(scrl)
        
        self.load_d(ctry_name)
    
    def load_d(self, ctry_name, st_yr=None, end_yr=None):
        results = get_ctry_stats(ctry_name, st_yr, end_yr)
        self.lst_store.clear()
        for row in results:
            self.lst_store.append([str(x) for x in row])
    
    def on_flt_apply(self, btn, ctry_name):
        try:
            st_yr = int(self.st_yr_entry.get_text())
            end_yr = int(self.end_yr_entry.get_text())
            self.load_d(ctry_name, st_yr, end_yr)
        except ValueError:
            print("Please enter valid year numbers")

def create_ln_chrt(ctry_name, chrt_cont, tmp_dir):
    while chrt_cont.get_first_child():
        chrt_cont.remove(chrt_cont.get_first_child())
    
    yrly_stats = get_ctry_yrly_stats(ctry_name)
    if not yrly_stats:
        return
    
    chrt_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    
    plt.figure(figsize=(12, 6))
    
    plt.plot(yrly_stats['years'], yrly_stats['matches'], label='Matches')
    plt.plot(yrly_stats['years'], yrly_stats['wins'], label='Wins')
    plt.plot(yrly_stats['years'], yrly_stats['losses'], label='Losses')
    plt.plot(yrly_stats['years'], yrly_stats['draws'], label='Draws')
    
    plt.title(f'Yearly Statistics for {ctry_name}')
    plt.xlabel('Year')
    plt.ylabel('Count')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    
    plt.xticks(yrly_stats['years'], rotation=90)
    plt.tight_layout()
    
    tmp_file = os.path.join(tmp_dir, f'{ctry_name.replace(" ", "_")}_plot.png')
    plt.savefig(tmp_file, format='png', dpi=100)
    plt.close()
    
    img = Gtk.Picture.new_for_file(Gio.File.new_for_path(tmp_file))
    img.set_size_request(900, 400)
    
    chrt_box.append(img)
    
    dtls_btn = Gtk.Button(label="Show Table")
    dtls_btn.set_margin_top(10)
    dtls_btn.set_margin_bottom(10)
    dtls_btn.connect('clicked', lambda btn: CtryDataWndw(ctry_name).present())
    chrt_box.append(dtls_btn)
    
    chrt_cont.append(chrt_box)

def on_ctry_chg(drpdwn, pspec, yrs_lbl, chrt_cont, tmp_dir):
    sel = drpdwn.get_selected()
    mdl = drpdwn.get_model()
    if sel >= 0:
        ctry_name = mdl.get_string(sel)
        yrs_info = get_ctry_yr_info(ctry_name)
        yrs_txt = (
            f"Participated from {yrs_info['first_year']} to {yrs_info['last_year']}\n"
            f"Total years of participation: {yrs_info['total_years']}\n\n"
            f"Stats:\n"
            f"Total matches played: {yrs_info['total_matches']}\n"
            f"Total wins: {yrs_info['total_wins']}\n"
            f"Total losses: {yrs_info['total_losses']}\n\n"
            f"Home Statistics:\n"
            f"Home matches: {yrs_info['total_home_matches']}\n"
            f"Home wins: {yrs_info['total_home_wins']}\n"
            f"Home losses: {yrs_info['total_home_losses']}\n\n"
            f"Away Statistics:\n"
            f"Away matches: {yrs_info['total_away_matches']}\n"
            f"Away wins: {yrs_info['total_away_wins']}\n"
            f"Away losses: {yrs_info['total_away_losses']}"
        )
        yrs_lbl.set_text(yrs_txt)
        create_ln_chrt(ctry_name, chrt_cont, tmp_dir)

def create_ctry_tab(notebook, tmp_dir):
    ctry_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    ctry_lbl = Gtk.Label()
    ctry_lbl.set_label("Countries")
    
    ctry_drpdwn = Gtk.DropDown.new_from_strings(get_all_ctry())
    ctry_drpdwn.set_margin_start(10)
    ctry_drpdwn.set_margin_end(10)
    ctry_drpdwn.set_margin_top(10)
    
    yrs_info_lbl = Gtk.Label()
    yrs_info_lbl.set_margin_start(10)
    yrs_info_lbl.set_margin_end(10)
    yrs_info_lbl.set_margin_top(10)
    
    chrt_cont = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    chrt_cont.set_margin_start(10)
    chrt_cont.set_margin_end(10)
    chrt_cont.set_margin_top(10)
    
    ctry_drpdwn.connect('notify::selected', on_ctry_chg, yrs_info_lbl, chrt_cont, tmp_dir)
    
    ctry_box.append(ctry_drpdwn)
    ctry_box.append(yrs_info_lbl)
    ctry_box.append(chrt_cont)
    
    notebook.append_page(ctry_box, ctry_lbl)