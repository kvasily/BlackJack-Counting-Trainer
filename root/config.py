"""
Configuration constants for the Blackjack Card Counting Trainer
"""

# ═══════════════════════════════════════════════════════════════
# ELEGANT PRIVATE CLUB COLOR PALETTE
# ═══════════════════════════════════════════════════════════════
COLORS = {
    # Backgrounds - Dark walnut/espresso tones
    'bg_primary': '#1a1512',       # Deep espresso
    'bg_secondary': '#231e1a',     # Dark walnut
    'bg_card_table': '#2d4a3e',    # Muted forest green felt
    'bg_panel': '#1f1b17',         # Rich dark wood
    'bg_elevated': '#2a2520',      # Elevated walnut surface
    
    # Accents - Cream and ivory instead of bright gold
    'gold': '#d4c4a8',             # Warm ivory/cream
    'gold_light': '#e8dcc8',       # Light cream
    'gold_dim': '#a89880',         # Muted taupe
    'emerald': '#5a7d6a',          # Muted sage green
    'emerald_dark': '#3d5a4a',     # Dark forest
    
    # Status colors - Sophisticated muted tones
    'success': '#6b9b7a',          # Muted sage green
    'danger': '#a85454',           # Muted burgundy red
    'warning': '#c4a35a',          # Antique gold
    'info': '#6a8cad',             # Muted slate blue
    'cyan': '#7a9ea8',             # Dusty teal
    
    # Text - Warm cream tones
    'text_primary': '#f5f0e8',     # Warm cream white
    'text_secondary': '#b8a890',   # Warm taupe
    'text_muted': '#8a7d6d',       # Muted brown
    
    # Cards
    'card_face': '#faf8f3',        # Warm off-white
    'card_back': '#5c2e2e',        # Rich burgundy/maroon
    'card_back_pattern': '#d4c4a8', # Cream diamond pattern
    'card_red': '#8b3a3a',         # Deep burgundy red
    'card_black': '#2a2625',       # Warm charcoal black
    'card_border': '#3d3835',      # Card border color
    
    # Buttons - Elegant muted tones
    'btn_hit': '#4a6a8a',          # Muted slate blue
    'btn_stand': '#8b5a5a',        # Muted burgundy
    'btn_double': '#9a7a4a',       # Antique bronze
    'btn_deal': '#4a6a5a',         # Muted forest
    'btn_new_game': '#8a7a5a',     # Warm bronze
    
    # Glow effects for bust/win
    'glow_bust': '#6b2a2a',        # Deep burgundy glow
    'glow_win': '#8a7a4a',         # Warm gold glow
    'glow_active': '#4a5a4a',      # Subtle green for active player
    
    # Player frame backgrounds
    'player_frame_normal': '#2a3d35',    # Normal player area
    'player_frame_active': '#354a40',    # Active player highlight
    'player_frame_inner': '#324540',     # Inner frame color
}

# ═══════════════════════════════════════════════════════════════
# GAME DEFAULTS
# ═══════════════════════════════════════════════════════════════
DEFAULT_NUM_DECKS = 1
DEFAULT_NUM_PLAYERS = 1
DEFAULT_TIMER_DURATION = 15
DEFAULT_AUTO_DEAL_DELAY = 3
DEFAULT_AI_SKILL = 50

# Reshuffle when deck reaches this penetration
RESHUFFLE_PENETRATION = 0.25

# ═══════════════════════════════════════════════════════════════
# CARD DATA
# ═══════════════════════════════════════════════════════════════
SUITS = ['hearts', 'diamonds', 'clubs', 'spades']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

SUIT_SYMBOLS = {
    'hearts': '♥', 
    'diamonds': '♦', 
    'clubs': '♣', 
    'spades': '♠'
}

# Hi-Lo card counting values
HILO_VALUES = {
    '2': 1, '3': 1, '4': 1, '5': 1, '6': 1,
    '7': 0, '8': 0, '9': 0,
    '10': -1, 'J': -1, 'Q': -1, 'K': -1, 'A': -1
}

# ═══════════════════════════════════════════════════════════════
# ANIMATION TIMING (milliseconds)
# ═══════════════════════════════════════════════════════════════
ANIMATION_CARD_DEAL = 150
ANIMATION_CARD_EFFECT = 200
ANIMATION_FLIP_STEP = 150
ANIMATION_AI_THINK = 400
ANIMATION_AI_RESULT = 300
ANIMATION_DEALER_DRAW = 600
ANIMATION_PLAYER_ACTION = 300
ANIMATION_NEXT_PLAYER = 400

# Arc animation settings
ANIMATION_ARC_DURATION = 450      # Total duration of arc animation (ms)
ANIMATION_ARC_STEPS = 20          # Number of steps in arc animation
ANIMATION_ARC_HEIGHT = 80         # Peak height of arc in pixels

# ═══════════════════════════════════════════════════════════════
# CARD DIMENSIONS
# ═══════════════════════════════════════════════════════════════
CARD_WIDTH = 110
CARD_HEIGHT = 154
CARD_CORNER_RADIUS = 8

