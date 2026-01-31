# Blackjack Simulator - Project Context

**Last Updated:** 2026-01-31
**Project Status:** Stage 4 - Results & Analysis (COMPLETE)
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
6. **Web Interface**: Provide simple web UI for running simulations without writing code

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
├── web/                      # Web interface (Stage 5)
│   ├── api.py               # FastAPI server
│   └── static/
│       ├── index.html       # Single-page web UI
│       ├── styles.css       # Simple styling
│       └── app.js           # Vanilla JavaScript frontend
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

**Web Interface Architecture (Stage 5):**
- **Backend**: FastAPI server (Python) exposing simulation as REST API
- **Frontend**: Static HTML/CSS/JavaScript (vanilla JS or Alpine.js for simplicity)
- **Separation**: Core simulation logic (`src/`) stays pure Python with no web dependencies
- **API Design**:
  - `GET /api/defaults` - Returns default game parameters from config files
  - `POST /api/simulate` - Accepts parameters, runs simulation, returns results
  - `GET /api/results/{id}` - Retrieves cached simulation results (optional)
- **Frontend Flow**:
  1. Load page → fetch defaults → populate selectors
  2. User adjusts parameters (dropdowns, sliders)
  3. Click "Run Simulation" → POST to API
  4. Display loading state
  5. Show results (win rate, expected value, statistics)
- **Deployment**: Can run locally or deploy (Render, Railway, Vercel for frontend + backend)

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

### Stage 1: Foundation & Documentation (COMPLETE)
**Status**: ✓ COMPLETE
**Goal**: Set up repository and comprehensive documentation

**Completed:**
- ✓ Local project directory created
- ✓ Git repository initialized and configured
- ✓ requirements.txt created
- ✓ Project structure created
- ✓ PROJECT_CONTEXT.md and README.md created
- ✓ Private GitHub repository created and pushed

### Stage 2: Core Game Logic (COMPLETE)
**Status**: ✓ COMPLETE (2026-01-30)
**Goal**: Implement basic blackjack game mechanics

**Completed:**
- ✓ cards.py: Card, Deck, Shoe classes (19 tests)
  - Multi-deck shoes (1-8 decks)
  - Infinite deck mode (CSM)
  - Penetration tracking with auto-reshuffle
- ✓ hand.py: Hand evaluation logic (19 tests)
  - Soft/hard ace handling
  - Blackjack, bust, pair detection
  - Complex multi-ace logic
- ✓ dealer.py: Dealer behavior (20 tests)
  - Automatic play following house rules
  - Configurable H17/S17 rule
  - Upcard/hole card management
- ✓ game.py: Complete game flow (16 tests)
  - Full blackjack gameplay
  - Player actions: hit, stand, double, surrender
  - Configurable game rules
  - Payout calculations
- ✓ Demo scripts for all modules
- ✓ **74 total passing tests**

### Stage 3: Strategy & Simulation (COMPLETE)
**Status**: ✓ COMPLETE (2026-01-30)
**Goal**: Add strategy execution and multi-hand simulation

**Completed:**
- ✓ player.py: JSON-based strategy system (19 tests)
  - Load strategies from JSON files
  - Support for hard totals, soft totals, pairs
  - Fallback actions (double_else_hit, surrender_else_hit, etc.)
  - Dealer upcard and pair rank normalization
- ✓ simulator.py: Full simulation engine (22 tests)
  - Single-session mode for accurate EV calculation
  - Multi-session mode for variance analysis
  - Strategy comparison framework
  - Detailed statistics tracking
- ✓ Strategy files:
  - basic_strategy_h17.json: Full Wizard of Odds basic strategy
  - never_bust.json: Toy strategy for comparison
- ✓ Demo scripts and extensive testing
- ✓ **115 total passing tests** (was 74)

**Results:**
- Basic strategy: ~-1% EV (expected: ~-0.5%)
- Never-bust strategy: ~-5% EV (4% worse than basic)
- Always-stand strategy: ~-16% EV
- Session variance: StdDev ~0.106 over 100 sessions

### Stage 4: Results & Analysis (COMPLETE)
**Status**: ✓ COMPLETE (2026-01-31)
**Goal**: Add results tracking and reporting

**Completed:**
- ✓ reporter.py: Results export module
  - CSV export: summary, sessions, hand samples
  - JSON export for web API consumption
  - Optional hand tracking with configurable sampling (default: 100 hands)
- ✓ simulator.py: Enhanced with hand tracking
  - Added `track_hands` and `max_tracked_hands` parameters
  - Minimal memory overhead - only tracks sample for sense-checking
- ✓ demo_reporter.py: Demo script showing export functionality
- ✓ test_reporter.py: 12 comprehensive tests for export functions
- ✓ **127 total passing tests** (was 115)

**Implementation notes:**
- Hand-level CSV export is optional and off by default (configurable)
- By default, tracks first 100 hands for spot-checking simulation correctness
- CSV files are clean and ready for Excel/Google Sheets import
- JSON export designed for Stage 5 web API consumption

### Stage 5: Web Interface (PLANNED)
**Goal**: Build simple web UI for running simulations

**Tasks:**
- Create FastAPI server (web/api.py)
  - Endpoint to fetch default parameters
  - Endpoint to run simulation with custom parameters
  - Endpoint to retrieve results
- Build static frontend (web/static/)
  - HTML structure with parameter selectors
  - CSS for simple, clean styling
  - JavaScript for API calls and UI updates
- Test web interface locally
- (Optional) Deploy to hosting platform
- Add web interface documentation to README

**Technical Notes:**
- Keep frontend simple: ~100 lines HTML, ~50 lines JS, ~30 lines CSS
- Use vanilla JavaScript or Alpine.js (no heavy frameworks)
- Core simulation code (`src/`) remains web-agnostic
- FastAPI chosen for modern Python, auto-generated API docs, ease of use

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

7. **Web Interface Architecture**: Chose FastAPI + static frontend over Streamlit for clean separation of concerns. Core simulation logic (`src/`) stays pure Python with no web framework dependencies. Frontend uses vanilla JavaScript for simplicity and minimal dependencies.

8. **No Heavy Frontend Frameworks**: Avoiding React, Vue, etc. to keep code simple and minimal. Vanilla JS or Alpine.js is sufficient for the straightforward UI needs.

---

## Questions & Clarifications

### Answered
- Q: Use GitHub CLI or direct git? → A: GitHub CLI (installed and authenticated)
- Q: Project location? → A: ~/projects/blackjack-simulator-26
- Q: GitHub username? → A: alhamood
- Q: HTTPS or SSH? → A: HTTPS

### Answered (2026-01-30)
- Q: Web interface approach? → A: FastAPI + static frontend (vanilla JS)
- Q: Keep simulation logic separate from web code? → A: Yes, `src/` stays pure Python

### Open Questions
- File structure granularity: Keep as-is or consolidate modules?
- Export format preference: CSV sufficient or add other formats?
- Google Sheets integration: Priority or defer to later?
- Testing depth: How comprehensive should unit tests be?
- Web deployment platform: Run locally or deploy to Render/Railway/Vercel?

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
