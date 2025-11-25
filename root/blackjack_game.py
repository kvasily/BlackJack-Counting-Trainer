"""
Main Blackjack Game class - ties together all components
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Optional, Tuple

from config import (
    COLORS, RANKS, DEFAULT_NUM_DECKS, DEFAULT_NUM_PLAYERS,
    DEFAULT_TIMER_DURATION, DEFAULT_AUTO_DEAL_DELAY, DEFAULT_AI_SKILL,
    RESHUFFLE_PENETRATION, HILO_VALUES, CARD_WIDTH, CARD_HEIGHT,
    ANIMATION_CARD_DEAL, ANIMATION_CARD_EFFECT, ANIMATION_FLIP_STEP,
    ANIMATION_AI_THINK, ANIMATION_AI_RESULT, ANIMATION_DEALER_DRAW,
    ANIMATION_PLAYER_ACTION, ANIMATION_NEXT_PLAYER,
    ANIMATION_ARC_DURATION, ANIMATION_ARC_STEPS
)
from models import Player, PlayerType, AnimationManager, DeckPosition
from game_logic import (
    create_deck, get_card_value, get_hilo_value,
    calculate_hand_score, calculate_running_count, calculate_true_count,
    get_ai_decision
)
from ui_components import (
    lighten_color, add_hover_effect, create_card_widget, setup_ttk_styles,
    create_card_back_canvas, create_discard_pile_widget
)


class BlackjackGame:
    """Main game controller class"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("♠ PRIVATE CLUB ♠ Blackjack Card Counting Trainer")
        self.root.geometry("1400x900")
        self.root.configure(bg=COLORS['bg_primary'])
        self.root.minsize(1200, 800)
        
        # Game settings (tkinter variables)
        self.num_decks = tk.IntVar(value=DEFAULT_NUM_DECKS)
        self.num_players = tk.IntVar(value=DEFAULT_NUM_PLAYERS)
        self.timer_enabled = tk.BooleanVar(value=False)
        self.timer_duration = tk.IntVar(value=DEFAULT_TIMER_DURATION)
        self.auto_deal_enabled = tk.BooleanVar(value=False)
        self.auto_deal_delay = tk.IntVar(value=DEFAULT_AUTO_DEAL_DELAY)
        self.ai_skill = tk.IntVar(value=DEFAULT_AI_SKILL)
        
        # Visibility toggles
        self.show_running_count = tk.BooleanVar(value=True)
        self.show_true_count = tk.BooleanVar(value=True)
        self.show_discard_tray = tk.BooleanVar(value=True)
        self.show_hilo_chart = tk.BooleanVar(value=True)
        self.training_mode = tk.BooleanVar(value=True)
        
        # Game state
        self.deck = []
        self.discarded_cards = []      # All discarded (for reshuffling)
        self.visible_cards = []         # Only visible cards (for counting)
        self.players: List[Player] = []
        self.dealer_hand = []
        self.dealer_hole_card = None
        self.current_player_index = 0
        self.game_over = False
        self.game_started = False
        self.timer_id = None
        self.time_remaining = 0
        self.auto_deal_id = None
        self.is_paused = False
        
        # Player configurations (type for each slot)
        self.player_types = [tk.StringVar(value="Human") for _ in range(5)]
        
        # Animation manager and deck position
        self.animation = AnimationManager(self)
        self.deck_position = DeckPosition()
        
        # Setup UI
        setup_ttk_styles()
        self._setup_gui()
        self.settings_window = None
        
    # ═══════════════════════════════════════════════════════════════
    # UI SETUP METHODS
    # ═══════════════════════════════════════════════════════════════
    
    def _setup_gui(self):
        """Setup the main GUI layout"""
        self.main_container = tk.Frame(self.root, bg=COLORS['bg_primary'])
        self.main_container.pack(fill='both', expand=True)
        
        self._setup_header()
        
        # Content area
        self.content_frame = tk.Frame(self.main_container, bg=COLORS['bg_primary'])
        self.content_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        # Left side - Game table
        self.game_frame = tk.Frame(self.content_frame, bg=COLORS['bg_card_table'], 
                                   relief='flat', bd=0)
        self.game_frame.pack(side='left', fill='both', expand=True)
        
        self._setup_table_decoration()
        self._setup_counting_panel()
        self._setup_game_table()
        self._setup_controls()
        
    def _setup_header(self):
        """Create the header bar"""
        header_container = tk.Frame(self.main_container, bg=COLORS['bg_secondary'], height=80)
        header_container.pack(fill='x')
        header_container.pack_propagate(False)
        
        # Left section - Settings
        left_section = tk.Frame(header_container, bg=COLORS['bg_secondary'])
        left_section.pack(side='left', padx=20, fill='y')
        
        settings_btn = tk.Button(left_section, text="⚙  SETTINGS", 
                                font=('Trebuchet MS', 10, 'bold'),
                                bg=COLORS['bg_elevated'], fg=COLORS['text_secondary'],
                                relief='flat', cursor='hand2', padx=20, pady=8,
                                activebackground=COLORS['bg_panel'],
                                activeforeground=COLORS['gold'],
                                command=self._show_settings)
        settings_btn.pack(side='left', pady=20)
        add_hover_effect(settings_btn, COLORS['bg_elevated'], COLORS['bg_panel'])
        
        # Center section - Title
        center_section = tk.Frame(header_container, bg=COLORS['bg_secondary'])
        center_section.pack(side='left', expand=True, fill='both')
        
        title_frame = tk.Frame(center_section, bg=COLORS['bg_secondary'])
        title_frame.pack(expand=True)
        
        tk.Label(title_frame, text="♠ ♥", font=('Times New Roman', 20),
                bg=COLORS['bg_secondary'], fg=COLORS['gold_dim']).pack(side='left', padx=10)
        
        tk.Label(title_frame, text="PRIVATE CLUB",
                font=('Palatino Linotype', 26, 'bold'),
                bg=COLORS['bg_secondary'], fg=COLORS['gold']).pack(side='left')
        
        tk.Label(title_frame, text="♦ ♣", font=('Times New Roman', 20),
                bg=COLORS['bg_secondary'], fg=COLORS['gold_dim']).pack(side='left', padx=10)
        
        tk.Label(center_section, text="CARD COUNTING TRAINER",
                font=('Trebuchet MS', 11, 'bold'),
                bg=COLORS['bg_secondary'], fg=COLORS['text_muted']).pack()
        
        # Right section - Info and mode
        right_section = tk.Frame(header_container, bg=COLORS['bg_secondary'])
        right_section.pack(side='right', padx=20, fill='y')
        
        self.deck_info_label = tk.Label(right_section, text="DECK: 52/52",
                                       font=('Consolas', 10),
                                       bg=COLORS['bg_secondary'], fg=COLORS['text_muted'])
        self.deck_info_label.pack(side='top', pady=(15, 5))
        
        self.mode_btn = tk.Button(right_section, text="🎓 TRAINING", 
                                 font=('Trebuchet MS', 10, 'bold'),
                                 bg=COLORS['emerald_dark'], fg=COLORS['text_primary'],
                                 relief='flat', cursor='hand2', padx=15, pady=5,
                                 activebackground=COLORS['emerald'],
                                 command=self._toggle_mode)
        self.mode_btn.pack(side='top', pady=5)
        
    def _setup_table_decoration(self):
        """Add decorative border to game table"""
        glow_frame = tk.Frame(self.game_frame, bg=COLORS['emerald_dark'], bd=0)
        glow_frame.place(relx=0.5, rely=0.5, anchor='center', relwidth=0.98, relheight=0.98)
        
        self.table_inner = tk.Frame(glow_frame, bg=COLORS['bg_card_table'])
        self.table_inner.pack(fill='both', expand=True, padx=3, pady=3)
        
    def _setup_counting_panel(self):
        """Create the counting information panel"""
        panel_container = tk.Frame(self.content_frame, bg=COLORS['bg_secondary'], width=320)
        panel_container.pack(side='right', fill='y', padx=(15, 0))
        panel_container.pack_propagate(False)
        
        self.counting_frame = tk.Frame(panel_container, bg=COLORS['bg_secondary'])
        self.counting_frame.pack(fill='both', expand=True, padx=2, pady=2)
        
        # Panel header
        header = tk.Frame(self.counting_frame, bg=COLORS['bg_panel'], height=50)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        tk.Label(header, text="📊  CARD COUNTING", font=('Trebuchet MS', 13, 'bold'),
                bg=COLORS['bg_panel'], fg=COLORS['gold']).pack(expand=True)
        
        # Stats container
        stats_frame = tk.Frame(self.counting_frame, bg=COLORS['bg_secondary'])
        stats_frame.pack(fill='both', expand=True, pady=10)
        
        # Running Count
        self.running_count_frame = self._create_stat_card(stats_frame, "RUNNING COUNT", "0", COLORS['success'])
        
        # True Count
        self.true_count_frame = self._create_stat_card(stats_frame, "TRUE COUNT", "0.0", COLORS['cyan'])
        
        # Cards remaining
        cards_frame = tk.Frame(stats_frame, bg=COLORS['bg_elevated'], relief='flat')
        cards_frame.pack(fill='x', padx=15, pady=8)
        
        cards_inner = tk.Frame(cards_frame, bg=COLORS['bg_elevated'])
        cards_inner.pack(fill='x', padx=15, pady=12)
        
        tk.Label(cards_inner, text="CARDS REMAINING", font=('Trebuchet MS', 9),
                bg=COLORS['bg_elevated'], fg=COLORS['text_muted']).pack()
        self.cards_remaining_label = tk.Label(cards_inner, text="52",
                                             font=('Consolas', 22, 'bold'),
                                             bg=COLORS['bg_elevated'], fg=COLORS['text_primary'])
        self.cards_remaining_label.pack()
        
        # Hi-Lo Reference Chart
        self.hilo_frame = tk.Frame(stats_frame, bg=COLORS['bg_elevated'])
        self.hilo_frame.pack(fill='x', padx=15, pady=8)
        
        hilo_inner = tk.Frame(self.hilo_frame, bg=COLORS['bg_elevated'])
        hilo_inner.pack(fill='x', padx=15, pady=12)
        
        tk.Label(hilo_inner, text="HI-LO QUICK REFERENCE", font=('Trebuchet MS', 9, 'bold'),
                bg=COLORS['bg_elevated'], fg=COLORS['gold']).pack(pady=(0, 10))
        
        chart = tk.Frame(hilo_inner, bg=COLORS['bg_elevated'])
        chart.pack()
        
        for value, cards, color in [
            ("+1", "2 3 4 5 6", COLORS['success']),
            (" 0", "7 8 9", COLORS['warning']),
            ("-1", "10 J Q K A", COLORS['danger'])
        ]:
            row = tk.Frame(chart, bg=COLORS['bg_elevated'])
            row.pack(fill='x', pady=2)
            tk.Label(row, text=value, font=('Consolas', 11, 'bold'), width=3,
                    bg=COLORS['bg_elevated'], fg=color).pack(side='left')
            tk.Label(row, text="→", font=('Arial', 10),
                    bg=COLORS['bg_elevated'], fg=COLORS['text_muted']).pack(side='left', padx=5)
            tk.Label(row, text=cards, font=('Consolas', 11),
                    bg=COLORS['bg_elevated'], fg=COLORS['text_secondary']).pack(side='left')
        
        # Discard Tray
        self.discard_frame = tk.Frame(stats_frame, bg=COLORS['bg_elevated'])
        self.discard_frame.pack(fill='both', expand=True, padx=15, pady=8)
        
        discard_header = tk.Frame(self.discard_frame, bg=COLORS['bg_elevated'])
        discard_header.pack(fill='x', padx=15, pady=(12, 5))
        
        tk.Label(discard_header, text="DISCARD TRAY", font=('Trebuchet MS', 9, 'bold'),
                bg=COLORS['bg_elevated'], fg=COLORS['gold']).pack()
        
        self.discard_text = tk.Text(self.discard_frame, font=('Consolas', 9),
                                   bg=COLORS['bg_panel'], fg=COLORS['text_secondary'],
                                   height=10, width=30, relief='flat', 
                                   state='disabled', padx=10, pady=10,
                                   selectbackground=COLORS['gold_dim'])
        self.discard_text.pack(padx=15, pady=(0, 12), fill='both', expand=True)
        
        # Toggle section
        toggle_frame = tk.Frame(self.counting_frame, bg=COLORS['bg_panel'])
        toggle_frame.pack(fill='x', side='bottom')
        
        toggle_inner = tk.Frame(toggle_frame, bg=COLORS['bg_panel'])
        toggle_inner.pack(fill='x', padx=15, pady=10)
        
        for text, var in [
            ("Running Count", self.show_running_count),
            ("True Count", self.show_true_count),
            ("Hi-Lo Chart", self.show_hilo_chart),
            ("Discard Tray", self.show_discard_tray)
        ]:
            cb = tk.Checkbutton(toggle_inner, text=text, variable=var,
                               font=('Trebuchet MS', 9), bg=COLORS['bg_panel'],
                               fg=COLORS['text_secondary'], selectcolor=COLORS['bg_elevated'],
                               activebackground=COLORS['bg_panel'],
                               activeforeground=COLORS['text_primary'],
                               command=self._update_counting_visibility)
            cb.pack(anchor='w', pady=1)
            
    def _create_stat_card(self, parent, title, value, color):
        """Create a styled stat display card"""
        frame = tk.Frame(parent, bg=COLORS['bg_elevated'])
        frame.pack(fill='x', padx=15, pady=8)
        
        inner = tk.Frame(frame, bg=COLORS['bg_elevated'])
        inner.pack(fill='x', padx=15, pady=15)
        
        tk.Label(inner, text=title, font=('Trebuchet MS', 9),
                bg=COLORS['bg_elevated'], fg=COLORS['text_muted']).pack()
        
        value_label = tk.Label(inner, text=value,
                              font=('Consolas', 36, 'bold'),
                              bg=COLORS['bg_elevated'], fg=color)
        value_label.pack(pady=(5, 0))
        
        # Store reference for updates
        if 'RUNNING' in title:
            self.running_count_label = value_label
        elif 'TRUE' in title:
            self.true_count_label = value_label
            
        return frame
        
    def _setup_game_table(self):
        """Setup the game table layout"""
        # Top-left: Visual Discard Pile and Deck
        top_section = tk.Frame(self.table_inner, bg=COLORS['bg_card_table'])
        top_section.pack(fill='x', padx=20, pady=(15, 0))
        
        # Discard pile on the left
        self.visual_discard_frame = tk.Frame(top_section, bg=COLORS['bg_card_table'])
        self.visual_discard_frame.pack(side='left', padx=10)
        self._update_visual_discard_pile()
        
        # Deck visual (where cards deal from)
        self.deck_visual_frame = tk.Frame(top_section, bg=COLORS['bg_card_table'])
        self.deck_visual_frame.pack(side='left', padx=20)
        self._create_deck_visual()
        
        # Dealer section
        dealer_section = tk.Frame(self.table_inner, bg=COLORS['bg_card_table'])
        dealer_section.pack(fill='x', pady=(20, 10))
        
        dealer_header = tk.Frame(dealer_section, bg=COLORS['bg_card_table'])
        dealer_header.pack()
        
        tk.Label(dealer_header, text="━━━━━", font=('Arial', 14),
                bg=COLORS['bg_card_table'], fg=COLORS['gold_dim']).pack(side='left')
        tk.Label(dealer_header, text="  DEALER  ", font=('Palatino Linotype', 16, 'bold'),
                bg=COLORS['bg_card_table'], fg=COLORS['gold']).pack(side='left')
        tk.Label(dealer_header, text="━━━━━", font=('Arial', 14),
                bg=COLORS['bg_card_table'], fg=COLORS['gold_dim']).pack(side='left')
        
        # Dealer cards container with fixed background
        self.dealer_cards_container = tk.Frame(dealer_section, bg=COLORS['bg_card_table'])
        self.dealer_cards_container.pack(pady=15)
        
        self.dealer_cards_frame = tk.Frame(self.dealer_cards_container, bg=COLORS['bg_card_table'])
        self.dealer_cards_frame.pack()
        
        self.dealer_score_label = tk.Label(dealer_section, text="",
                                          font=('Trebuchet MS', 13),
                                          bg=COLORS['bg_card_table'], fg=COLORS['text_primary'])
        self.dealer_score_label.pack()
        
        # Divider
        divider_frame = tk.Frame(self.table_inner, bg=COLORS['bg_card_table'])
        divider_frame.pack(fill='x', pady=20)
        
        tk.Frame(divider_frame, bg=COLORS['emerald_dark'], height=2).pack(fill='x', padx=50)
        
        # Players section
        self.players_container = tk.Frame(self.table_inner, bg=COLORS['bg_card_table'])
        self.players_container.pack(fill='both', expand=True, pady=10)
        
        self.player_frames = []
        
    def _create_deck_visual(self):
        """Create the visual deck representation using actual card back widgets"""
        for widget in self.deck_visual_frame.winfo_children():
            widget.destroy()
        
        # Container for stacked cards
        stack_container = tk.Frame(self.deck_visual_frame, bg=COLORS['bg_card_table'])
        stack_container.pack()
        
        # Calculate how many card backs to show based on deck size
        num_visible = min(5, max(1, len(self.deck) // 10))
        
        # Create a canvas to hold the stacked card backs
        stack_offset = 2
        total_width = CARD_WIDTH + (num_visible - 1) * stack_offset + 4
        total_height = CARD_HEIGHT + (num_visible - 1) * stack_offset + 4
        
        # Use a frame to stack actual card back canvases
        for i in range(num_visible):
            # Create actual card back using the same function as dealer cards
            card_back = create_card_back_canvas(stack_container)
            # Position with offset using place for stacking effect
            card_back.place(x=i * stack_offset, y=i * stack_offset)
        
        # Set container size
        stack_container.config(width=total_width, height=total_height)
        stack_container.pack_propagate(False)
        
        # Deck label
        tk.Label(
            self.deck_visual_frame,
            text="DECK",
            font=('Trebuchet MS', 8),
            bg=COLORS['bg_card_table'],
            fg=COLORS['text_muted']
        ).pack(pady=(3, 0))
        
        # Store deck position for animations
        self.deck_visual_frame.update_idletasks()
        
    def _update_visual_discard_pile(self):
        """Update the visual discard pile display"""
        for widget in self.visual_discard_frame.winfo_children():
            widget.destroy()
            
        discard_pile = create_discard_pile_widget(
            self.visual_discard_frame,
            card_count=len(self.discarded_cards)
        )
        discard_pile.pack()
        
    def _setup_controls(self):
        """Setup control buttons"""
        controls_container = tk.Frame(self.main_container, bg=COLORS['bg_secondary'], height=140)
        controls_container.pack(fill='x')
        controls_container.pack_propagate(False)
        
        # Timer bar (hidden initially)
        self.timer_frame = tk.Frame(controls_container, bg=COLORS['bg_secondary'])
        self.timer_frame.pack(fill='x', padx=30, pady=(10, 0))
        
        self.timer_bar = ttk.Progressbar(self.timer_frame, length=500, mode='determinate',
                                        style="Gold.Horizontal.TProgressbar")
        self.timer_bar.pack(side='left', padx=(0, 15))
        
        self.timer_label = tk.Label(self.timer_frame, text="", font=('Consolas', 14, 'bold'),
                                   bg=COLORS['bg_secondary'], fg=COLORS['gold'])
        self.timer_label.pack(side='left')
        
        self.timer_frame.pack_forget()
        
        # Button container
        buttons_frame = tk.Frame(controls_container, bg=COLORS['bg_secondary'])
        buttons_frame.pack(expand=True)
        
        # Action buttons
        action_configs = [
            ("HIT", COLORS['btn_hit'], self._player_hit, "↓"),
            ("STAND", COLORS['btn_stand'], self._player_stand, "✋"),
            ("DOUBLE", COLORS['btn_double'], self._player_double, "2×"),
        ]
        
        self.action_buttons = {}
        
        for i, (text, color, command, icon) in enumerate(action_configs):
            btn_frame = tk.Frame(buttons_frame, bg=COLORS['bg_secondary'])
            btn_frame.grid(row=0, column=i, padx=8, pady=10)
            
            btn = tk.Button(btn_frame, text=f"{icon}\n{text}",
                           font=('Trebuchet MS', 11, 'bold'),
                           bg=color, fg='white',
                           width=10, height=3,
                           relief='flat', cursor='hand2',
                           activebackground=lighten_color(color),
                           command=command)
            btn.pack()
            
            self.action_buttons[text.lower()] = btn
            add_hover_effect(btn, color, lighten_color(color))
        
        # Separator
        tk.Frame(buttons_frame, bg=COLORS['text_muted'], width=2).grid(
            row=0, column=3, padx=15, sticky='ns', pady=15)
        
        # DEAL button
        deal_frame = tk.Frame(buttons_frame, bg=COLORS['bg_secondary'])
        deal_frame.grid(row=0, column=4, padx=8, pady=10)
        
        self.deal_button = tk.Button(deal_frame, text="🃏\nDEAL",
                                    font=('Trebuchet MS', 11, 'bold'),
                                    bg=COLORS['btn_deal'], fg='white',
                                    width=10, height=3,
                                    relief='flat', cursor='hand2',
                                    activebackground=lighten_color(COLORS['btn_deal']),
                                    command=self._deal_new_hand)
        self.deal_button.pack()
        add_hover_effect(self.deal_button, COLORS['btn_deal'], lighten_color(COLORS['btn_deal']))
        
        tk.Label(deal_frame, text="Same Deck", font=('Trebuchet MS', 8),
                bg=COLORS['bg_secondary'], fg=COLORS['text_muted']).pack()
        
        # NEW GAME button
        new_game_frame = tk.Frame(buttons_frame, bg=COLORS['bg_secondary'])
        new_game_frame.grid(row=0, column=5, padx=8, pady=10)
        
        self.new_game_button = tk.Button(new_game_frame, text="🔄\nNEW GAME",
                                        font=('Trebuchet MS', 11, 'bold'),
                                        bg=COLORS['btn_new_game'], fg='white',
                                        width=10, height=3,
                                        relief='flat', cursor='hand2',
                                        activebackground=lighten_color(COLORS['btn_new_game']),
                                        command=self._start_new_game)
        self.new_game_button.pack()
        add_hover_effect(self.new_game_button, COLORS['btn_new_game'], lighten_color(COLORS['btn_new_game']))
        
        tk.Label(new_game_frame, text="Fresh Deck", font=('Trebuchet MS', 8),
                bg=COLORS['bg_secondary'], fg=COLORS['text_muted']).pack()
        
        # PAUSE button
        pause_frame = tk.Frame(buttons_frame, bg=COLORS['bg_secondary'])
        pause_frame.grid(row=0, column=6, padx=8, pady=10)
        
        self.pause_button = tk.Button(pause_frame, text="⏸\nPAUSE",
                                     font=('Trebuchet MS', 11, 'bold'),
                                     bg=COLORS['bg_elevated'], fg='white',
                                     width=10, height=3,
                                     relief='flat', cursor='hand2',
                                     activebackground=lighten_color(COLORS['bg_elevated']),
                                     command=self._toggle_pause)
        self.pause_button.pack()
        add_hover_effect(self.pause_button, COLORS['bg_elevated'], lighten_color(COLORS['bg_elevated']))
        
        # Store references
        self.hit_button = self.action_buttons['hit']
        self.stand_button = self.action_buttons['stand']
        self.double_button = self.action_buttons['double']
        
        # Status label
        self.status_label = tk.Label(controls_container, 
                                    text="♠ ♥ Welcome to the Private Club ♦ ♣",
                                    font=('Palatino Linotype', 14),
                                    bg=COLORS['bg_secondary'], fg=COLORS['gold'])
        self.status_label.pack(pady=(0, 15))
        
    # ═══════════════════════════════════════════════════════════════
    # SETTINGS DIALOG
    # ═══════════════════════════════════════════════════════════════
    
    def _show_settings(self):
        """Show settings dialog"""
        if self.settings_window and self.settings_window.winfo_exists():
            self.settings_window.lift()
            return
            
        self.settings_window = tk.Toplevel(self.root)
        self.settings_window.title("⚙ Game Settings")
        self.settings_window.geometry("500x600")
        self.settings_window.configure(bg=COLORS['bg_primary'])
        self.settings_window.resizable(False, False)
        self.settings_window.transient(self.root)
        
        # Header
        header = tk.Frame(self.settings_window, bg=COLORS['bg_secondary'], height=60)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        tk.Label(header, text="⚙  GAME SETTINGS",
                font=('Palatino Linotype', 18, 'bold'),
                bg=COLORS['bg_secondary'], fg=COLORS['gold']).pack(expand=True)
        
        # Content
        content = tk.Frame(self.settings_window, bg=COLORS['bg_primary'])
        content.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Settings rows
        self._create_setting_row(content, "Number of Decks", self.num_decks, 1, 8)
        self._create_setting_row(content, "Number of Hands", self.num_players, 1, 5,
                               command=self._update_player_config)
        
        # Player configuration
        tk.Label(content, text="PLAYER CONFIGURATION",
                font=('Trebuchet MS', 11, 'bold'),
                bg=COLORS['bg_primary'], fg=COLORS['gold']).pack(fill='x', pady=(20, 10), anchor='w')
        
        self.player_config_frame = tk.Frame(content, bg=COLORS['bg_elevated'])
        self.player_config_frame.pack(fill='x', pady=5)
        self._update_player_config()
        
        # AI Skill slider
        ai_frame = tk.Frame(content, bg=COLORS['bg_primary'])
        ai_frame.pack(fill='x', pady=15)
        
        tk.Label(ai_frame, text="AI Skill Level:", font=('Trebuchet MS', 11),
                bg=COLORS['bg_primary'], fg=COLORS['text_primary']).pack(side='left')
        
        self.ai_skill_label = tk.Label(ai_frame, text=f"{self.ai_skill.get()}%",
                                      font=('Consolas', 11, 'bold'),
                                      bg=COLORS['bg_primary'], fg=COLORS['gold'])
        self.ai_skill_label.pack(side='right')
        
        ai_scale = tk.Scale(ai_frame, from_=0, to=100, orient='horizontal',
                           variable=self.ai_skill, bg=COLORS['bg_elevated'],
                           fg=COLORS['text_primary'], highlightthickness=0,
                           length=200, troughcolor=COLORS['bg_panel'],
                           activebackground=COLORS['gold'],
                           command=lambda v: self.ai_skill_label.config(text=f"{int(float(v))}%"))
        ai_scale.pack(side='right', padx=10)
        
        # Timer settings
        timer_frame = tk.Frame(content, bg=COLORS['bg_primary'])
        timer_frame.pack(fill='x', pady=10)
        
        tk.Checkbutton(timer_frame, text="Enable Turn Timer", variable=self.timer_enabled,
                      font=('Trebuchet MS', 11), bg=COLORS['bg_primary'],
                      fg=COLORS['text_primary'], selectcolor=COLORS['bg_elevated'],
                      activebackground=COLORS['bg_primary']).pack(side='left')
        
        tk.Label(timer_frame, text="sec", font=('Trebuchet MS', 10),
                bg=COLORS['bg_primary'], fg=COLORS['text_muted']).pack(side='right')
        tk.Spinbox(timer_frame, from_=5, to=30, textvariable=self.timer_duration,
                  width=5, font=('Consolas', 11), bg=COLORS['bg_elevated'],
                  fg=COLORS['text_primary']).pack(side='right', padx=5)
        
        # Auto-deal settings
        auto_frame = tk.Frame(content, bg=COLORS['bg_primary'])
        auto_frame.pack(fill='x', pady=10)
        
        tk.Checkbutton(auto_frame, text="Auto-Deal Next Hand", variable=self.auto_deal_enabled,
                      font=('Trebuchet MS', 11), bg=COLORS['bg_primary'],
                      fg=COLORS['text_primary'], selectcolor=COLORS['bg_elevated'],
                      activebackground=COLORS['bg_primary']).pack(side='left')
        
        tk.Label(auto_frame, text="sec delay", font=('Trebuchet MS', 10),
                bg=COLORS['bg_primary'], fg=COLORS['text_muted']).pack(side='right')
        tk.Spinbox(auto_frame, from_=1, to=5, textvariable=self.auto_deal_delay,
                  width=5, font=('Consolas', 11), bg=COLORS['bg_elevated'],
                  fg=COLORS['text_primary']).pack(side='right', padx=5)
        
        # Apply button
        apply_btn = tk.Button(self.settings_window, text="✓  APPLY & START NEW GAME",
                             font=('Trebuchet MS', 13, 'bold'),
                             bg=COLORS['emerald_dark'], fg='white',
                             relief='flat', cursor='hand2', pady=12,
                             activebackground=COLORS['emerald'],
                             command=self._apply_settings)
        apply_btn.pack(fill='x', padx=30, pady=20)
        add_hover_effect(apply_btn, COLORS['emerald_dark'], COLORS['emerald'])
        
    def _create_setting_row(self, parent, label, var, min_val, max_val, command=None):
        """Create a settings row with label and spinbox"""
        frame = tk.Frame(parent, bg=COLORS['bg_primary'])
        frame.pack(fill='x', pady=8)
        
        tk.Label(frame, text=label + ":", font=('Trebuchet MS', 11),
                bg=COLORS['bg_primary'], fg=COLORS['text_primary']).pack(side='left')
        
        tk.Spinbox(frame, from_=min_val, to=max_val, textvariable=var,
                  width=5, font=('Consolas', 11), bg=COLORS['bg_elevated'],
                  fg=COLORS['text_primary'], command=command).pack(side='right')
        
    def _update_player_config(self):
        """Update player configuration UI"""
        for widget in self.player_config_frame.winfo_children():
            widget.destroy()
            
        num = self.num_players.get()
        for i in range(num):
            row = tk.Frame(self.player_config_frame, bg=COLORS['bg_elevated'])
            row.pack(fill='x', padx=15, pady=5)
            
            tk.Label(row, text=f"Hand {i+1}:", font=('Trebuchet MS', 10),
                    bg=COLORS['bg_elevated'], fg=COLORS['text_primary']).pack(side='left', pady=8)
            
            ttk.Combobox(row, textvariable=self.player_types[i],
                        values=["Human", "AI"], state='readonly', width=12).pack(side='right', pady=8, padx=10)
            
    def _apply_settings(self):
        """Apply settings and start new game"""
        if self.settings_window:
            self.settings_window.destroy()
        self._start_new_game()
        
    # ═══════════════════════════════════════════════════════════════
    # VISIBILITY TOGGLES
    # ═══════════════════════════════════════════════════════════════
    
    def _toggle_mode(self):
        """Toggle between training and test mode"""
        self.training_mode.set(not self.training_mode.get())
        if self.training_mode.get():
            self.mode_btn.config(text="🎓 TRAINING", bg=COLORS['emerald_dark'])
            self.show_running_count.set(True)
            self.show_true_count.set(True)
            self.show_hilo_chart.set(True)
            self.show_discard_tray.set(True)
        else:
            self.mode_btn.config(text="📝 TEST MODE", bg=COLORS['danger'])
            self.show_running_count.set(False)
            self.show_true_count.set(False)
            self.show_hilo_chart.set(False)
            self.show_discard_tray.set(False)
        self._update_counting_visibility()
        
    def _update_counting_visibility(self):
        """Update visibility of counting aids"""
        if self.show_running_count.get():
            self.running_count_frame.pack(fill='x', padx=15, pady=8)
        else:
            self.running_count_frame.pack_forget()
            
        if self.show_true_count.get():
            self.true_count_frame.pack(fill='x', padx=15, pady=8)
        else:
            self.true_count_frame.pack_forget()
            
        if self.show_hilo_chart.get():
            self.hilo_frame.pack(fill='x', padx=15, pady=8)
        else:
            self.hilo_frame.pack_forget()
            
        if self.show_discard_tray.get():
            self.discard_frame.pack(fill='both', expand=True, padx=15, pady=8)
        else:
            self.discard_frame.pack_forget()
            
    # ═══════════════════════════════════════════════════════════════
    # CARD MANAGEMENT
    # ═══════════════════════════════════════════════════════════════
    
    def _discard_card(self, card, visible=True):
        """Add card to discard pile"""
        self.discarded_cards.append(card)
        if visible:
            self.visible_cards.append(card)
        # Update visual discard pile
        self._update_visual_discard_pile()
            
    def _reveal_dealer_hole_card(self):
        """Reveal dealer's hole card for counting"""
        if self.dealer_hole_card and self.dealer_hole_card not in self.visible_cards:
            self.visible_cards.append(self.dealer_hole_card)
            self.dealer_hole_card = None
            self._update_counting_display()
            
    def _deal_card(self, to_hand, visible=True):
        """Deal a card to a hand"""
        if len(self.deck) == 0:
            self._shuffle_deck()
        card = self.deck.pop()
        to_hand.append(card)
        self._discard_card(card, visible=visible)
        self._create_deck_visual()  # Update deck visual
        return card
        
    def _deal_dealer_hole_card(self):
        """Deal dealer's hidden hole card"""
        if len(self.deck) == 0:
            self._shuffle_deck()
        card = self.deck.pop()
        self.dealer_hand.append(card)
        self.dealer_hole_card = card
        self._discard_card(card, visible=False)
        self._create_deck_visual()
        return card
        
    def _shuffle_deck(self):
        """Reshuffle the deck"""
        self.deck = create_deck(self.num_decks.get())
        self.discarded_cards = []
        self.visible_cards = []
        self.dealer_hole_card = None
        self._update_visual_discard_pile()
        self._create_deck_visual()
        self.status_label.config(text="🔄 Deck reshuffled!", fg=COLORS['warning'])
        
    # ═══════════════════════════════════════════════════════════════
    # DISPLAY UPDATES
    # ═══════════════════════════════════════════════════════════════
    
    def _update_counting_display(self):
        """Update counting information"""
        running = calculate_running_count(self.visible_cards)
        true = calculate_true_count(running, len(self.deck))
        cards_left = len(self.deck)
        
        # Color code running count
        if running > 0:
            rc_color = COLORS['success']
        elif running < 0:
            rc_color = COLORS['danger']
        else:
            rc_color = COLORS['text_primary']
            
        self.running_count_label.config(text=f"{running:+d}" if running != 0 else "0", fg=rc_color)
        
        # Color code true count
        if true > 0:
            tc_color = COLORS['cyan']
        elif true < 0:
            tc_color = COLORS['warning']
        else:
            tc_color = COLORS['text_primary']
            
        self.true_count_label.config(text=f"{true:+.1f}" if true != 0 else "0.0", fg=tc_color)
        
        self.cards_remaining_label.config(text=str(cards_left))
        
        # Update deck info
        total_cards = self.num_decks.get() * 52
        self.deck_info_label.config(text=f"DECK: {cards_left}/{total_cards}")
        
        self._update_discard_display()
        
    def _update_discard_display(self):
        """Update discard tray display"""
        self.discard_text.config(state='normal')
        self.discard_text.delete('1.0', tk.END)
        
        # Count only visible cards
        rank_counts = {rank: 0 for rank in RANKS}
        for card in self.visible_cards:
            rank_counts[card[0]] += 1
            
        # Header
        self.discard_text.insert(tk.END, "  Card │ Seen │ Hi-Lo\n")
        self.discard_text.insert(tk.END, "  ─────┼──────┼──────\n")
            
        for rank in RANKS:
            count = rank_counts[rank]
            hilo = HILO_VALUES[rank]
            
            if hilo > 0:
                hilo_str = f"+{hilo}"
            elif hilo < 0:
                hilo_str = str(hilo)
            else:
                hilo_str = " 0"
                
            self.discard_text.insert(tk.END, f"  {rank:>3}  │  {count:2d}  │  {hilo_str}\n")
            
        self.discard_text.config(state='disabled')
        
    def _setup_player_frames(self):
        """Setup player display frames"""
        for widget in self.players_container.winfo_children():
            widget.destroy()
        self.player_frames = []
        
        for i, player in enumerate(self.players):
            # Outer frame for glow effect
            glow_frame = tk.Frame(self.players_container, bg=COLORS['player_frame_normal'], 
                                 relief='flat', bd=0)
            glow_frame.pack(side='left', fill='both', expand=True, padx=8, pady=10)
            
            # Main player frame
            frame = tk.Frame(glow_frame, bg=COLORS['player_frame_normal'], relief='flat')
            frame.pack(fill='both', expand=True, padx=3, pady=3)
            
            inner_frame = tk.Frame(frame, bg=COLORS['player_frame_inner'])
            inner_frame.pack(fill='both', expand=True, padx=2, pady=2)
            
            type_icon = "🤖" if player.player_type == PlayerType.AI else "👤"
            header = tk.Label(inner_frame, text=f"{type_icon}  {player.name}",
                            font=('Trebuchet MS', 12, 'bold'),
                            bg=COLORS['player_frame_inner'], fg=COLORS['gold'])
            header.pack(pady=(10, 0))
            
            # Cards frame with FIXED background (isolated from state changes)
            cards_outer = tk.Frame(inner_frame, bg=COLORS['bg_card_table'])
            cards_outer.pack(pady=15, fill='x', padx=10)
            
            cards_frame = tk.Frame(cards_outer, bg=COLORS['bg_card_table'])
            cards_frame.pack(expand=True)
            
            score_label = tk.Label(inner_frame, text="Score: 0",
                                  font=('Trebuchet MS', 12),
                                  bg=COLORS['player_frame_inner'], fg=COLORS['text_primary'])
            score_label.pack()
            
            status_label = tk.Label(inner_frame, text="",
                                   font=('Trebuchet MS', 10, 'italic'),
                                   bg=COLORS['player_frame_inner'], fg=COLORS['text_muted'])
            status_label.pack(pady=(0, 10))
            
            self.player_frames.append({
                'glow_frame': glow_frame,
                'frame': frame,
                'inner_frame': inner_frame,
                'cards_outer': cards_outer,
                'cards_frame': cards_frame,
                'score_label': score_label,
                'status_label': status_label,
                'header': header,
                'player': player
            })
            
    def _update_display(self):
        """Update the entire game display"""
        # Update dealer cards
        for widget in self.dealer_cards_frame.winfo_children():
            widget.destroy()
            
        for i, card in enumerate(self.dealer_hand):
            hidden = (i == 0 and not self.game_over)
            card_widget = create_card_widget(self.dealer_cards_frame, card, hidden=hidden,
                                            training_mode=self.training_mode.get())
            card_widget.pack(side='left', padx=4)
            
        # Dealer score
        if self.game_over:
            dealer_score = calculate_hand_score(self.dealer_hand)
            self.dealer_score_label.config(text=f"Score: {dealer_score}")
        elif len(self.dealer_hand) > 1:
            visible_score = get_card_value(self.dealer_hand[1])
            self.dealer_score_label.config(text=f"Showing: {visible_score}")
        else:
            self.dealer_score_label.config(text="")
            
        # Update player frames
        for pf in self.player_frames:
            player = pf['player']
            cards_frame = pf['cards_frame']
            
            for widget in cards_frame.winfo_children():
                widget.destroy()
                
            card_container = tk.Frame(cards_frame, bg=COLORS['bg_card_table'])
            card_container.pack(expand=True)
            
            for card in player.hand:
                card_widget = create_card_widget(card_container, card,
                                                training_mode=self.training_mode.get())
                card_widget.pack(side='left', padx=3)
                
            # Update score
            score = calculate_hand_score(player.hand)
            pf['score_label'].config(text=f"Score: {score}")
            
            # Update status and apply glow effects
            self._apply_player_visual_state(pf, player)
                
        self._update_counting_display()
        
        # Update button states
        current_player = self.players[self.current_player_index] if self.current_player_index < len(self.players) else None
        is_human_turn = current_player and current_player.player_type == PlayerType.HUMAN and not self.game_over
        
        state = 'normal' if is_human_turn else 'disabled'
        self.hit_button.config(state=state)
        self.stand_button.config(state=state)
        
        can_double = is_human_turn and current_player and len(current_player.hand) == 2
        self.double_button.config(state='normal' if can_double else 'disabled')
        
    def _apply_player_visual_state(self, pf, player):
        """Apply visual state (glow effects) to a player frame"""
        glow_frame = pf['glow_frame']
        frame = pf['frame']
        inner_frame = pf['inner_frame']
        header = pf['header']
        score_label = pf['score_label']
        status_label = pf['status_label']
        
        # Default colors
        glow_color = COLORS['player_frame_normal']
        frame_color = COLORS['player_frame_normal']
        inner_color = COLORS['player_frame_inner']
        
        if player.is_busted:
            # BUST - Red glow effect
            glow_color = COLORS['glow_bust']
            frame_color = COLORS['glow_bust']
            inner_color = '#3d2a2a'  # Dark reddish interior
            status_label.config(text="💥 BUSTED!", fg=COLORS['danger'])
            
        elif player.is_winner:
            # WIN - Gold glow effect
            glow_color = COLORS['glow_win']
            frame_color = COLORS['glow_win']
            inner_color = '#3d3a2a'  # Warm golden interior
            status_label.config(text="🏆 WINNER!", fg=COLORS['gold'])
            
        elif player.is_standing:
            status_label.config(text="✓ Standing", fg=COLORS['success'])
            
        elif self.current_player_index < len(self.players) and \
             self.players[self.current_player_index] == player and not self.game_over:
            # Active player - subtle green glow
            glow_color = COLORS['glow_active']
            frame_color = COLORS['player_frame_active']
            inner_color = COLORS['player_frame_active']
            status_label.config(text="► YOUR TURN", fg=COLORS['gold'])
            
        else:
            status_label.config(text="", fg=COLORS['text_muted'])
        
        # Apply colors
        glow_frame.config(bg=glow_color)
        frame.config(bg=frame_color)
        inner_frame.config(bg=inner_color)
        header.config(bg=inner_color)
        score_label.config(bg=inner_color)
        status_label.config(bg=inner_color)
        
        # Cards area ALWAYS stays table green (isolated from state)
        pf['cards_outer'].config(bg=COLORS['bg_card_table'])
        pf['cards_frame'].config(bg=COLORS['bg_card_table'])
        
    # ═══════════════════════════════════════════════════════════════
    # GAME FLOW
    # ═══════════════════════════════════════════════════════════════
    
    def _cancel_all_timers(self):
        """Cancel all active timers"""
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        if self.auto_deal_id:
            self.root.after_cancel(self.auto_deal_id)
            self.auto_deal_id = None
        self.is_paused = False
        self.pause_button.config(text="⏸\nPAUSE", bg=COLORS['bg_elevated'])
        self.timer_frame.pack_forget()
        
    def _start_new_game(self):
        """Full game reset with fresh deck"""
        self._cancel_all_timers()
        self.animation.cancel_all()
        
        # Full reset
        self.deck = create_deck(self.num_decks.get())
        self.discarded_cards = []
        self.visible_cards = []
        self.dealer_hole_card = None
        
        # Update visuals
        self._update_visual_discard_pile()
        self._create_deck_visual()
        
        self.status_label.config(text="🔄 New game started - Fresh deck shuffled!", fg=COLORS['gold'])
        self.root.after(500, self._begin_dealing)
        
    def _deal_new_hand(self):
        """Deal new hand with same deck"""
        self._cancel_all_timers()
        self.animation.cancel_all()
        
        self.dealer_hole_card = None
        
        # Check if reshuffle needed
        total_cards = self.num_decks.get() * 52
        if len(self.deck) < total_cards * RESHUFFLE_PENETRATION or not self.deck:
            self.deck = create_deck(self.num_decks.get())
            self.discarded_cards = []
            self.visible_cards = []
            self._update_visual_discard_pile()
            self._create_deck_visual()
            self.status_label.config(text="🔀 Deck reshuffled - dealing new hand...", fg=COLORS['warning'])
        else:
            self.status_label.config(text="🃏 Dealing new hand...", fg=COLORS['success'])
            
        self.root.after(300, self._begin_dealing)
        
    def _begin_dealing(self):
        """Initialize hands and begin dealing"""
        self.players = []
        num_players = self.num_players.get()
        
        for i in range(num_players):
            player_type = PlayerType.AI if self.player_types[i].get() == "AI" else PlayerType.HUMAN
            player = Player(
                name=f"Hand {i+1}",
                player_type=player_type,
                hand=[],
                ai_skill=self.ai_skill.get()
            )
            self.players.append(player)
            
        self.dealer_hand = []
        self.current_player_index = 0
        self.game_over = False
        self.game_started = True
        
        self._setup_player_frames()
        self._update_display()
        
        self.animation.set_animating(True)
        self._animate_deal_sequence(0, 0)
        
    def _animate_deal_sequence(self, round_num, player_idx):
        """Animate dealing cards in sequence"""
        if round_num >= 2:
            self._finish_dealing()
            return
            
        if player_idx < len(self.players):
            self._animate_card_deal(self.players[player_idx].hand,
                lambda: self._animate_deal_sequence(round_num, player_idx + 1), visible=True)
        elif player_idx == len(self.players):
            if round_num == 0:
                # First dealer card is hole card (hidden)
                self._animate_dealer_hole_card(
                    lambda: self._animate_deal_sequence(round_num + 1, 0))
            else:
                # Second dealer card is visible
                self._animate_card_deal(self.dealer_hand,
                    lambda: self._animate_deal_sequence(round_num + 1, 0), visible=True)
                    
    def _animate_card_deal(self, target_hand, callback, visible=True):
        """Animate a single card being dealt with arc motion"""
        self.status_label.config(text="🎴 Dealing...", fg=COLORS['cyan'])
        self._deal_card(target_hand, visible=visible)
        self.root.after(ANIMATION_CARD_DEAL, lambda: self._card_dealt_effect(callback))
        
    def _animate_dealer_hole_card(self, callback):
        """Animate dealing dealer's hidden hole card"""
        self.status_label.config(text="🎴 Dealing...", fg=COLORS['cyan'])
        self._deal_dealer_hole_card()
        self.root.after(ANIMATION_CARD_DEAL, lambda: self._card_dealt_effect(callback))
        
    def _card_dealt_effect(self, callback):
        """Visual effect after card is dealt"""
        self._update_display()
        self.root.after(ANIMATION_CARD_EFFECT, callback)
        
    def _finish_dealing(self):
        """Complete dealing and start play"""
        self.animation.set_animating(False)
        self._update_display()
        
        # Check for dealer blackjack
        if calculate_hand_score(self.dealer_hand) == 21:
            self.game_over = True
            self._animate_dealer_reveal(self._handle_dealer_blackjack)
            return
            
        # Check for player blackjacks
        for player in self.players:
            if calculate_hand_score(player.hand) == 21:
                player.is_standing = True
                
        self._find_next_active_player()
        self._update_display()
        self.status_label.config(text="♠ ♥ Cards dealt - Good luck! ♦ ♣", fg=COLORS['success'])
        self._start_player_turn()
        
    def _handle_dealer_blackjack(self):
        """Handle dealer blackjack"""
        self.status_label.config(text="♠ Dealer has Blackjack! ♠", fg=COLORS['danger'])
        self._update_display()
        self._schedule_auto_deal()
        
    def _animate_dealer_reveal(self, callback):
        """Animate dealer hole card reveal"""
        self.status_label.config(text="🔄 Dealer reveals hole card...", fg=COLORS['warning'])
        self.root.after(300, lambda: self._dealer_card_flip_step(0, callback))
        
    def _dealer_card_flip_step(self, step, callback):
        """Animated card flip steps"""
        if step < 3:
            self._update_display()
            self.root.after(ANIMATION_FLIP_STEP, lambda: self._dealer_card_flip_step(step + 1, callback))
        else:
            self._reveal_dealer_hole_card()
            self._update_display()
            self.root.after(300, callback)
            
    def _find_next_active_player(self):
        """Find next player who can act"""
        while self.current_player_index < len(self.players):
            player = self.players[self.current_player_index]
            if not player.is_standing and not player.is_busted:
                return True
            self.current_player_index += 1
        return False
        
    def _start_player_turn(self):
        """Start current player's turn"""
        if self.game_over or self.current_player_index >= len(self.players):
            self._dealer_play()
            return
            
        player = self.players[self.current_player_index]
        
        if player.player_type == PlayerType.AI:
            self.root.after(500, self._ai_play)
        else:
            if self.timer_enabled.get():
                self._start_timer()
            self.status_label.config(text=f"♠ {player.name}'s turn - Hit or Stand? ♠", fg=COLORS['gold'])
            
    def _start_timer(self):
        """Start turn timer"""
        self.time_remaining = self.timer_duration.get()
        self.timer_frame.pack(fill='x', padx=30, pady=(10, 0))
        self.timer_bar['maximum'] = self.timer_duration.get()
        self.timer_bar['value'] = self.time_remaining
        self._update_timer()
        
    def _update_timer(self):
        """Update timer countdown"""
        if self.game_over or self.is_paused:
            return
            
        self.timer_bar['value'] = self.time_remaining
        self.timer_label.config(text=f"⏱ {self.time_remaining}s")
        
        if self.time_remaining <= 5:
            self.timer_label.config(fg=COLORS['danger'])
        else:
            self.timer_label.config(fg=COLORS['gold'])
            
        if self.time_remaining <= 0:
            self.timer_frame.pack_forget()
            self._player_stand()
            return
            
        self.time_remaining -= 1
        self.timer_id = self.root.after(1000, self._update_timer)
        
    # ═══════════════════════════════════════════════════════════════
    # PLAYER ACTIONS
    # ═══════════════════════════════════════════════════════════════
    
    def _player_hit(self):
        """Human player hits"""
        if self.game_over or self.animation.is_animating:
            return
            
        player = self.players[self.current_player_index]
        if player.player_type != PlayerType.HUMAN:
            return
            
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        self.timer_frame.pack_forget()
        
        # Disable buttons during animation
        self.hit_button.config(state='disabled')
        self.stand_button.config(state='disabled')
        self.double_button.config(state='disabled')
        
        self._execute_hit(player)
        self.root.after(ANIMATION_NEXT_PLAYER, lambda: self._after_player_hit(player))
        
    def _execute_hit(self, player):
        """Execute hit action"""
        self.status_label.config(text="🎴 Hit!", fg=COLORS['cyan'])
        self._deal_card(player.hand)
        self._update_display()
        self.root.after(ANIMATION_CARD_EFFECT, lambda: self._check_hit_result(player))
        
    def _check_hit_result(self, player):
        """Check hit result"""
        score = calculate_hand_score(player.hand)
        
        if score > 21:
            player.is_busted = True
            self.status_label.config(text=f"💥 {player.name} busted with {score}!", fg=COLORS['danger'])
        elif score == 21:
            player.is_standing = True
            self.status_label.config(text=f"🎯 {player.name} has 21!", fg=COLORS['success'])
        else:
            self.status_label.config(text=f"📊 {player.name} has {score}", fg=COLORS['text_primary'])
            
        self._update_display()
        
    def _after_player_hit(self, player):
        """Handle state after player hit"""
        if not player.is_busted and not player.is_standing:
            if self.timer_enabled.get():
                self._start_timer()
            self._update_display()
        else:
            self._next_player()
            
    def _player_stand(self):
        """Human player stands"""
        if self.game_over or self.animation.is_animating:
            return
            
        player = self.players[self.current_player_index]
        if player.player_type != PlayerType.HUMAN:
            return
            
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        self.timer_frame.pack_forget()
        
        self.status_label.config(text=f"✋ {player.name} stands", fg=COLORS['info'])
        player.is_standing = True
        self._update_display()
        
        self.root.after(ANIMATION_PLAYER_ACTION, self._next_player)
        
    def _player_double(self):
        """Human player doubles"""
        if self.game_over or self.animation.is_animating:
            return
            
        player = self.players[self.current_player_index]
        if player.player_type != PlayerType.HUMAN or len(player.hand) != 2:
            return
            
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        self.timer_frame.pack_forget()
        
        self.hit_button.config(state='disabled')
        self.stand_button.config(state='disabled')
        self.double_button.config(state='disabled')
        
        self._execute_double(player)
        self.root.after(500, self._next_player)
        
    def _execute_double(self, player):
        """Execute double action"""
        self.status_label.config(text="💰 Double Down!", fg=COLORS['gold'])
        self._deal_card(player.hand)
        player.is_standing = True
        self._update_display()
        self.root.after(ANIMATION_PLAYER_ACTION, lambda: self._check_double_result(player))
        
    def _check_double_result(self, player):
        """Check double result"""
        score = calculate_hand_score(player.hand)
        
        if score > 21:
            player.is_busted = True
            self.status_label.config(text=f"💥 {player.name} doubled and busted!", fg=COLORS['danger'])
        else:
            self.status_label.config(text=f"✨ {player.name} doubled down to {score}!", fg=COLORS['gold'])
            
        self._update_display()
        
    def _next_player(self):
        """Move to next player"""
        self.current_player_index += 1
        
        if not self._find_next_active_player():
            self._dealer_play()
        else:
            self._update_display()
            self._start_player_turn()
            
    # ═══════════════════════════════════════════════════════════════
    # AI PLAYER
    # ═══════════════════════════════════════════════════════════════
    
    def _ai_play(self):
        """AI player makes decision"""
        if self.game_over or self.is_paused:
            return
            
        player = self.players[self.current_player_index]
        if player.player_type != PlayerType.AI:
            return
            
        self.status_label.config(text=f"🤖 {player.name} is thinking...", fg=COLORS['cyan'])
        
        hand_score = calculate_hand_score(player.hand)
        dealer_upcard = get_card_value(self.dealer_hand[1]) if len(self.dealer_hand) > 1 else 10
        decision = get_ai_decision(hand_score, dealer_upcard, len(player.hand), player.ai_skill)
        
        if decision == 'hit':
            self.root.after(ANIMATION_AI_THINK, lambda: self._ai_execute_hit(player))
        elif decision == 'double':
            self.root.after(ANIMATION_AI_THINK, lambda: self._ai_execute_double(player))
        else:
            self.root.after(ANIMATION_AI_THINK, lambda: self._ai_stand(player))
            
    def _ai_execute_hit(self, player):
        """AI executes hit"""
        self.status_label.config(text=f"🤖 {player.name} hits!", fg=COLORS['info'])
        self._deal_card(player.hand)
        self._update_display()
        
        score = calculate_hand_score(player.hand)
        
        def check_result():
            if score > 21:
                player.is_busted = True
                self.status_label.config(text=f"💥 {player.name} busted!", fg=COLORS['danger'])
            elif score == 21:
                player.is_standing = True
                self.status_label.config(text=f"🎯 {player.name} has 21!", fg=COLORS['success'])
            self._update_display()
            
            if not player.is_busted and not player.is_standing:
                self.root.after(ANIMATION_DEALER_DRAW, self._ai_play)
            else:
                self.root.after(ANIMATION_NEXT_PLAYER, self._next_player)
                
        self.root.after(ANIMATION_AI_RESULT, check_result)
        
    def _ai_execute_double(self, player):
        """AI executes double"""
        self.status_label.config(text=f"🤖 {player.name} doubles down!", fg=COLORS['gold'])
        self._deal_card(player.hand)
        player.is_standing = True
        self._update_display()
        
        score = calculate_hand_score(player.hand)
        
        def check_result():
            if score > 21:
                player.is_busted = True
                self.status_label.config(text=f"💥 {player.name} doubled and busted!", fg=COLORS['danger'])
            else:
                self.status_label.config(text=f"✨ {player.name} doubled to {score}!", fg=COLORS['gold'])
            self._update_display()
            self.root.after(ANIMATION_NEXT_PLAYER, self._next_player)
            
        self.root.after(ANIMATION_AI_RESULT, check_result)
        
    def _ai_stand(self, player):
        """AI stands"""
        self.status_label.config(text=f"🤖 {player.name} stands", fg=COLORS['info'])
        player.is_standing = True
        self._update_display()
        self.root.after(ANIMATION_PLAYER_ACTION, self._next_player)
        
    # ═══════════════════════════════════════════════════════════════
    # DEALER PLAY
    # ═══════════════════════════════════════════════════════════════
    
    def _dealer_play(self):
        """Dealer plays hand"""
        self.game_over = True
        all_busted = all(p.is_busted for p in self.players)
        self._animate_dealer_reveal(lambda: self._dealer_draw_sequence(all_busted))
        
    def _dealer_draw_sequence(self, all_busted):
        """Dealer draws cards"""
        if not all_busted and calculate_hand_score(self.dealer_hand) < 17:
            self.status_label.config(text="🎴 Dealer draws...", fg=COLORS['cyan'])
            self._deal_card(self.dealer_hand)
            self._update_display()
            self.root.after(ANIMATION_DEALER_DRAW, lambda: self._dealer_draw_sequence(all_busted))
        else:
            self._update_display()
            self._determine_winners()
            self._schedule_auto_deal()
            
    def _determine_winners(self):
        """Determine winners and apply win glow effects"""
        dealer_score = calculate_hand_score(self.dealer_hand)
        dealer_busted = dealer_score > 21
        
        results = []
        
        for player in self.players:
            player_score = calculate_hand_score(player.hand)
            
            if player.is_busted:
                results.append(f"{player.name}: LOST 💔")
            elif dealer_busted:
                player.is_winner = True
                results.append(f"{player.name}: WON! 🏆")
            elif player_score > dealer_score:
                player.is_winner = True
                results.append(f"{player.name}: WON! 🏆")
            elif player_score < dealer_score:
                results.append(f"{player.name}: LOST 💔")
            else:
                results.append(f"{player.name}: PUSH 🤝")
        
        # Update display to show win/bust glow effects
        self._update_display()
        self.status_label.config(text=" │ ".join(results), fg=COLORS['gold'])
        
    def _schedule_auto_deal(self):
        """Schedule auto-deal"""
        if self.auto_deal_enabled.get() and not self.is_paused:
            delay = self.auto_deal_delay.get() * 1000
            self.auto_deal_id = self.root.after(delay, self._deal_new_hand)
            
    def _toggle_pause(self):
        """Toggle pause state"""
        self.is_paused = not self.is_paused
        
        if self.is_paused:
            self.pause_button.config(text="▶\nRESUME", bg=COLORS['danger'])
            if self.auto_deal_id:
                self.root.after_cancel(self.auto_deal_id)
                self.auto_deal_id = None
        else:
            self.pause_button.config(text="⏸\nPAUSE", bg=COLORS['bg_elevated'])
            if self.game_over and self.auto_deal_enabled.get():
                self._schedule_auto_deal()
            elif not self.game_over:
                self._start_player_turn()
