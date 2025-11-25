import tkinter as tk
import random

class BlackjackGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Blackjack")
        self.root.geometry("800x600")
        self.root.configure(bg='dark green')
        
        # Initialize game variables
        self.deck = []
        self.player_hand = []
        self.dealer_hand = []
        self.player_score = 0
        self.dealer_score = 0
        self.game_over = False
        
        # Card values
        self.suits = ['hearts', 'diamonds', 'clubs', 'spades']
        self.ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        
        self.setup_gui()
        self.start_new_game()
    
    def setup_gui(self):
        # Title
        title_label = tk.Label(self.root, text="BLACKJACK", font=('Arial', 24, 'bold'), 
                              bg='dark green', fg='gold')
        title_label.pack(pady=10)
        
        # Dealer frame
        dealer_frame = tk.Frame(self.root, bg='dark green')
        dealer_frame.pack(pady=20)
        
        dealer_label = tk.Label(dealer_frame, text="Dealer's Hand:", font=('Arial', 16, 'bold'),
                               bg='dark green', fg='white')
        dealer_label.pack()
        
        self.dealer_cards_frame = tk.Frame(dealer_frame, bg='dark green')
        self.dealer_cards_frame.pack(pady=10)
        
        self.dealer_score_label = tk.Label(dealer_frame, text="Score: ?", font=('Arial', 14),
                                          bg='dark green', fg='white')
        self.dealer_score_label.pack()
        
        # Player frame
        player_frame = tk.Frame(self.root, bg='dark green')
        player_frame.pack(pady=20)
        
        player_label = tk.Label(player_frame, text="Your Hand:", font=('Arial', 16, 'bold'),
                               bg='dark green', fg='white')
        player_label.pack()
        
        self.player_cards_frame = tk.Frame(player_frame, bg='dark green')
        self.player_cards_frame.pack(pady=10)
        
        self.player_score_label = tk.Label(player_frame, text="Score: 0", font=('Arial', 14),
                                          bg='dark green', fg='white')
        self.player_score_label.pack()
        
        # Buttons frame
        buttons_frame = tk.Frame(self.root, bg='dark green')
        buttons_frame.pack(pady=20)
        
        self.hit_button = tk.Button(buttons_frame, text="Hit", font=('Arial', 14),
                                   command=self.player_hit, width=10, bg='light blue')
        self.hit_button.grid(row=0, column=0, padx=10)
        
        self.stand_button = tk.Button(buttons_frame, text="Stand", font=('Arial', 14),
                                     command=self.player_stand, width=10, bg='light coral')
        self.stand_button.grid(row=0, column=1, padx=10)
        
        self.new_game_button = tk.Button(buttons_frame, text="New Game", font=('Arial', 14),
                                        command=self.start_new_game, width=10, bg='light green')
        self.new_game_button.grid(row=0, column=2, padx=10)
        
        # Status label
        self.status_label = tk.Label(self.root, text="Welcome to Blackjack!", font=('Arial', 16, 'bold'),
                                    bg='dark green', fg='yellow')
        self.status_label.pack(pady=10)
        
        # Game instructions
        instructions = tk.Label(self.root, text="Try to get closer to 21 than the dealer without going over!", 
                               font=('Arial', 10), bg='dark green', fg='white')
        instructions.pack(side='bottom', pady=5)
    
    def create_deck(self):
        """Create a standard deck of 52 cards"""
        deck = []
        for suit in self.suits:
            for rank in self.ranks:
                deck.append((rank, suit))
        random.shuffle(deck)
        return deck
    
    def get_card_value(self, card):
        """Get the value of a card"""
        rank = card[0]
        if rank in ['J', 'Q', 'K']:
            return 10
        elif rank == 'A':
            return 11
        else:
            return int(rank)
    
    def calculate_hand_score(self, hand):
        """Calculate the score of a hand, handling aces properly"""
        score = 0
        aces = 0
        
        for card in hand:
            value = self.get_card_value(card)
            if card[0] == 'A':
                aces += 1
            score += value
        
        # Adjust for aces if score is over 21
        while score > 21 and aces > 0:
            score -= 10
            aces -= 1
        
        return score
    
    def create_card_widget(self, card, hidden=False):
        """Create a visual card widget"""
        if hidden:
            # Create back of card
            card_frame = tk.Frame(self.dealer_cards_frame, bg='red', relief='raised', bd=3, 
                                 width=80, height=120)
            card_frame.pack_propagate(False)
            
            inner_frame = tk.Frame(card_frame, bg='dark red', width=74, height=114)
            inner_frame.pack_propagate(False)
            inner_frame.pack(padx=3, pady=3)
            
            label = tk.Label(inner_frame, text="?", font=('Arial', 24, 'bold'), 
                           bg='dark red', fg='yellow')
            label.pack(expand=True)
            
        else:
            # Create front of card
            rank, suit = card
            suit_symbols = {'hearts': '♥', 'diamonds': '♦', 'clubs': '♣', 'spades': '♠'}
            suit_colors = {'hearts': 'red', 'diamonds': 'red', 'clubs': 'black', 'spades': 'black'}
            
            card_frame = tk.Frame(self.player_cards_frame, bg='white', relief='raised', bd=3, 
                                 width=80, height=120)
            card_frame.pack_propagate(False)
            
            # Top rank and suit
            top_frame = tk.Frame(card_frame, bg='white')
            top_frame.pack(anchor='nw', padx=5, pady=5)
            
            rank_label = tk.Label(top_frame, text=rank, font=('Arial', 12, 'bold'),
                                fg=suit_colors[suit], bg='white')
            rank_label.pack(side='left')
            
            suit_label = tk.Label(top_frame, text=suit_symbols[suit], font=('Arial', 12),
                                fg=suit_colors[suit], bg='white')
            suit_label.pack(side='left')
            
            # Center large suit symbol
            center_label = tk.Label(card_frame, text=suit_symbols[suit], font=('Arial', 32, 'bold'),
                                  fg=suit_colors[suit], bg='white')
            center_label.pack(expand=True)
            
            # Bottom rank and suit (upside down)
            bottom_frame = tk.Frame(card_frame, bg='white')
            bottom_frame.pack(anchor='se', padx=5, pady=5)
            
            rank_label_bottom = tk.Label(bottom_frame, text=rank, font=('Arial', 12, 'bold'),
                                       fg=suit_colors[suit], bg='white')
            rank_label_bottom.pack(side='right')
            
            suit_label_bottom = tk.Label(bottom_frame, text=suit_symbols[suit], font=('Arial', 12),
                                       fg=suit_colors[suit], bg='white')
            suit_label_bottom.pack(side='right')
        
        return card_frame
    
    def update_display(self):
        """Update the GUI with current game state"""
        # Clear existing cards
        for widget in self.dealer_cards_frame.winfo_children():
            widget.destroy()
        for widget in self.player_cards_frame.winfo_children():
            widget.destroy()
        
        # Display dealer's cards
        for i, card in enumerate(self.dealer_hand):
            if i == 0 and not self.game_over:
                card_widget = self.create_card_widget(card, hidden=True)
            else:
                card_widget = self.create_card_widget(card)
            card_widget.pack(side='left', padx=5)
        
        # Display player's cards
        for card in self.player_hand:
            card_widget = self.create_card_widget(card)
            card_widget.pack(side='left', padx=5)
        
        # Update scores
        self.player_score = self.calculate_hand_score(self.player_hand)
        self.player_score_label.config(text=f"Score: {self.player_score}")
        
        if self.game_over:
            self.dealer_score = self.calculate_hand_score(self.dealer_hand)
            self.dealer_score_label.config(text=f"Score: {self.dealer_score}")
        else:
            # Only show visible card value for dealer
            if len(self.dealer_hand) > 1:
                visible_score = self.get_card_value(self.dealer_hand[1])
                self.dealer_score_label.config(text=f"Score: ? + {visible_score}")
            else:
                self.dealer_score_label.config(text="Score: ?")
        
        # Update button states
        if self.game_over:
            self.hit_button.config(state='disabled')
            self.stand_button.config(state='disabled')
        else:
            self.hit_button.config(state='normal')
            self.stand_button.config(state='normal')
    
    def start_new_game(self):
        """Start a new game"""
        self.deck = self.create_deck()
        self.player_hand = []
        self.dealer_hand = []
        self.game_over = False
        
        # Deal initial cards
        self.player_hand.append(self.deck.pop())
        self.dealer_hand.append(self.deck.pop())
        self.player_hand.append(self.deck.pop())
        self.dealer_hand.append(self.deck.pop())
        
        self.update_display()
        self.status_label.config(text="Your turn! Hit or Stand?")
        
        # Check for blackjack
        player_score = self.calculate_hand_score(self.player_hand)
        if player_score == 21:
            self.status_label.config(text="Blackjack! You got 21!")
            self.player_stand()
    
    def player_hit(self):
        """Player draws a card"""
        if self.game_over:
            return
        
        self.player_hand.append(self.deck.pop())
        self.update_display()
        
        player_score = self.calculate_hand_score(self.player_hand)
        
        if player_score > 21:
            self.end_game("Bust! You went over 21. Dealer wins!")
        elif player_score == 21:
            self.status_label.config(text="You have 21! Good job!")
            self.player_stand()
    
    def player_stand(self):
        """Player stands, dealer plays"""
        self.game_over = True
        
        # Dealer draws until 17 or higher
        dealer_score = self.calculate_hand_score(self.dealer_hand)
        while dealer_score < 17:
            self.dealer_hand.append(self.deck.pop())
            dealer_score = self.calculate_hand_score(self.dealer_hand)
        
        self.update_display()
        self.determine_winner()
    
    def determine_winner(self):
        """Determine the winner and display result"""
        player_score = self.calculate_hand_score(self.player_hand)
        dealer_score = self.calculate_hand_score(self.dealer_hand)
        
        if player_score > 21:
            result = "Bust! You went over 21. Dealer wins!"
            color = "red"
        elif dealer_score > 21:
            result = "Dealer busts! You win!"
            color = "green"
        elif player_score > dealer_score:
            result = f"You win! {player_score} to {dealer_score}"
            color = "green"
        elif dealer_score > player_score:
            result = f"Dealer wins! {dealer_score} to {player_score}"
            color = "red"
        else:
            result = f"Push! It's a tie! {player_score} to {dealer_score}"
            color = "yellow"
        
        self.status_label.config(text=result, fg=color)
    
    def end_game(self, message):
        """End the game with a message"""
        self.game_over = True
        self.status_label.config(text=message, fg='red')
        self.update_display()

def main():
    root = tk.Tk()
    game = BlackjackGame(root)
    root.mainloop()

if __name__ == "__main__":
    main()