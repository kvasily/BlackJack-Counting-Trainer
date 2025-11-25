"""
Data models for the Blackjack Card Counting Trainer
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Callable, Optional
from enum import Enum
import math

from config import ANIMATION_ARC_DURATION, ANIMATION_ARC_STEPS, ANIMATION_ARC_HEIGHT


class PlayerType(Enum):
    """Type of player - human or AI controlled"""
    HUMAN = "Human"
    AI = "AI"


@dataclass
class Player:
    """Represents a player hand at the table"""
    name: str
    player_type: PlayerType
    hand: List[Tuple[str, str]] = field(default_factory=list)
    is_standing: bool = False
    is_busted: bool = False
    is_winner: bool = False  # Track win state for glow effect
    ai_skill: int = 50  # 0-100, 100 = perfect basic strategy
    
    def reset(self):
        """Reset player state for a new hand"""
        self.hand = []
        self.is_standing = False
        self.is_busted = False
        self.is_winner = False


class ArcAnimation:
    """Handles arc path calculations for card dealing animations"""
    
    def __init__(self, start_x: float, start_y: float, end_x: float, end_y: float,
                 arc_height: float = ANIMATION_ARC_HEIGHT):
        """
        Initialize an arc animation path.
        
        Args:
            start_x, start_y: Starting position
            end_x, end_y: Ending position
            arc_height: Maximum height of the arc above the straight line
        """
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.arc_height = arc_height
        
    def get_position(self, t: float) -> Tuple[float, float]:
        """
        Get the (x, y) position at time t (0.0 to 1.0).
        
        Uses a parabolic arc for natural card-throwing motion.
        
        Args:
            t: Progress through animation (0.0 = start, 1.0 = end)
            
        Returns:
            Tuple of (x, y) position
        """
        # Linear interpolation for x (horizontal movement)
        x = self.start_x + (self.end_x - self.start_x) * t
        
        # Linear interpolation for y (base vertical movement)
        base_y = self.start_y + (self.end_y - self.start_y) * t
        
        # Parabolic arc: peaks at t=0.5, zero at t=0 and t=1
        # Using -4 * arc_height * t * (t - 1) which gives a nice parabola
        arc_offset = -4 * self.arc_height * t * (t - 1)
        
        y = base_y - arc_offset  # Subtract because y increases downward
        
        return (x, y)
    
    def get_rotation(self, t: float) -> float:
        """
        Get the rotation angle at time t for a natural spinning effect.
        
        Args:
            t: Progress through animation (0.0 to 1.0)
            
        Returns:
            Rotation angle in degrees
        """
        # Card spins slightly during flight
        # Use sine for smooth start and end
        max_rotation = 15  # Maximum rotation in degrees
        return max_rotation * math.sin(t * math.pi)


class AnimationManager:
    """Manages card dealing and flip animations"""
    
    def __init__(self, game):
        self.game = game
        self.is_animating = False
        self.animation_queue = []
        self.current_animation_id = None
        self.active_arc_animations: List[dict] = []
        
    def cancel_all(self):
        """Cancel any running animations"""
        if self.current_animation_id:
            self.game.root.after_cancel(self.current_animation_id)
            self.current_animation_id = None
        
        # Cancel all arc animations
        for anim in self.active_arc_animations:
            if anim.get('after_id'):
                self.game.root.after_cancel(anim['after_id'])
            if anim.get('canvas'):
                anim['canvas'].destroy()
        
        self.active_arc_animations = []
        self.animation_queue = []
        self.is_animating = False
        
    def set_animating(self, state: bool):
        """Set the animation state"""
        self.is_animating = state
        
    def animate_card_arc(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int],
                        card_canvas, target_frame, callback: Optional[Callable] = None,
                        duration: int = ANIMATION_ARC_DURATION,
                        steps: int = ANIMATION_ARC_STEPS):
        """
        Animate a card along an arc path from start to end position.
        
        Args:
            start_pos: (x, y) starting position relative to game table
            end_pos: (x, y) ending position relative to game table
            card_canvas: The card canvas widget to animate
            target_frame: The frame to place card in after animation
            callback: Function to call when animation completes
            duration: Total animation duration in milliseconds
            steps: Number of animation steps
        """
        arc = ArcAnimation(
            start_pos[0], start_pos[1],
            end_pos[0], end_pos[1]
        )
        
        step_duration = duration // steps
        current_step = 0
        
        # Animation state
        anim_state = {
            'arc': arc,
            'canvas': card_canvas,
            'target_frame': target_frame,
            'callback': callback,
            'step_duration': step_duration,
            'total_steps': steps,
            'current_step': 0,
            'after_id': None
        }
        
        self.active_arc_animations.append(anim_state)
        self._execute_arc_step(anim_state)
        
    def _execute_arc_step(self, anim_state: dict):
        """Execute a single step of the arc animation"""
        current_step = anim_state['current_step']
        total_steps = anim_state['total_steps']
        
        if current_step > total_steps:
            # Animation complete
            self._finish_arc_animation(anim_state)
            return
            
        # Calculate progress (0.0 to 1.0)
        t = current_step / total_steps
        
        # Get position on arc
        arc = anim_state['arc']
        x, y = arc.get_position(t)
        
        # Move the card canvas
        canvas = anim_state['canvas']
        if canvas.winfo_exists():
            canvas.place(x=int(x), y=int(y))
        
        # Schedule next step
        anim_state['current_step'] += 1
        anim_state['after_id'] = self.game.root.after(
            anim_state['step_duration'],
            lambda: self._execute_arc_step(anim_state)
        )
        
    def _finish_arc_animation(self, anim_state: dict):
        """Complete an arc animation and clean up"""
        # Remove from active animations
        if anim_state in self.active_arc_animations:
            self.active_arc_animations.remove(anim_state)
        
        # Hide the flying card
        canvas = anim_state['canvas']
        if canvas.winfo_exists():
            canvas.place_forget()
            canvas.destroy()
        
        # Call completion callback
        if anim_state['callback']:
            anim_state['callback']()


class DeckPosition:
    """Tracks the deck position for animation origins"""
    
    def __init__(self, x: int = 50, y: int = 80):
        self.x = x
        self.y = y
        
    def get_position(self) -> Tuple[int, int]:
        """Get the current deck position"""
        return (self.x, self.y)
        
    def set_position(self, x: int, y: int):
        """Update deck position"""
        self.x = x
        self.y = y
