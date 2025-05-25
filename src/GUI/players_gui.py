import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib, Gio
import matplotlib.pyplot as plt
import os
from Queries.player_queries import get_career_stats, get_players, get_player_and_team_stats

class PlayersTab:
    def __init__(self, tmp_dir):
        self.tmp_dir = tmp_dir
        self.b = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.init_ui()
    
    def init_ui(self):
        search_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        
        self.player_combo = Gtk.DropDown.new_from_strings(get_players())
        self.player_combo.set_size_request(300, -1)  
        self.player_combo.connect('notify::selected', self.on_player_changed)
        
        search_box.append(self.player_combo)
        self.b.append(search_box)
        
        self.stats_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.stats_label = Gtk.Label()
        self.stats_box.append(self.stats_label)
        
        self.charts_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.stats_box.append(self.charts_box)
        self.b.append(self.stats_box)
        
        self.stats_box.set_visible(False)
        
        self.b.set_margin_start(12)
        self.b.set_margin_end(12)
        self.b.set_margin_top(12)
        self.b.set_margin_bottom(12)
    
    def on_player_changed(self, dropdown, pspec):
        selected = dropdown.get_selected()
        if selected < 0:  
            return
            
        model = dropdown.get_model()
        player_name = model.get_string(selected)
        if not player_name:
            return
            
        career_stats = get_career_stats(player_name)
        if not career_stats:
            self.stats_label.set_text(f"No data found for player: {player_name}")
            self.stats_box.set_visible(True)
            return
            
        start_year, end_year, total_goals, max_goals = career_stats
        
        
        stats_text = f"""
            Player: {player_name}
            Years in which player scored: {start_year} - {end_year}
            Total goals: {total_goals}
            Max goals in a match: {max_goals}
        """
        self.stats_label.set_text(stats_text)
        
        while self.charts_box.get_first_child():
            self.charts_box.remove(self.charts_box.get_first_child())
        
        yearly_box = self.create_yearly_stats_chart(player_name)
        self.charts_box.append(yearly_box)
        
        self.stats_box.set_visible(True)
    
    def create_yearly_stats_chart(self, player_name):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        yearly_stats = get_player_and_team_stats(player_name)
        if not yearly_stats:
            return box
            
        years = [stat[0] for stat in yearly_stats]
        player_goals = [stat[1] for stat in yearly_stats]
        team_goals = [stat[2] for stat in yearly_stats]
        
        career_stats = get_career_stats(player_name)
        if career_stats:
            fig, ax1 = plt.subplots(figsize=(10, 6))
            
            color1 = 'tab:blue'
            ax1.set_xlabel('Year')
            ax1.set_ylabel('Player Goals', color=color1)
            line1 = ax1.plot(years, player_goals, color=color1, marker='o', linestyle='-', label='Player Goals')
            ax1.tick_params(axis='y', labelcolor=color1)
            
            ax2 = ax1.twinx()
            color2 = 'tab:red'
            ax2.set_ylabel('Team Goals per Match', color=color2)
            line2 = ax2.plot(years, team_goals, color=color2, marker='s', linestyle='--', label='Team Goals/Match')
            ax2.tick_params(axis='y', labelcolor=color2)
            
            plt.title(f"Goals per Year")
            ax1.set_xticks(years)
            ax1.set_xticklabels(years, rotation=90)
            ax1.grid(True, linestyle='--', alpha=0.7)
            
            lines = line1 + line2
            labels = [l.get_label() for l in lines]
            ax1.legend(lines, labels, loc='upper right')
            
            plt.tight_layout()
            
            tmp_file = os.path.join(self.tmp_dir, f'player_stats_{player_name}.png')
            plt.savefig(tmp_file, format='png', dpi=100, bbox_inches='tight')
            plt.close()
            
            img = Gtk.Picture.new_for_file(Gio.File.new_for_path(tmp_file))
            img.set_size_request(800, 800)
            box.append(img)
        
        return box

def create_plyr_tab(notebook, tmp_dir):
    players_tab = PlayersTab(tmp_dir)
    players_label = Gtk.Label(label="Players")
    notebook.append_page(players_tab.b, players_label)