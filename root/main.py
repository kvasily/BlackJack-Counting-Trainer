"""
Blackjack Card Counting Trainer
Entry point for the application
"""

import tkinter as tk
from blackjack_game import BlackjackGame


def main():
    root = tk.Tk()
    game = BlackjackGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()

