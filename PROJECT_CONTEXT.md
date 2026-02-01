# Blackjack Simulator - Project Context

**Last Updated:** 2026-01-31
**Project Status:** Stage 10 - Strategy Editor Fixes & Mimic-the-Dealer (COMPLETE)
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

### Stage 5: Web Interface (COMPLETE)
**Status**: ✓ COMPLETE (2026-01-31)
**Goal**: Build comprehensive web UI with custom strategy editor

**Completed:**
- ✓ web/api.py: FastAPI server with 5 endpoints (323 lines)
  - GET /api/defaults - Default parameters and available strategies
  - POST /api/simulate - Run simulation with custom or predefined strategies
  - GET /api/strategies - List all available strategies
  - GET /api/strategies/{id} - Get full strategy JSON for editing
  - Static file serving for frontend
- ✓ web/static/index.html: Main simulation page (203 lines)
  - Comprehensive configuration form (game rules, shoe, simulation)
  - Results display with summary stats and dual chart visualization
  - Hierarchical breakdown table with payout analysis
  - Loading spinner and error handling
  - Download buttons for JSON/CSV export
- ✓ web/static/strategy-editor.html: Visual strategy builder (167 lines)
  - Strategy metadata (name, description)
  - Three strategy tables (hard totals, soft totals, pairs)
  - Load existing strategies, reset, save, use in simulation
- ✓ web/static/styles.css: Responsive styling (421 lines)
  - Clean layout with CSS Grid/Flexbox for dual charts
  - Color-coded stat cards (positive/negative EV)
  - Hierarchical table styling with indentation
  - Mobile-responsive design
  - Loading animations and error message styling
- ✓ web/static/app.js: Main page logic (565 lines)
  - Load defaults from API
  - Form submission and validation
  - Dual Chart.js visualizations (hand outcomes + session outcomes)
  - Hierarchical results table with payout calculations
  - Download as JSON/CSV
  - Custom strategy support from localStorage
- ✓ web/static/strategy-editor.js: Strategy editor logic (334 lines)
  - Dynamic table generation (Hard: 17 rows, Soft: 9 rows, Pairs: 10 rows)
  - Load/save/reset functionality
  - Extract strategy from tables
  - localStorage integration
- ✓ Procfile: Deployment configuration
- ✓ tests/test_api.py: API endpoint tests (12 tests)
  - Test defaults, strategies list, strategy detail
  - Test simulation with various configurations
  - Test custom strategy support
  - Test validation and error handling
- ✓ requirements.txt: Updated with FastAPI, uvicorn, pydantic
- ✓ README.md: Updated with web interface documentation
- ✓ Total: ~1700 lines of new code (vs planned ~1200)

**Architecture:**
- **Backend**: FastAPI with 5 endpoints
  - `GET /api/defaults` - Return default parameters and available strategies
  - `POST /api/simulate` - Run simulation (supports custom strategy JSON)
  - `GET /api/strategies` - List available strategies with metadata
  - `GET /api/strategies/{id}` - Get full strategy JSON for editing
  - `GET /` - Serve static files
- **Frontend**: Two pages + shared assets
  - `index.html` - Main simulation page with all parameters
  - `strategy-editor.html` - Visual strategy builder
  - `app.js` - Simulation logic (~250 lines)
  - `strategy-editor.js` - Editor logic (~300 lines)
  - `styles.css` - Shared styling (~120 lines)

**Key Features:**
- Comprehensive parameter control (all game rules, shoe config, simulation options)
- Dual Chart.js visualizations:
  - Hand-level outcome distribution (blackjacks, double wins/losses, regular wins/losses, surrenders, pushes)
  - Session-level outcome distribution (winning/losing/break-even sessions)
- Hierarchical breakdown table with payout analysis by outcome category
- Download results as JSON or CSV
- **Custom strategy editor** with visual table builder:
  - Three tables: Hard totals, Soft totals, Pairs
  - Dropdowns for each cell (hit, stand, double, split, surrender, fallbacks)
  - Load existing strategies for editing
  - Save as JSON or use in simulation (localStorage)
- Cloud deployment ready (Railway/Render)

**Implementation Phases:**
1. Backend Setup - FastAPI server with all endpoints, Pydantic validation
2. Frontend Structure - Main page HTML with configuration form
3. Frontend Logic - Interactive UI, API integration, Chart.js
4. Strategy Editor - Visual strategy builder page
5. Deployment Configuration - Procfile, environment variables
6. Testing & Polish - API tests, cross-browser testing, documentation

**Files to Create:**
- `web/api.py` (~250 lines)
- `web/static/index.html` (~150 lines)
- `web/static/strategy-editor.html` (~200 lines)
- `web/static/styles.css` (~120 lines)
- `web/static/app.js` (~250 lines)
- `web/static/strategy-editor.js` (~300 lines)
- `web/Procfile` (deployment config)
- `tests/test_api.py` (~120 lines)

**Technical Notes:**
- Total scope: ~1200 lines of code
- Reuse existing `export_to_json()` format from reporter.py
- Strategy wrapper function pattern from demo_simulator.py
- Chart.js loaded from CDN (no npm)
- Custom strategies stored in localStorage or downloaded as JSON
- API auto-documentation at /docs (FastAPI feature)
- Timeout protection: 30s max per simulation

**Detailed Plan:** See `/Users/alberthamood/.claude/plans/moonlit-wobbling-leaf.md` for complete implementation plan with API specs, validation rules, and verification steps

### Stage 8: Time Estimation & Reporting (COMPLETE)
**Status**: ✓ COMPLETE (2026-01-31)
**Goal**: Add simulation time estimation and elapsed time reporting

**Completed:**
- ✓ `SimulationResult.elapsed_seconds` field with display in `summary()`
- ✓ `Simulator.estimate_time()` method: runs calibration simulation, extrapolates linearly
  - Multi-session mode: uses same hands-per-session as real run, scales by session count
  - Single-session mode: 1000-hand calibration, linear extrapolation
  - Accuracy: ~1-3% error in testing
- ✓ `POST /api/estimate` endpoint for pre-simulation time estimation
- ✓ Web UI: time estimate shown inline next to total hands count, updates on parameter changes
- ✓ Web UI: elapsed time stat card in results display
- ✓ Web UI: best/worst session in session statistics table
- ✓ API elapsed_seconds measures full request lifecycle (not just simulation)
- ✓ Fixed: disabled unnecessary `track_hands` default (was generating 45MB responses)
- ✓ Demo script: `demo_time_estimation()` in demo_simulator.py

**Key files modified:**
- `src/simulator.py` - elapsed_seconds, estimate_time(), time import
- `web/api.py` - /api/estimate endpoint, _build_simulator_and_strategy helper, full-request timing
- `web/static/app.js` - fetchTimeEstimate(), elapsed time display, best/worst session stats
- `web/static/index.html` - time-estimate span, elapsed-time stat card
- `web/static/styles.css` - .time-estimate styling
- `demo_simulator.py` - demo_time_estimation()

### Stage 9: Performance Optimization & Chart Enhancements (COMPLETE)
**Status**: ✓ COMPLETE (2026-01-31)
**Goal**: Optimize simulation performance for larger runs; improve chart visualizations

**Performance Optimizations (1.57x speedup):**
- ✓ `Card`: Pre-computed `_value` int and `is_ace` bool in `__init__` (eliminates repeated string comparisons)
  - Added `__slots__` for memory efficiency, `frozenset` for validation, `_RANK_VALUES` dict lookup
- ✓ `Hand`: Cached `value()` and `is_soft()` with dirty-flag invalidation on `add_card()`
  - Single `_recalculate()` computes both value and soft flag in one pass
  - `is_bust()` returns cached value directly (no re-traversal)
- ✓ `Shoe`: Card objects built once in `_master_cards`, reused across reshuffles (copy + shuffle only)
  - Penetration check uses pre-computed integer threshold (`cards_dealt >= threshold`)
  - Infinite shoe skips shuffle tracking entirely
- ✓ Results: 50K hands in 0.72s (was 1.13s), ~70K hands/sec throughput

**Chart Enhancements:**
- ✓ Session histogram: bins always break at 0 boundary (no mixed win/loss bins)
  - Proportional bin allocation on each side of 0
  - Clean red/green color separation
- ✓ Payout labels on both charts: abbreviated format (e.g. +1.2k, -340) above each bar
  - Color-coded: green for positive, red for negative
  - Tooltips also show total payout per bin/category
- ✓ Hand outcome chart: payout labels using estimated payouts per category
  - Uses blackjack payout value from form for accurate estimates

**Limits & Estimation:**
- ✓ Input limits increased 10x: hands per session up to 10M, sessions up to 100K, total up to 100M
  - Updated across HTML, JS validation, and API validators
- ✓ Calibration size increased: single-session 5K hands (was 1K), multi-session 10-50 sessions (was 3-10)
  - Estimate accuracy improved to <1% error

**Key files modified:**
- `src/cards.py` - Card __slots__/pre-computed values, Shoe _master_cards/threshold optimization
- `src/hand.py` - Cached value/soft with dirty flag, _recalculate()
- `src/simulator.py` - Increased calibration defaults (5K hands, 10-50 sessions)
- `web/api.py` - Increased field limits (10M hands, 100K sessions, 100M total)
- `web/static/app.js` - Zero-boundary histogram, payout labels, increased validation limits
- `web/static/index.html` - Increased max attributes on inputs

### Stage 10: Strategy Editor Fixes & Mimic-the-Dealer (COMPLETE)
**Status**: ✓ COMPLETE (2026-01-31)
**Goal**: Fix strategy editor "Use in Simulation" flow, add new strategy, improve UX

**Strategy Editor Fixes:**
- ✓ Fixed "Use in Simulation" button: now redirects to `/?strategy=custom` with server-side inline script injection
  - Server detects `?strategy=custom` URL param and injects `<script>` to auto-select custom strategy
  - Eliminates browser caching issues with external JS files
  - Custom strategy data passed via localStorage, selection triggered via injected inline script with 500ms delay
- ✓ Added "Quick Test" button: runs 10K-hand simulation inline and shows EV result
  - Uses standard game rules (6-deck, H17, surrender, DAS, 3:2 BJ)
  - Color-coded result (green/red) displayed next to button
- ✓ Fixed strategy dropdown ordering: `basic_strategy_h17` always appears first
  - `glob()` returns non-deterministic order; added explicit sort in both `/api/defaults` and `/api/strategies`
- ✓ Updated version numbers: both index.html and strategy-editor.html updated from v0.5 to v0.9
- ✓ Added cache-busting query strings to `<script>` tags (`?v=0.9.1`)

**New Strategy:**
- ✓ Added `mimic_the_dealer.json`: hit on hard ≤16, hit soft 17, stand hard 17+, no doubles/splits/surrenders
  - Tested at ~-6.27% EV (baseline comparison strategy)

**Key files modified:**
- `web/api.py` - Server-side `?strategy=custom` handling with inline script injection, strategy sort order
- `web/static/app.js` - Custom strategy auto-selection logic, `checkForCustomStrategy()` cleanup
- `web/static/strategy-editor.js` - `useInSimulation()` redirect with URL param, `quickTest()` function
- `web/static/strategy-editor.html` - Quick test button, version update, cache-busting script tag
- `web/static/index.html` - Version update, cache-busting script tag
- `config/strategies/mimic_the_dealer.json` - New strategy file

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
