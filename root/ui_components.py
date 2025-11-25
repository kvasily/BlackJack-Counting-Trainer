"""
UI component creation helpers for the Blackjack game
"""

import tkinter as tk
from tkinter import ttk
import math

from config import (
    COLORS, SUIT_SYMBOLS, HILO_VALUES,
    CARD_WIDTH, CARD_HEIGHT, CARD_CORNER_RADIUS
)
from game_logic import get_hilo_value


def lighten_color(hex_color: str, factor: float = 1.2) -> str:
    """Lighten a hex color by a factor"""
    hex_color = hex_color.lstrip('#')
    r, g, b = int(hex_color[:2], 16), int(hex_color[2:4], 16), int(hex_color[4:], 16)
    r = min(255, int(r * factor))
    g = min(255, int(g * factor))
    b = min(255, int(b * factor))
    return f'#{r:02x}{g:02x}{b:02x}'


def darken_color(hex_color: str, factor: float = 0.8) -> str:
    """Darken a hex color by a factor"""
    hex_color = hex_color.lstrip('#')
    r, g, b = int(hex_color[:2], 16), int(hex_color[2:4], 16), int(hex_color[4:], 16)
    r = max(0, int(r * factor))
    g = max(0, int(g * factor))
    b = max(0, int(b * factor))
    return f'#{r:02x}{g:02x}{b:02x}'


def add_hover_effect(widget, normal_color: str, hover_color: str):
    """Add hover effect to a button widget"""
    def on_enter(e):
        if widget['state'] != 'disabled':
            widget.configure(bg=hover_color)
    def on_leave(e):
        if widget['state'] != 'disabled':
            widget.configure(bg=normal_color)
    widget.bind('<Enter>', on_enter)
    widget.bind('<Leave>', on_leave)


def create_rounded_rect(canvas, x1, y1, x2, y2, radius, **kwargs):
    """Draw a rounded rectangle on a canvas"""
    points = [
        x1 + radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1,
        x1 + radius, y1
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)


def draw_diamond_pattern(canvas, x, y, width, height, pattern_color, spacing=10):
    """Draw a classic diamond/rhombus pattern on the card back, clipped to bounds"""
    # Draw small diamond shapes in a grid pattern (stays within bounds)
    diamond_size = spacing // 2
    
    for row in range(0, height, spacing):
        for col in range(0, width, spacing):
            cx = x + col + spacing // 2
            cy = y + row + spacing // 2
            
            # Only draw if fully within bounds
            if cx - diamond_size >= x and cx + diamond_size <= x + width and \
               cy - diamond_size >= y and cy + diamond_size <= y + height:
                canvas.create_polygon(
                    cx, cy - diamond_size,
                    cx + diamond_size, cy,
                    cx, cy + diamond_size,
                    cx - diamond_size, cy,
                    outline=pattern_color, fill='', width=1
                )


def create_card_back_canvas(parent, width=CARD_WIDTH, height=CARD_HEIGHT):
    """
    Create an elegant card back with diamond pattern using Canvas.
    
    Returns:
        Canvas widget representing card back
    """
    canvas = tk.Canvas(
        parent, 
        width=width, 
        height=height, 
        bg=COLORS['bg_card_table'],
        highlightthickness=0
    )
    
    # Card dimensions (with padding for shadow)
    card_x = 2
    card_y = 2
    card_w = width - 6
    card_h = height - 6
    
    # Card shadow (offset slightly)
    create_rounded_rect(
        canvas, 
        card_x + 2, card_y + 2, 
        card_x + card_w + 2, card_y + card_h + 2,
        CARD_CORNER_RADIUS,
        fill='#1a1512', outline=''
    )
    
    # Main card background - rich burgundy
    create_rounded_rect(
        canvas, 
        card_x, card_y, card_x + card_w, card_y + card_h,
        CARD_CORNER_RADIUS,
        fill=COLORS['card_back'], outline=darken_color(COLORS['card_back'], 0.7), width=1
    )
    
    # Outer decorative border
    border_margin = 5
    create_rounded_rect(
        canvas,
        card_x + border_margin, card_y + border_margin, 
        card_x + card_w - border_margin, card_y + card_h - border_margin,
        CARD_CORNER_RADIUS - 2,
        fill='', outline=COLORS['card_back_pattern'], width=1
    )
    
    # Diamond pattern area (well within card bounds)
    pattern_margin = 12
    pattern_x = card_x + pattern_margin
    pattern_y = card_y + pattern_margin
    pattern_w = card_w - pattern_margin * 2
    pattern_h = card_h - pattern_margin * 2
    
    # Draw the diamond pattern (constrained to inner area)
    draw_diamond_pattern(
        canvas, 
        pattern_x, pattern_y, 
        pattern_w, pattern_h,
        COLORS['card_back_pattern'],
        spacing=12
    )
    
    # Inner decorative border
    inner_margin = 8
    create_rounded_rect(
        canvas,
        card_x + inner_margin, card_y + inner_margin, 
        card_x + card_w - inner_margin, card_y + card_h - inner_margin,
        CARD_CORNER_RADIUS - 2,
        fill='', outline=COLORS['card_back_pattern'], width=1
    )
    
    # Center ornament - small diamond
    center_x = card_x + card_w // 2
    center_y = card_y + card_h // 2
    ornament_size = 6
    canvas.create_polygon(
        center_x, center_y - ornament_size,
        center_x + ornament_size, center_y,
        center_x, center_y + ornament_size,
        center_x - ornament_size, center_y,
        fill=COLORS['card_back_pattern'], outline=''
    )
    
    return canvas


def create_card_front_canvas(parent, card, show_hilo=True, training_mode=True, 
                             width=CARD_WIDTH, height=CARD_HEIGHT):
    """
    Create a classic flat-style card front using Canvas.
    
    Args:
        parent: Parent tkinter widget
        card: Tuple of (rank, suit)
        show_hilo: If True and training_mode, show Hi-Lo value
        training_mode: If True, Hi-Lo values can be shown
        width: Card width in pixels
        height: Card height in pixels
        
    Returns:
        Canvas widget representing card front
    """
    rank, suit = card
    is_red = suit in ['hearts', 'diamonds']
    suit_color = COLORS['card_red'] if is_red else COLORS['card_black']
    suit_symbol = SUIT_SYMBOLS[suit]
    
    canvas = tk.Canvas(
        parent, 
        width=width, 
        height=height, 
        bg=COLORS['bg_card_table'],
        highlightthickness=0
    )
    
    # Card bounds - leave room for shadow
    padding = 3
    shadow_offset = 2
    card_left = padding
    card_top = padding
    card_right = width - padding - shadow_offset
    card_bottom = height - padding - shadow_offset
    card_w = card_right - card_left
    card_h = card_bottom - card_top
    
    # Card shadow
    create_rounded_rect(
        canvas, 
        card_left + shadow_offset, card_top + shadow_offset, 
        card_right + shadow_offset, card_bottom + shadow_offset,
        CARD_CORNER_RADIUS,
        fill='#1a1512', outline=''
    )
    
    # Main card background - warm off-white
    create_rounded_rect(
        canvas, 
        card_left, card_top, card_right, card_bottom,
        CARD_CORNER_RADIUS,
        fill=COLORS['card_face'], outline=COLORS['card_border'], width=1
    )
    
    # Subtle inner border for elegance
    border_inset = 3
    create_rounded_rect(
        canvas,
        card_left + border_inset, card_top + border_inset, 
        card_right - border_inset, card_bottom - border_inset,
        CARD_CORNER_RADIUS - 1,
        fill='', outline='#e5e0d8', width=1
    )
    
    # Calculate center position
    center_x = card_left + card_w // 2
    center_y = card_top + card_h // 2
    
    # Corner text positioning - keep well inside card edges
    corner_inset = 6
    
    # Rank display
    rank_display = rank
    rank_font_size = 9 if rank == '10' else 10
    suit_font_size = 8
    
    # Top-left rank and suit
    canvas.create_text(
        card_left + corner_inset, card_top + corner_inset,
        text=rank_display,
        font=('Georgia', rank_font_size, 'bold'),
        fill=suit_color,
        anchor='nw'
    )
    canvas.create_text(
        card_left + corner_inset + 1, card_top + corner_inset + 13,
        text=suit_symbol,
        font=('Arial', suit_font_size),
        fill=suit_color,
        anchor='nw'
    )
    
    # Bottom-right rank and suit (no rotation - just position at bottom right)
    canvas.create_text(
        card_right - corner_inset, card_bottom - corner_inset - 13,
        text=suit_symbol,
        font=('Arial', suit_font_size),
        fill=suit_color,
        anchor='se'
    )
    canvas.create_text(
        card_right - corner_inset - 1, card_bottom - corner_inset,
        text=rank_display,
        font=('Georgia', rank_font_size, 'bold'),
        fill=suit_color,
        anchor='se'
    )
    
    # Center content - adjust position if hi-lo badge is shown
    center_y_adjust = -5 if (show_hilo and training_mode) else 0
    
    # Center suit/face symbol - use smaller fonts to fit
    if rank in ['J', 'Q', 'K']:
        # Face card - letter and suit
        canvas.create_text(
            center_x, center_y - 5 + center_y_adjust,
            text=rank,
            font=('Georgia', 14, 'bold'),
            fill=suit_color,
            anchor='center'
        )
        canvas.create_text(
            center_x, center_y + 10 + center_y_adjust,
            text=suit_symbol,
            font=('Arial', 12),
            fill=suit_color,
            anchor='center'
        )
    elif rank == 'A':
        # Ace - larger suit
        canvas.create_text(
            center_x, center_y + center_y_adjust,
            text=suit_symbol,
            font=('Arial', 22),
            fill=suit_color,
            anchor='center'
        )
    else:
        # Number card - medium suit
        canvas.create_text(
            center_x, center_y + center_y_adjust,
            text=suit_symbol,
            font=('Arial', 18),
            fill=suit_color,
            anchor='center'
        )
    
    # Hi-Lo indicator (if training mode)
    if show_hilo and training_mode:
        hilo = get_hilo_value(card)
        if hilo > 0:
            hilo_color = COLORS['success']
            hilo_text = f"+{hilo}"
            badge_bg = '#1a3d2a'  # Dark green background
        elif hilo < 0:
            hilo_color = COLORS['danger']
            hilo_text = str(hilo)
            badge_bg = '#3d1a1a'  # Dark red background
        else:
            hilo_color = COLORS['warning']
            hilo_text = "0"
            badge_bg = '#3d3d1a'  # Dark yellow background
        
        # Hi-Lo badge - larger and positioned below center content
        badge_y = card_bottom - 16
        badge_width = 22
        badge_height = 14
        
        # Rounded rectangle badge
        create_rounded_rect(
            canvas,
            center_x - badge_width // 2, badge_y - badge_height // 2,
            center_x + badge_width // 2, badge_y + badge_height // 2,
            4,
            fill=badge_bg, outline=hilo_color, width=1
        )
        canvas.create_text(
            center_x, badge_y,
            text=hilo_text,
            font=('Consolas', 10, 'bold'),
            fill=hilo_color,
            anchor='center'
        )
    
    return canvas


def create_card_widget(parent, card, hidden=False, show_hilo=True, training_mode=True):
    """
    Create a premium card widget using Canvas rendering.
    
    Args:
        parent: Parent tkinter frame
        card: Tuple of (rank, suit)
        hidden: If True, show card back
        show_hilo: If True and training_mode, show Hi-Lo value
        training_mode: If True, Hi-Lo values can be shown
        
    Returns:
        Canvas widget for the card
    """
    if hidden:
        return create_card_back_canvas(parent)
    else:
        return create_card_front_canvas(parent, card, show_hilo, training_mode)


def create_mini_card_back(parent, width=30, height=42):
    """Create a smaller card back for the discard pile display"""
    canvas = tk.Canvas(
        parent,
        width=width,
        height=height,
        bg=COLORS['bg_card_table'],
        highlightthickness=0
    )
    
    # Card dimensions
    card_x = 1
    card_y = 1
    card_w = width - 4
    card_h = height - 4
    
    # Simple card back
    create_rounded_rect(
        canvas,
        card_x, card_y, card_x + card_w, card_y + card_h,
        3,
        fill=COLORS['card_back'], outline=darken_color(COLORS['card_back'], 0.7), width=1
    )
    
    # Simple inner border
    create_rounded_rect(
        canvas,
        card_x + 2, card_y + 2, card_x + card_w - 2, card_y + card_h - 2,
        2,
        fill='', outline=COLORS['card_back_pattern'], width=1
    )
    
    return canvas


def create_discard_pile_widget(parent, card_count=0, max_visible=5):
    """
    Create a stacked discard pile visual with count badge.
    
    Args:
        parent: Parent widget
        card_count: Number of discarded cards
        max_visible: Maximum number of card backs to show in stack
        
    Returns:
        Frame containing the discard pile visual
    """
    frame = tk.Frame(parent, bg=COLORS['bg_card_table'])
    
    # Container for stacked cards
    stack_frame = tk.Frame(frame, bg=COLORS['bg_card_table'])
    stack_frame.pack(pady=5)
    
    # Mini card dimensions
    mini_w = 28
    mini_h = 40
    
    # Calculate how many card backs to show
    visible_cards = min(card_count, max_visible) if card_count > 0 else 0
    
    if visible_cards == 0:
        # Show empty placeholder
        placeholder = tk.Canvas(
            stack_frame,
            width=mini_w + 6,
            height=mini_h + 6,
            bg=COLORS['bg_card_table'],
            highlightthickness=0
        )
        create_rounded_rect(
            placeholder,
            2, 2, mini_w + 2, mini_h + 2,
            3,
            fill='', outline=COLORS['text_muted'], width=1, dash=(3, 3)
        )
        placeholder.pack()
    else:
        # Create stacked card backs with offset
        stack_offset = 2
        canvas_w = mini_w + 6 + (visible_cards - 1) * stack_offset
        canvas_h = mini_h + 6 + (visible_cards - 1) * stack_offset
        
        stack_canvas = tk.Canvas(
            stack_frame,
            width=canvas_w,
            height=canvas_h,
            bg=COLORS['bg_card_table'],
            highlightthickness=0
        )
        stack_canvas.pack()
        
        for i in range(visible_cards):
            offset_x = i * stack_offset
            offset_y = i * stack_offset
            
            # Card shadow
            create_rounded_rect(
                stack_canvas,
                offset_x + 3, offset_y + 3,
                offset_x + mini_w + 3, offset_y + mini_h + 3,
                3,
                fill='#1a1512', outline=''
            )
            
            # Card back
            create_rounded_rect(
                stack_canvas,
                offset_x + 1, offset_y + 1,
                offset_x + mini_w + 1, offset_y + mini_h + 1,
                3,
                fill=COLORS['card_back'], 
                outline=darken_color(COLORS['card_back'], 0.7), 
                width=1
            )
            
            # Inner border
            create_rounded_rect(
                stack_canvas,
                offset_x + 4, offset_y + 4,
                offset_x + mini_w - 2, offset_y + mini_h - 2,
                2,
                fill='', outline=COLORS['card_back_pattern'], width=1
            )
    
    # Count badge
    badge_frame = tk.Frame(frame, bg=COLORS['bg_elevated'], padx=8, pady=2)
    badge_frame.pack(pady=(5, 0))
    
    count_label = tk.Label(
        badge_frame,
        text=f"{card_count}",
        font=('Consolas', 10, 'bold'),
        bg=COLORS['bg_elevated'],
        fg=COLORS['text_primary']
    )
    count_label.pack()
    
    # Label
    tk.Label(
        frame,
        text="DISCARDED",
        font=('Trebuchet MS', 7),
        bg=COLORS['bg_card_table'],
        fg=COLORS['text_muted']
    ).pack(pady=(2, 0))
    
    return frame


def setup_ttk_styles():
    """Configure ttk styles for an elegant appearance"""
    style = ttk.Style()
    style.theme_use('clam')
    
    # Progress bar style - more muted gold
    style.configure("Gold.Horizontal.TProgressbar",
                   troughcolor=COLORS['bg_elevated'],
                   background=COLORS['gold'],
                   bordercolor=COLORS['bg_elevated'],
                   lightcolor=COLORS['gold_light'],
                   darkcolor=COLORS['gold_dim'])
    
    # Combobox style
    style.configure("TCombobox",
                   fieldbackground=COLORS['bg_elevated'],
                   background=COLORS['bg_elevated'],
                   foreground=COLORS['text_primary'])
