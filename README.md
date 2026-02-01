# Blackjack Simulator

A Python-based blackjack simulator for testing playing strategies against configurable game conditions.

## Overview

This simulator allows you to:
- Test blackjack strategies (starting with basic strategy) across thousands of hands
- Configure various game rules (dealer hits soft 17, surrender allowed, etc.)
- Simulate with 1-6 physical decks or infinite deck
- Track and analyze win/loss/push rates and expected value
- Export results for further analysis
- Run simulations via command line or web interface (planned)

## Project Status

**Current Stage:** Stage 10 - Strategy Editor Fixes & Mimic-the-Dealer ✓ COMPLETE

**Completed:**
- ✓ Stage 1: Foundation & Documentation
- ✓ Stage 2: Core Game Logic
  - Card, Deck, and Shoe classes with infinite deck support
  - Hand evaluation with soft/hard ace logic
  - Dealer behavior with configurable rules
  - Complete blackjack game engine
- ✓ Stage 3: Strategy & Simulation
  - JSON-based strategy system with Wizard of Odds basic strategy
  - Strategy comparison framework
  - Single-session and multi-session simulation engine
  - Variance analysis across sessions
- ✓ Stage 4: Results & Analysis
  - CSV export for summary, sessions, and hand samples
  - JSON export for web API consumption
  - Optional hand tracking (default: first 100 hands)
  - 127 passing tests across all modules
- ✓ Stage 5: Web Interface
  - FastAPI backend with 5 REST endpoints
  - Interactive web UI with comprehensive parameter control
  - Chart.js visualization for outcome distribution
  - Visual strategy editor for creating custom strategies
  - Download results as JSON or CSV
  - Deployment-ready with Procfile
  - 12 API endpoint tests
- ✓ Stage 6: Split Implementation & Strategy Verification
  - Complete split/re-split logic (up to 4 hands)
  - Split aces handling (one card only, no re-split)
  - Double after split support
  - Individual hand tracking with bet/payout aggregation
  - Debug mode with strategy categorization
  - Action history tracking for verification
  - EV calculations now accurate (~-0.5% for optimal basic strategy)
- ✓ Stage 7: Enhanced Visualizations
  - Replaced pie charts with bar chart (hand outcomes) and histogram (session distribution)
  - Hand outcome chart sorted descending by frequency
  - Session statistics table with percentiles (P10, P25, P50, P75, P90)
  - Reorganized UI into Session-Level and Hand-Level Analysis sections
  - Color-coded charts for better visual distinction
  - Sturges' rule for optimal histogram binning

- ✓ Stage 8: Time Estimation & Reporting
  - Pre-simulation time estimates via calibration (shown inline in config)
  - Elapsed time reporting in results (full server-side timing)
  - Best/worst session stats in session statistics table
  - `/api/estimate` endpoint for time prediction
  - Fixed 45MB response overhead from unnecessary hand tracking

- ✓ Stage 9: Performance Optimization & Chart Enhancements
  - 1.57x simulation speedup via Card/Hand/Shoe optimizations
  - Session histogram with mandatory zero boundary (clean red/green separation)
  - Payout labels on both charts (abbreviated format: +1.2k, -340)
  - Input limits increased 10x (up to 100M total hands)
  - Improved time estimation accuracy (<1% error)

- ✓ Stage 10: Strategy Editor Fixes & Mimic-the-Dealer
  - Fixed "Use in Simulation" flow (server-side URL param + inline script injection)
  - Added "Quick Test" button for instant EV feedback in editor
  - Added mimic-the-dealer strategy (~-6% EV baseline)
  - Fixed strategy dropdown ordering (H17 basic strategy always first)
  - Updated version numbers and added cache-busting

**Next Steps:** (See [NEXT_STEPS.md](NEXT_STEPS.md) for details)
- Additional default strategies (card counting, conservative variants)
- Strategy editor further improvements
- AWS deployment preparation

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
├── web/                      # Web interface (planned)
│   ├── api.py               # FastAPI server
│   └── static/
│       ├── index.html       # Web UI
│       ├── styles.css       # Styling
│       └── app.js           # Frontend logic
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

### Web Interface

The simulator includes a comprehensive web interface for running simulations without writing code.

**Starting the Web Server:**
```bash
# Install web dependencies if not already installed
pip install -r requirements.txt

# Start the server
python web/api.py

# Or use uvicorn directly
uvicorn web.api:app --reload
```

Then open [http://localhost:8000](http://localhost:8000) in your browser.

**Features:**
- **Configuration Form**: Control all simulation parameters
  - Game rules (dealer hits soft 17, surrender, double after split, blackjack payout)
  - Shoe configuration (deck count, penetration, infinite shoe mode)
  - Simulation settings (number of hands, number of sessions)
  - Strategy selection (built-in strategies or custom)
  - Debug mode for strategy verification
- **Results Display**:
  - Summary statistics (EV, win rate, total payout, split count)
  - **Session-Level Analysis**:
    - Interactive histogram showing distribution of session payouts
    - Color-coded bins (green for profit, red for loss, gray for break-even)
    - Optimal binning using Sturges' rule
    - Comprehensive statistics table with percentiles (P10, P25, P50, P75, P90), mean, and standard deviation
  - **Hand-Level Analysis**:
    - Bar chart of hand outcomes sorted descending by frequency
    - Categories: Blackjacks, Double Wins/Losses, Regular Wins/Losses, Surrenders, Pushes
    - Color-coded bars for visual distinction
    - Hierarchical breakdown table with payout analysis
      - Shows wins/losses/pushes with indented sub-categories
      - Displays count, percentage, and total payout in units for each outcome type
  - Debug mode output:
    - Hands categorized by strategy situation (hard_12_vs_10, pair_8_vs_5, etc.)
    - Initial 2-card hand for accurate strategy verification
    - Complete action history for each hand
    - Split hand details (each hand shown separately with actions, cards, bets, payouts)
    - Dealer final value for comparison
  - Download results as JSON or CSV
- **Strategy Editor**: Create and edit custom strategies
  - Visual table builder for defining strategies
  - Load existing strategies for modification
  - Save custom strategies as JSON files
  - Use custom strategies directly in simulations
- **Split Hand Support**:
  - Complete split/re-split logic (up to 4 hands)
  - Split aces receive one card only (casino rules)
  - Double after split (configurable)
  - Individual tracking of each split hand
  - Bet and payout aggregation across all hands
  - 21 after split pays 1:1 (not blackjack 3:2)

**API Endpoints:**
- `GET /api/defaults` - Get default game parameters and available strategies
- `POST /api/simulate` - Run simulation with custom parameters (supports custom strategies)
- `GET /api/strategies` - List all available strategies
- `GET /api/strategies/{id}` - Get full strategy JSON for editing
- `GET /docs` - Interactive API documentation (Swagger UI)

**Architecture:**
- **Backend**: FastAPI server ([web/api.py](web/api.py))
- **Frontend**: Static HTML/CSS/JavaScript ([web/static/](web/static/))
- Core simulation logic ([src/](src/)) remains pure Python with no web dependencies

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

## Roadmap

- **Stage 1**: Foundation & Documentation ✓
- **Stage 2**: Core Game Logic (cards, hands, dealer) ✓
- **Stage 3**: Strategy & Simulation (strategy execution, simulation engine) ✓
- **Stage 4**: Results & Analysis (CSV/JSON export, hand tracking) ✓
- **Stage 5**: Web Interface (FastAPI backend, static frontend) ✓
- **Stage 6**: Split Implementation & Strategy Verification ✓
- **Stage 7**: Enhanced Visualizations (bar charts, histograms, session statistics) ✓
- **Stage 8**: Time Estimation & Reporting ✓
- **Stage 9**: Performance Optimization & Chart Enhancements ✓
- **Stage 10**: Strategy Editor Fixes & Mimic-the-Dealer ✓

## Version History

- **v0.10 (Current)** - Stage 10: Strategy Editor Fixes & Mimic-the-Dealer - COMPLETE
  - Fixed "Use in Simulation" flow: server-side URL param detection with inline script injection
  - Added "Quick Test" button to strategy editor (10K hands, shows EV inline)
  - Added mimic-the-dealer strategy (~-6% EV baseline comparison)
  - Fixed strategy dropdown ordering (H17 basic strategy always first, then alphabetical)
  - Updated version numbers on both pages (v0.5 → v0.9)
  - Added cache-busting query strings to script tags

- **v0.9** - Stage 9: Performance Optimization & Chart Enhancements - COMPLETE
  - 1.57x simulation speedup (50K hands: 1.13s → 0.72s, ~70K hands/sec)
    - Card: pre-computed numeric values, `__slots__`, frozenset validation
    - Hand: cached value/soft calculations with dirty-flag invalidation
    - Shoe: reuse Card objects across reshuffles, integer threshold comparison
  - Session histogram always breaks at 0 (no mixed win/loss bins)
  - Payout labels on both charts (abbreviated format above bars + in tooltips)
  - Input limits increased 10x: 10M hands/session, 100K sessions, 100M total
  - Time estimation calibration increased (5K hands / 10-50 sessions) for <1% accuracy

- **v0.8** - Stage 8: Time Estimation & Reporting - COMPLETE
  - Pre-simulation time estimates: calibration-based prediction shown inline next to total hands
  - Elapsed time reporting in results summary (stat card + CLI output)
  - New `/api/estimate` endpoint for time prediction before simulation starts
  - Best/worst session added to session statistics table
  - Fixed performance bug: disabled unnecessary hand tracking that generated 45MB JSON responses
  - Estimate accuracy: ~1-3% error via linear extrapolation from calibration run
  - Full server-side timing (includes strategy loading and response building)

- **v0.7** - Stage 7: Enhanced Visualizations - COMPLETE
  - Replaced pie charts with more informative visualizations:
    - Hand outcomes: Sorted descending bar chart
    - Session outcomes: Histogram with optimal binning (Sturges' rule)
  - Added comprehensive session statistics table:
    - Percentiles: P10, P25, P50 (median), P75, P90
    - Mean and standard deviation
    - Descriptive explanations for each metric
  - Reorganized results UI into two clear sections:
    - Session-Level Analysis (variance and distribution)
    - Hand-Level Analysis (detailed outcome breakdown)
  - Enhanced color coding:
    - Profit/loss indicators on histogram (green/red/gray)
    - Distinct colors for each hand outcome type
  - Improved information architecture for better user understanding

- **v0.6** - Stage 6: Split Implementation & Strategy Verification - COMPLETE
  - Complete split/re-split logic with up to 4 hands
  - Split aces handling (one card only, correct casino rules)
  - Double after split support (configurable)
  - Individual hand tracking with bet/payout aggregation
  - Action history tracking for each hand
  - Debug mode with strategy categorization:
    - Categorizes by initial 2-card hand (hard/soft/pair)
    - Shows complete action sequence for each hand
    - Split hands displayed separately with individual bets/payouts
    - Dealer final value shown for comparison
  - Fixed action tracking bugs:
    - Actions now attributed to correct hand
    - Records actual actions taken (not just requested)
    - Both split hands properly show "split" action
  - EV calculations now accurate (~-0.5% for optimal basic strategy vs previous -0.7%)

- **v0.5** - Stage 5: Web Interface - COMPLETE
  - FastAPI backend with 5 REST endpoints (defaults, simulate, strategies list/detail)
  - Interactive web UI with comprehensive parameter control
  - Dual Chart.js visualizations:
    - Hand-level outcome distribution (7 categories: blackjacks, double wins/losses, regular wins/losses, surrenders, pushes)
    - Session-level outcome distribution (winning/losing/break-even sessions for variance analysis)
  - Hierarchical breakdown table with payout calculations
    - Indented sub-categories showing composition of wins/losses/pushes
    - Per-category payout totals in betting units
  - Visual strategy editor for creating and editing custom strategies
  - Download results as JSON or CSV
  - Custom strategy support (localStorage + JSON import/export)
  - Deployment-ready (Procfile for Railway/Render)
  - 12 new API endpoint tests (139 total tests)
  - Full API documentation at /docs (FastAPI auto-generated)

- **v0.4** - Stage 4: Results & Analysis - COMPLETE
  - Results export system (reporter.py)
  - CSV export: summary, sessions, and hand samples
  - JSON export for web API consumption
  - Optional hand tracking with configurable sampling
  - 127 passing unit tests (12 new tests for reporter)
  - Demo script showing all export functionality

- **v0.3** - Stage 3: Strategy & Simulation - COMPLETE
  - JSON-based strategy system with full basic strategy
  - Strategy comparison framework (basic vs never-bust vs always-stand)
  - Single and multi-session simulation engine
  - Variance analysis across sessions
  - 115 passing unit tests
  - Demo results: Basic strategy ~-1% EV, Never-bust ~-5% EV

- **v0.2** - Stage 2: Core Game Logic - COMPLETE
  - Complete blackjack game engine
  - 74 passing unit tests
  - Support for infinite deck (CSM)
  - Configurable game rules (H17/S17, surrender, payouts)
  - Player actions: hit, stand, double, surrender
  - Demo scripts for all modules

- **v0.1** - Stage 1: Foundation & Documentation - COMPLETE
  - Project structure created
  - Documentation initialized (including web interface plan)
  - Git repository configured
