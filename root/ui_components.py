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
    
    # Card bounds - same as front card for consistency
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
    
    # Main card background - rich burgundy
    create_rounded_rect(
        canvas, 
        card_left, card_top, card_right, card_bottom,
        CARD_CORNER_RADIUS,
        fill=COLORS['card_back'], outline=darken_color(COLORS['card_back'], 0.7), width=2
    )
    
    # Outer decorative border
    border_margin = 8
    inner_left = card_left + border_margin
    inner_top = card_top + border_margin
    inner_right = card_right - border_margin
    inner_bottom = card_bottom - border_margin
    
    create_rounded_rect(
        canvas,
        inner_left, inner_top, inner_right, inner_bottom,
        CARD_CORNER_RADIUS - 3,
        fill='', outline=COLORS['card_back_pattern'], width=2
    )
    
    # Inner area for pattern
    pattern_margin = 12
    pattern_left = card_left + pattern_margin
    pattern_top = card_top + pattern_margin
    pattern_right = card_right - pattern_margin
    pattern_bottom = card_bottom - pattern_margin
    pattern_w = pattern_right - pattern_left
    pattern_h = pattern_bottom - pattern_top
    
    # Draw crosshatch/diamond pattern using lines
    line_spacing = 12
    pattern_color = COLORS['card_back_pattern']
    
    # Diagonal lines from top-left to bottom-right
    for i in range(-int(pattern_h), int(pattern_w) + int(pattern_h), line_spacing):
        x1 = pattern_left + i
        y1 = pattern_top
        x2 = pattern_left + i + pattern_h
        y2 = pattern_bottom
        
        # Clip to pattern bounds
        if x1 < pattern_left:
            y1 = pattern_top + (pattern_left - x1)
            x1 = pattern_left
        if x2 > pattern_right:
            y2 = pattern_bottom - (x2 - pattern_right)
            x2 = pattern_right
        if y1 < pattern_top or y2 > pattern_bottom:
            continue
        if x1 <= pattern_right and x2 >= pattern_left:
            canvas.create_line(x1, y1, x2, y2, fill=pattern_color, width=1)
    
    # Diagonal lines from top-right to bottom-left
    for i in range(-int(pattern_h), int(pattern_w) + int(pattern_h), line_spacing):
        x1 = pattern_right - i
        y1 = pattern_top
        x2 = pattern_right - i - pattern_h
        y2 = pattern_bottom
        
        # Clip to pattern bounds
        if x1 > pattern_right:
            y1 = pattern_top + (x1 - pattern_right)
            x1 = pattern_right
        if x2 < pattern_left:
            y2 = pattern_bottom - (pattern_left - x2)
            x2 = pattern_left
        if y1 < pattern_top or y2 > pattern_bottom:
            continue
        if x1 >= pattern_left and x2 <= pattern_right:
            canvas.create_line(x1, y1, x2, y2, fill=pattern_color, width=1)
    
    # Inner decorative border (covers pattern edges)
    create_rounded_rect(
        canvas,
        inner_left, inner_top, inner_right, inner_bottom,
        CARD_CORNER_RADIUS - 3,
        fill='', outline=COLORS['card_back_pattern'], width=2
    )
    
    # Center ornament - larger diamond with fill
    center_x = card_left + card_w // 2
    center_y = card_top + card_h // 2
    ornament_size = 10
    
    # Diamond background
    canvas.create_polygon(
        center_x, center_y - ornament_size - 2,
        center_x + ornament_size + 2, center_y,
        center_x, center_y + ornament_size + 2,
        center_x - ornament_size - 2, center_y,
        fill=COLORS['card_back'], outline=''
    )
    # Diamond outline
    canvas.create_polygon(
        center_x, center_y - ornament_size,
        center_x + ornament_size, center_y,
        center_x, center_y + ornament_size,
        center_x - ornament_size, center_y,
        fill=COLORS['card_back_pattern'], outline=darken_color(COLORS['card_back_pattern'], 0.8), width=1
    )
    
    return canvas


def _draw_card_pips(canvas, rank, suit_symbol, suit_color, card_x, card_y, card_w, card_h):
    """
    Draw traditional playing card pip patterns.
    
    Args:
        canvas: The canvas to draw on
        rank: Card rank (2-10, J, Q, K, A)
        suit_symbol: The suit symbol character
        suit_color: Color for the pips
        card_x, card_y: Top-left corner of card content area
        card_w, card_h: Width and height of card content area
    """
    # Define the pip area (leaving room for corner numbers)
    # More generous margins to avoid overlap with corner text
    pip_area_top = card_y + card_h * 0.28
    pip_area_bottom = card_y + card_h * 0.72
    pip_area_left = card_x + card_w * 0.22
    pip_area_right = card_x + card_w * 0.78
    
    pip_area_h = pip_area_bottom - pip_area_top
    pip_area_w = pip_area_right - pip_area_left
    
    # Column positions (left, center, right)
    left_x = pip_area_left
    center_x = card_x + card_w // 2
    right_x = pip_area_right
    
    # Row positions within pip area
    top_y = pip_area_top
    row_2 = pip_area_top + pip_area_h * 0.25
    mid_y = pip_area_top + pip_area_h * 0.5
    row_4 = pip_area_top + pip_area_h * 0.75
    bottom_y = pip_area_bottom
    
    # Pip font size - scaled for larger cards
    pip_font = ('Arial', 13)
    pip_font_large = ('Arial', 28)
    pip_font_face = ('Georgia', 20, 'bold')
    
    def draw_pip(x, y, inverted=False, font=pip_font):
        """Draw a single pip, optionally inverted"""
        canvas.create_text(x, y, text=suit_symbol, font=font, 
                          fill=suit_color, anchor='center', 
                          angle=180 if inverted else 0)
    
    if rank == 'A':
        # Ace - one large center pip
        draw_pip(center_x, card_y + card_h // 2, font=pip_font_large)
        
    elif rank == '2':
        # Two pips - top and bottom center
        draw_pip(center_x, top_y)
        draw_pip(center_x, bottom_y, inverted=True)
        
    elif rank == '3':
        # Three pips - column of three
        draw_pip(center_x, top_y)
        draw_pip(center_x, mid_y)
        draw_pip(center_x, bottom_y, inverted=True)
        
    elif rank == '4':
        # Four pips - corners of pip area
        draw_pip(left_x, top_y)
        draw_pip(right_x, top_y)
        draw_pip(left_x, bottom_y, inverted=True)
        draw_pip(right_x, bottom_y, inverted=True)
        
    elif rank == '5':
        # Five pips - corners plus center
        draw_pip(left_x, top_y)
        draw_pip(right_x, top_y)
        draw_pip(center_x, mid_y)
        draw_pip(left_x, bottom_y, inverted=True)
        draw_pip(right_x, bottom_y, inverted=True)
        
    elif rank == '6':
        # Six pips - two columns of three
        draw_pip(left_x, top_y)
        draw_pip(right_x, top_y)
        draw_pip(left_x, mid_y)
        draw_pip(right_x, mid_y)
        draw_pip(left_x, bottom_y, inverted=True)
        draw_pip(right_x, bottom_y, inverted=True)
        
    elif rank == '7':
        # Seven pips - six in grid plus one upper center
        draw_pip(left_x, top_y)
        draw_pip(right_x, top_y)
        draw_pip(center_x, row_2)
        draw_pip(left_x, mid_y)
        draw_pip(right_x, mid_y)
        draw_pip(left_x, bottom_y, inverted=True)
        draw_pip(right_x, bottom_y, inverted=True)
        
    elif rank == '8':
        # Eight pips - six in grid plus two center
        draw_pip(left_x, top_y)
        draw_pip(right_x, top_y)
        draw_pip(center_x, row_2)
        draw_pip(left_x, mid_y)
        draw_pip(right_x, mid_y)
        draw_pip(center_x, row_4, inverted=True)
        draw_pip(left_x, bottom_y, inverted=True)
        draw_pip(right_x, bottom_y, inverted=True)
        
    elif rank == '9':
        # Nine pips - 4-1-4 pattern
        third_h = pip_area_h / 3
        draw_pip(left_x, top_y)
        draw_pip(right_x, top_y)
        draw_pip(left_x, top_y + third_h)
        draw_pip(right_x, top_y + third_h)
        draw_pip(center_x, mid_y)
        draw_pip(left_x, bottom_y - third_h, inverted=True)
        draw_pip(right_x, bottom_y - third_h, inverted=True)
        draw_pip(left_x, bottom_y, inverted=True)
        draw_pip(right_x, bottom_y, inverted=True)
        
    elif rank == '10':
        # Ten pips - 4-2-4 pattern
        third_h = pip_area_h / 3
        draw_pip(left_x, top_y)
        draw_pip(right_x, top_y)
        draw_pip(center_x, top_y + third_h * 0.5)
        draw_pip(left_x, top_y + third_h)
        draw_pip(right_x, top_y + third_h)
        draw_pip(left_x, bottom_y - third_h, inverted=True)
        draw_pip(right_x, bottom_y - third_h, inverted=True)
        draw_pip(center_x, bottom_y - third_h * 0.5, inverted=True)
        draw_pip(left_x, bottom_y, inverted=True)
        draw_pip(right_x, bottom_y, inverted=True)
        
    elif rank in ['J', 'Q', 'K']:
        # Face cards - letter with suit
        face_center_y = card_y + card_h // 2
        canvas.create_text(
            center_x, face_center_y - 8,
            text=rank,
            font=pip_font_face,
            fill=suit_color,
            anchor='center'
        )
        canvas.create_text(
            center_x, face_center_y + 16,
            text=suit_symbol,
            font=('Arial', 16),
            fill=suit_color,
            anchor='center'
        )


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
    
    # Corner text positioning - scaled for larger cards
    corner_x = 13  # Distance from left/right edge to center of text
    corner_y = 15  # Distance from top/bottom edge to center of text
    
    # Rank display - larger fonts for bigger cards
    rank_display = rank
    rank_font_size = 11 if rank == '10' else 13
    suit_font_size = 10
    
    # Determine if we should show corner suits (only for A, J, Q, K)
    show_corner_suits = rank in ['A', 'J', 'Q', 'K']
    
    # Top-left corner
    canvas.create_text(
        card_left + corner_x, card_top + corner_y,
        text=rank_display,
        font=('Arial', rank_font_size, 'bold'),
        fill=suit_color,
        anchor='center'
    )
    if show_corner_suits:
        canvas.create_text(
            card_left + corner_x, card_top + corner_y + 13,
            text=suit_symbol,
            font=('Arial', suit_font_size),
            fill=suit_color,
            anchor='center'
        )
    
    # Bottom-right corner
    if show_corner_suits:
        canvas.create_text(
            card_right - corner_x, card_bottom - corner_y - 13,
            text=suit_symbol,
            font=('Arial', suit_font_size),
            fill=suit_color,
            anchor='center'
        )
    canvas.create_text(
        card_right - corner_x, card_bottom - corner_y,
        text=rank_display,
        font=('Arial', rank_font_size, 'bold'),
        fill=suit_color,
        anchor='center'
    )
    
    # Draw pips based on card rank - traditional playing card layout
    _draw_card_pips(canvas, rank, suit_symbol, suit_color, 
                   card_left, card_top, card_w, card_h)
    
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
        
        # Hi-Lo badge - scaled for larger cards
        badge_y = card_bottom - 18
        badge_width = 28
        badge_height = 18
        
        # Rounded rectangle badge
        create_rounded_rect(
            canvas,
            center_x - badge_width // 2, badge_y - badge_height // 2,
            center_x + badge_width // 2, badge_y + badge_height // 2,
            5,
            fill=badge_bg, outline=hilo_color, width=1
        )
        canvas.create_text(
            center_x, badge_y,
            text=hilo_text,
            font=('Consolas', 11, 'bold'),
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
