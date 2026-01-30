# Blackjack Simulator - Project Context

**Last Updated:** 2026-01-29
**Project Status:** Stage 1 - Foundation & Documentation (IN PROGRESS)
**Repository:** Private GitHub repository (alhamood/blackjack-simulator-26)

---

## Project Overview

A Python-based blackjack simulator designed to test various playing strategies against different game conditions. The simulator runs thousands of hands to provide statistical analysis of strategy performance.

### Project Goals

1. **Strategy Testing**: Evaluate blackjack strategies (starting with basic strategy) across many simulated hands
2. **Configurable Game Conditions**: Support various common blackjack rule variations
3. **Statistical Analysis**: Track and report win/loss/push rates, expected value, and other metrics
4. **Flexible Deck Configurations**: Support 1-6 physical decks or infinite deck simulation
5. **Results Export**: Output results in formats suitable for analysis (CSV, JSON)

### Key Requirements

- **Primary Language**: Python (for accessibility to data science background)
- **Simplicity First**: Avoid over-engineering; keep solutions focused and straightforward
- **Multi-AI Collaboration**: Designed for work across different AI instances and sessions
- **Clear Documentation**: Comprehensive context for easy project handoffs

---

## Technical Architecture

### Project Structure

```
blackjack-simulator-26/
├── README.md                 # User-facing documentation
├── PROJECT_CONTEXT.md        # This file - AI handoff context
├── requirements.txt          # Python dependencies
├── .gitignore               # Git ignore rules
├── config/
│   ├── game_rules.json      # Configurable game conditions
│   └── strategies/
│       └── basic_strategy.json  # Strategy definitions
├── src/
│   ├── __init__.py
│   ├── cards.py             # Card, Deck, Shoe classes
│   ├── hand.py              # Hand evaluation logic
│   ├── dealer.py            # Dealer behavior
│   ├── player.py            # Player strategy execution
│   ├── game.py              # Single hand game logic
│   ├── simulator.py         # Multi-hand simulation engine
│   └── reporter.py          # Results analysis and export
├── tests/
│   └── test_*.py            # Unit tests
└── results/
    └── .gitkeep             # Results output folder
```

### Design Decisions

**Module Organization:**
- Granular file structure chosen to facilitate multi-AI collaboration
- Each module has clear responsibility (cards, hands, dealer, player, game, simulator, reporter)
- Alternative: Could consolidate into fewer files (e.g., game_logic.py + simulator.py)
- Decision point: User preference as DS vs SWE background

**Testing Strategy:**
- Unit tests to verify individual components work correctly
- Critical for catching bugs when returning to project after time
- Focus on core logic: hand evaluation, strategy execution, game rules
- Keep lightweight - not over-engineered

**Data Structures:**
- Card: Simple representation (rank, suit)
- Deck/Shoe: Collection of cards with shuffling logic
- Hand: Cards + evaluation (hard total, soft total, pair detection)
- Strategy: Lookup table mapping (player_hand, dealer_upcard) → action

---

## Game Logic Specifications

### Deck Configuration
- **Deck Count**: 1, 2, 4, 6, or 8 decks, OR infinite deck simulation
- **Penetration**: Configurable percentage of deck dealt before reshuffling
- **Shuffle**: When penetration threshold reached

### Game Rules (Configurable)
- **Dealer hits soft 17**: Yes/No
- **Surrender allowed**: Yes/No
- **Double after split**: Yes/No
- **Split aces allowed**: Yes/No
- **Number of ace splits**: Configurable limit
- **Blackjack payout**: 3:2 (standard) or 6:5 (unfavorable)
- **Insurance**: Available/not (future consideration)

### Player Actions
- **Hit**: Take another card
- **Stand**: End turn with current hand
- **Double Down**: Double bet, take exactly one more card
- **Surrender**: Forfeit hand, lose half bet
- **Split**: Split pair into two hands (with constraints)

### Strategy Representation
- Mapping of (player_hand, dealer_upcard) → action
- Hand types: Hard totals, Soft totals (with Ace), Pairs
- Example: (Hard 16, Dealer 10) → Surrender if allowed, else Hit
- Simplified: Many hands are equivalent (any hard 16 is the same)

### Win Conditions
- Player closer to 21 than dealer without busting → Win (1x bet)
- Player blackjack (21 in 2 cards) → Win (1.5x bet with 3:2 payout)
- Player busts (>21) → Lose
- Dealer busts, player doesn't → Win
- Push (tie) → Return bet

---

## Implementation Stages

### Stage 1: Foundation & Documentation (CURRENT)
**Status**: IN PROGRESS
**Goal**: Set up repository and comprehensive documentation

**Completed:**
- ✓ Local project directory created at `~/projects/blackjack-simulator-26`
- ✓ Git repository initialized
- ✓ .gitignore configured for Python
- ✓ requirements.txt created (minimal for now)
- ✓ Project structure created (folders, __init__.py files)
- ✓ PROJECT_CONTEXT.md created

**In Progress:**
- Creating README.md

**Remaining:**
- Initial git commit
- Create private GitHub repository (alhamood/blackjack-simulator-26)
- Push to remote

### Stage 2: Core Game Logic (PLANNED)
**Goal**: Implement basic blackjack game mechanics

**Tasks:**
- Implement Card, Deck, Shoe classes (cards.py)
- Implement Hand class with evaluation logic (hand.py)
- Implement dealer behavior (dealer.py)
- Implement single hand game flow (game.py)
- Write unit tests for core components
- Test with manual single-hand games

### Stage 3: Strategy & Simulation (PLANNED)
**Goal**: Add strategy execution and multi-hand simulation

**Tasks:**
- Define basic strategy data structure
- Implement strategy loader and executor (player.py)
- Implement simulation engine for N hands (simulator.py)
- Add configurable game rules
- Test strategy execution accuracy

### Stage 4: Results & Analysis (PLANNED)
**Goal**: Add results tracking and reporting

**Tasks:**
- Implement results tracking during simulation
- Calculate win/loss/push rates, expected value
- Export to CSV/JSON (reporter.py)
- Add summary statistics
- Optionally: Add Google Sheets integration

---

## Development Environment

**Platform:** macOS (Darwin 25.2.0)
**Python Version:** 3.9.12
**Git Version:** 2.39.2
**GitHub CLI:** 2.86.0
**GitHub Account:** alhamood
**Working Directory:** /Users/alberthamood/projects/blackjack-simulator-26

**Version Control:**
- Repository: Private GitHub repository
- Branch: main
- Commit strategy: Meaningful commits for each feature/stage
- Tagging: Use semantic versioning (v0.1, v0.2, etc.)

---

## Known Decisions & Trade-offs

1. **Python Standard Library First**: Minimal external dependencies initially. Can add pandas/numpy later for enhanced analysis.

2. **Simplified Hand Equivalence**: Treating all hands of the same total as equivalent (e.g., 10+6 = 9+7 = 8+8 for hard 16). This is standard for basic strategy.

3. **No GUI Initially**: Command-line/script-based simulation. Focus on engine first, UI later if needed.

4. **CSV Export Initially**: Start with CSV/JSON export. Google Sheets API integration is optional future enhancement.

5. **File Granularity**: Chose granular modules (cards.py, hand.py, etc.) over consolidated files. This aids multi-AI collaboration but may seem over-engineered to DS background. Open to consolidation if preferred.

6. **Unit Tests Lightweight**: Focus tests on critical logic (hand evaluation, strategy lookup, game rules). Don't over-test for a personal project.

---

## Questions & Clarifications

### Answered
- Q: Use GitHub CLI or direct git? → A: GitHub CLI (installed and authenticated)
- Q: Project location? → A: ~/projects/blackjack-simulator-26
- Q: GitHub username? → A: alhamood
- Q: HTTPS or SSH? → A: HTTPS

### Open Questions
- File structure granularity: Keep as-is or consolidate modules?
- Export format preference: CSV sufficient or add other formats?
- Google Sheets integration: Priority or defer to later?
- Testing depth: How comprehensive should unit tests be?

---

## Next Steps

**Immediate (Stage 1 Completion):**
1. Complete README.md
2. Make initial git commit
3. Create private GitHub repository
4. Push to GitHub
5. Verify remote repository is accessible

**Next Session (Stage 2):**
1. Implement cards.py (Card, Deck, Shoe)
2. Implement hand.py (Hand evaluation)
3. Add basic unit tests
4. Test manually

---

## Notes for AI Handoffs

**Context for Next AI Instance:**
- User (alhamood) is a data scientist, not a software engineer
- Prefers Python and straightforward solutions
- Values clear documentation and simple code over complex abstractions
- Working across multiple AI sessions - keep documentation updated
- This is a warmup project; user has more complex projects planned
- User may switch between different AI instances/tiers

**Communication Style:**
- Direct and concise
- Explain technical decisions when asked
- Don't over-engineer or add unrequested features
- Ask clarifying questions when requirements are ambiguous

**Remember:**
- Update this file after each significant milestone
- Keep PROJECT_CONTEXT.md and README.md in sync
- Document design decisions and rationale
- Track open questions and decisions made
