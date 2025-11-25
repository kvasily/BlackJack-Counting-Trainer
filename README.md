# ♠ PRIVATE CLUB ♠
### Blackjack Card Counting Trainer

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.x-blue?style=flat-square&logo=python&logoColor=white" alt="Python 3.x"/>
  <img src="https://img.shields.io/badge/GUI-Tkinter-green?style=flat-square" alt="Tkinter"/>
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=flat-square" alt="MIT License"/>
</p>

A sophisticated desktop application for learning and practicing the **Hi-Lo card counting system** in Blackjack. Featuring an elegant private club aesthetic with hand-crafted canvas-rendered cards and comprehensive training tools.

---

## ✨ Features

### 🎯 Card Counting Training
- **Running Count Display** — Real-time Hi-Lo count updated as cards are dealt
- **True Count Calculator** — Automatically adjusts for remaining decks
- **Hi-Lo Reference Chart** — Quick reference showing card values (+1, 0, -1)
- **On-Card Hi-Lo Badges** — Visual indicators on each card showing its counting value
- **Discard Tray Tracker** — See exactly which cards have been played

### 🎮 Game Modes
- **Training Mode** — All counting aids visible for learning
- **Test Mode** — Hide all aids to practice mental counting
- Toggle between modes with a single click

### 👥 Multiplayer Support
- Play **1-5 hands** simultaneously
- Configure each hand as **Human** or **AI** controlled
- **Adjustable AI skill level** (0-100%) — from random decisions to perfect basic strategy

### ⚙️ Customization
- **1-8 deck shoes** — Practice with any deck configuration
- **Turn Timer** — Optional countdown (5-30 seconds) for faster decision-making
- **Auto-Deal** — Automatically deal new hands after each round
- **Deck Penetration** — Automatic reshuffle at 25% deck remaining

### 🎨 Premium UI
- **Private Club aesthetic** — Dark walnut and espresso color palette
- **Canvas-rendered cards** — Beautiful cards with shadows, traditional pip layouts, and diamond-pattern backs
- **Smooth animations** — Card dealing with visual feedback
- **Win/Bust glow effects** — Clear visual indicators for game outcomes

---

## 🚀 Getting Started

### Prerequisites
- Python 3.x
- Tkinter (usually included with Python)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/BlackJack-Counting-Game.git
   cd BlackJack-Counting-Game
   ```

2. **Run the game**
   ```bash
   cd root
   python main.py
   ```

That's it! No additional dependencies required.

---

## 🎲 How to Play

### Basic Controls
| Button | Action |
|--------|--------|
| **HIT** | Draw another card |
| **STAND** | Keep your current hand |
| **DOUBLE** | Double down (first two cards only) |
| **DEAL** | Deal new hand with same deck |
| **NEW** | Start fresh with a new shuffled deck |
| **PAUSE** | Pause/resume the game |

### Understanding Hi-Lo Counting

The Hi-Lo system assigns values to cards:

| Cards | Count Value |
|-------|-------------|
| 2, 3, 4, 5, 6 | **+1** (Low cards) |
| 7, 8, 9 | **0** (Neutral) |
| 10, J, Q, K, A | **-1** (High cards) |

**Running Count**: Sum of all card values seen so far  
**True Count**: Running count ÷ decks remaining (more accurate for betting decisions)

### Training Tips
1. Start in **Training Mode** with Hi-Lo values visible on cards
2. Practice keeping the running count mentally while watching the display
3. Switch to **Test Mode** to verify your mental count
4. Increase difficulty by adding more decks or enabling the turn timer

---

## 📁 Project Structure

```
BlackJack-Counting-Game/
└── root/
    ├── main.py           # Application entry point
    ├── blackjack_game.py # Main game controller class
    ├── game_logic.py     # Core game mechanics & AI decisions
    ├── models.py         # Player, Animation, and data models
    ├── ui_components.py  # Card rendering & UI helpers
    └── config.py         # Colors, constants, and settings
```

---

## ⚙️ Settings

Access the Settings panel (⚙ button) to configure:

- **Number of Decks** (1-8)
- **Number of Hands** (1-5)
- **Player Types** (Human/AI per hand)
- **AI Skill Level** (0-100%)
- **Turn Timer** (on/off, 5-30 sec)
- **Auto-Deal** (on/off, 1-5 sec delay)
- **Show Hi-Lo on Cards** (on/off)

---

## 🎨 Color Palette

The "Private Club" theme features an elegant dark aesthetic:

| Element | Color |
|---------|-------|
| Background | Deep Espresso `#1a1512` |
| Table Felt | Muted Forest Green `#2d4a3e` |
| Accents | Warm Ivory/Cream `#d4c4a8` |
| Card Backs | Rich Burgundy `#5c2e2e` |
| Success | Muted Sage `#6b9b7a` |
| Danger | Muted Burgundy `#a85454` |

---

## 🤝 Contributing

Contributions are welcome! Feel free to:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Classic casino aesthetics for UI inspiration
- The Hi-Lo counting system developed by Harvey Dubner
- Python/Tkinter community for GUI framework

---

<p align="center">
  <strong>♠ ♥ Good luck at the tables! ♦ ♣</strong>
</p>

