import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib, Gio
import matplotlib.pyplot as plt
import os
from Queries.overall_stat_queries import country_scores, top_10

class StatsTab:
    def __init__(self, tmp_dir):
        self.tmp_dir = tmp_dir
        self.b = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.init_ui()
    
    def init_ui(self):
        self.chrt_ntbk = Gtk.Notebook()
        self.b.append(self.chrt_ntbk)
        
        chrt_cfg = [
            ('wins', 'Total Wins'),
            ('score', 'Total Score'),
            ('wins_per_year', 'Wins per Year'),
            ('score_per_year', 'Score per Year')
        ]
        
        for cat, ttl in chrt_cfg:
            chrt_box = self.create_top_10_chart(cat, f'Top 10 Countries by {ttl}')
            chrt_lbl = Gtk.Label(label=ttl)
            self.chrt_ntbk.append_page(chrt_box, chrt_lbl)
        
        corr_box = self.create_sct_plots()
        corr_lbl = Gtk.Label(label="Scatter Plot Wins X Population")
        self.chrt_ntbk.append_page(corr_box, corr_lbl)
        
        self.b.set_margin_start(12)
        self.b.set_margin_end(12)
        self.b.set_margin_top(12)
        self.b.set_margin_bottom(12)

    def create_top_10_chart(self, cat, ttl):
        b = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        d = top_10(cat)
        nms = [row[0] for row in d]
        vals = [row[1] for row in d]
        
        bars = ax.bar(nms, vals)
        ax.set_title(ttl)
        ax.tick_params(axis='x', rotation=45)
        
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., h,
                    f'{h:.1f}',
                    ha='center', va='bottom')
        
        plt.tight_layout()
        
        tmp_f = os.path.join(self.tmp_dir, f'top10_{cat}.png')
        plt.savefig(tmp_f, format='png', dpi=100, bbox_inches='tight')
        plt.close()
        
        img = Gtk.Picture.new_for_file(Gio.File.new_for_path(tmp_f))
        img.set_size_request(800, 400)
        b.append(img)
        
        return b

    def create_sct_plots(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        data = country_scores()
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        populations = [row[2] for row in data]
        wins = [row[1] for row in data]
        
        ax.scatter(populations, wins)
        ax.set_xlabel('Population')
        ax.set_ylabel('Total Wins')
        ax.set_title('Wins vs Population')
        
        plt.tight_layout()
        
        tmp_f = os.path.join(self.tmp_dir, 'correlations.png')
        plt.savefig(tmp_f, format='png', dpi=100, bbox_inches='tight')
        plt.close()
        
        img = Gtk.Picture.new_for_file(Gio.File.new_for_path(tmp_f))
        img.set_size_request(800, 600)
        box.append(img)
        
        return box

def create_stats_tab(ntbk, tmp_dir):
    stats_tab = StatsTab(tmp_dir)
    stats_lbl = Gtk.Label(label="Overall Stats")
    ntbk.append_page(stats_tab.b, stats_lbl)