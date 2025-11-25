"""
Core game logic for Blackjack - dealing, scoring, AI decisions
"""

import random
from typing import List, Tuple

from config import SUITS, RANKS, HILO_VALUES


def create_deck(num_decks: int = 1) -> List[Tuple[str, str]]:
    """Create a shuffled shoe with the specified number of decks"""
    deck = []
    for _ in range(num_decks):
        for suit in SUITS:
            for rank in RANKS:
                deck.append((rank, suit))
    random.shuffle(deck)
    return deck


def get_card_value(card: Tuple[str, str]) -> int:
    """Get the blackjack value of a card"""
    rank = card[0]
    if rank in ['J', 'Q', 'K']:
        return 10
    elif rank == 'A':
        return 11
    else:
        return int(rank)


def get_hilo_value(card: Tuple[str, str]) -> int:
    """Get the Hi-Lo counting value of a card"""
    return HILO_VALUES[card[0]]


def calculate_hand_score(hand: List[Tuple[str, str]]) -> int:
    """Calculate the score of a hand, handling aces properly"""
    score = 0
    aces = 0
    
    for card in hand:
        value = get_card_value(card)
        if card[0] == 'A':
            aces += 1
        score += value
        
    # Reduce aces from 11 to 1 as needed
    while score > 21 and aces > 0:
        score -= 10
        aces -= 1
        
    return score


def calculate_running_count(visible_cards: List[Tuple[str, str]]) -> int:
    """Calculate running count from visible cards only"""
    count = 0
    for card in visible_cards:
        count += get_hilo_value(card)
    return count


def calculate_true_count(running_count: int, cards_remaining: int) -> float:
    """Calculate true count (running count / decks remaining)"""
    decks_remaining = max(cards_remaining / 52, 0.5)
    return running_count / decks_remaining


def get_basic_strategy_decision(hand_score: int, dealer_upcard: int, num_cards: int) -> str:
    """
    Return the optimal basic strategy decision.
    
    Returns: 'hit', 'stand', or 'double'
    """
    if hand_score >= 17:
        return 'stand'
    elif hand_score >= 13 and dealer_upcard <= 6:
        return 'stand'
    elif hand_score == 12 and 4 <= dealer_upcard <= 6:
        return 'stand'
    elif hand_score == 11 and num_cards == 2:
        return 'double'
    elif hand_score == 10 and dealer_upcard <= 9 and num_cards == 2:
        return 'double'
    elif hand_score == 9 and 3 <= dealer_upcard <= 6 and num_cards == 2:
        return 'double'
    else:
        return 'hit'


def get_ai_decision(hand_score: int, dealer_upcard: int, num_cards: int, ai_skill: int) -> str:
    """
    Get AI decision based on basic strategy with skill variance.
    
    ai_skill: 0-100, where 100 = perfect basic strategy
    """
    optimal = get_basic_strategy_decision(hand_score, dealer_upcard, num_cards)
    
    # Apply skill variance - lower skill means more random mistakes
    if random.randint(1, 100) > ai_skill:
        choices = ['hit', 'stand']
        if num_cards == 2:
            choices.append('double')
        return random.choice(choices)
        
    return optimal

