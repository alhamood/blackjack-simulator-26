# Blackjack Simulator

A Python-based blackjack simulator for testing playing strategies against configurable game conditions.

## Overview

This simulator allows you to:
- Test blackjack strategies (starting with basic strategy) across thousands of hands
- Configure various game rules (dealer hits soft 17, surrender allowed, etc.)
- Simulate with 1-6 physical decks or infinite deck
- Track and analyze win/loss/push rates and expected value
- Export results for further analysis

## Project Status

**Current Stage:** Stage 1 - Foundation & Documentation

**Completed:**
- Project structure created
- Documentation initialized
- Repository configured

**Next Steps:**
- Implement core game logic (cards, hands, dealer)
- Add strategy execution
- Build simulation engine

## Installation

### Prerequisites
- Python 3.9+ (tested with Python 3.9.12)
- Git

### Setup

1. Clone the repository:
```bash
git clone https://github.com/alhamood/blackjack-simulator-26.git
cd blackjack-simulator-26
```

2. (Optional) Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

Currently, the project uses only Python standard library, so no external dependencies are required.

## Project Structure

```
blackjack-simulator-26/
├── README.md                 # This file
├── PROJECT_CONTEXT.md        # Detailed context for AI handoffs
├── requirements.txt          # Python dependencies
├── config/                   # Game rules and strategy configurations
│   ├── game_rules.json
│   └── strategies/
│       └── basic_strategy.json
├── src/                      # Core simulation code
│   ├── cards.py             # Card, Deck, Shoe classes
│   ├── hand.py              # Hand evaluation logic
│   ├── dealer.py            # Dealer behavior
│   ├── player.py            # Player strategy execution
│   ├── game.py              # Single hand game logic
│   ├── simulator.py         # Multi-hand simulation engine
│   └── reporter.py          # Results analysis and export
├── tests/                    # Unit tests
└── results/                  # Simulation output files
```

## Usage

*Note: Core functionality is under development. This section will be updated as features are implemented.*

### Basic Simulation (Planned)

```python
from src.simulator import Simulator
from src.player import BasicStrategy

# Create simulator with 6-deck shoe
sim = Simulator(
    num_decks=6,
    penetration=0.75,  # Deal 75% of shoe before shuffle
    strategy=BasicStrategy()
)

# Run 10,000 hands
results = sim.run(num_hands=10000)

# Print results
print(f"Win rate: {results.win_rate:.2%}")
print(f"Expected value: {results.expected_value:.4f}")

# Export to CSV
results.to_csv('results/simulation_001.csv')
```

### Configurable Game Rules (Planned)

```python
from src.game import GameRules

rules = GameRules(
    dealer_hits_soft_17=True,
    surrender_allowed=True,
    double_after_split=True,
    blackjack_payout=1.5  # 3:2 payout
)

sim = Simulator(num_decks=6, rules=rules, strategy=BasicStrategy())
```

## Game Rules & Variations

The simulator supports common blackjack rule variations:

- **Deck Count**: 1, 2, 4, 6, or 8 decks, or infinite deck simulation
- **Penetration**: How far into the deck the dealer deals before reshuffling
- **Dealer hits soft 17**: Whether dealer must hit on soft 17
- **Surrender**: Whether player can surrender (forfeit half bet)
- **Double after split**: Whether player can double down after splitting
- **Split aces**: Whether aces can be split and how many times
- **Blackjack payout**: Typically 3:2 (1.5x) or 6:5 (1.2x)

## Strategy Format

Strategies are defined as lookup tables mapping (player_hand, dealer_upcard) to actions:

- **Hit**: Take another card
- **Stand**: End turn with current hand
- **Double**: Double bet and take exactly one card
- **Surrender**: Forfeit hand and lose half bet
- **Split**: Split pair into two hands

Hand types:
- **Hard totals**: No ace or ace counted as 1
- **Soft totals**: Ace counted as 11
- **Pairs**: Two cards of same rank

## Development

### Running Tests

```bash
pytest tests/
```

### Adding a New Strategy

1. Create strategy file in `config/strategies/`
2. Define mapping of (hand, dealer_card) → action
3. Load strategy in simulation

### Contributing

This is a personal project, but suggestions and improvements are welcome.

## Documentation

- [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md) - Comprehensive project context for AI collaboration
- This README - User-facing documentation

## License

Private project - all rights reserved.

## Author

alhamood - 2026

## Version History

- **v0.1 (In Progress)** - Stage 1: Foundation & Documentation
  - Project structure created
  - Documentation initialized
  - Git repository configured
