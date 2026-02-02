# Blackjack Simulator

A Python-based blackjack simulator for testing playing strategies and betting systems against configurable game conditions. Runs up to 100M simulated hands with statistical analysis.

## Live Demo

Deployed at [blackjack.hamood.com](https://blackjack.hamood.com) (AWS Lightsail).

## Features

- **10 playing strategies** including basic strategy variants for 1, 2, 4-8 decks (H17/S17)
- **7 betting strategies**: Flat, Martingale, Reverse Martingale, 1-3-2-6, Paroli, D'Alembert, Fibonacci
- **Configurable rules**: dealer H17/S17, surrender, double after split, 3:2 or 6:5 blackjack payout
- **1-8 deck shoes** or infinite deck (CSM) simulation
- **Web UI** with charts, strategy editor, and pre-computed reference data
- **100M-hand reference table** comparing all strategies at both 3:2 and 6:5 payouts
- **Export** results as JSON or CSV

## Quick Start

```bash
git clone https://github.com/alhamood/blackjack-simulator-26.git
cd blackjack-simulator-26
pip install -r requirements.txt
uvicorn web.api:app --reload
```

Open [http://localhost:8000](http://localhost:8000).

## Project Structure

```
src/
├── cards.py          # Card, Deck, Shoe (with performance optimizations)
├── hand.py           # Hand evaluation (cached)
├── dealer.py         # Dealer behavior (H17/S17)
├── player.py         # Playing strategy from JSON lookup tables
├── game.py           # Single hand game logic
├── simulator.py      # Multi-hand simulation engine
├── reporter.py       # CSV/JSON export
└── betting.py        # 7 progressive betting strategies

web/
├── api.py            # FastAPI server
└── static/
    ├── index.html                # Main simulation page
    ├── strategy-editor.html      # Visual strategy builder
    ├── strategy-reference.html   # Pre-computed EV reference table
    ├── app.js, styles.css        # Frontend assets
    └── data/strategy_reference.json  # 100M-hand reference data

config/
├── strategies/           # 10 playing strategy JSON files
└── betting_strategies/   # 7 betting strategy JSON configs

deploy/                   # AWS Lightsail deployment configs
scripts/                  # Reference data generation
tests/                    # Unit tests (159 passing)
```

## Web Interface

### Main Simulator
Configure game rules, shoe, playing strategy, and betting strategy. Run simulations up to 100M hands. Results include:
- EV, win rate, total payout
- EV per unit bet and average bet size (for non-flat betting strategies)
- Session-level histogram with statistics (percentiles, std dev)
- Hand-level outcome distribution chart
- Debug mode for strategy verification

### Strategy Editor
Visual table builder for creating custom playing strategies (hard totals, soft totals, pairs). Load existing strategies, quick-test EV, and use directly in simulation.

### Strategy Reference
Pre-computed EV data for all 10 strategies across their natural configurations, with 6:5 blackjack payout variants. Sortable table with 100M-hand precision.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/defaults` | GET | Default parameters and available strategies |
| `/api/simulate` | POST | Run simulation with custom parameters |
| `/api/estimate` | POST | Pre-simulation time estimate |
| `/api/strategies` | GET | List playing strategies |
| `/api/strategies/{id}` | GET | Get strategy JSON |
| `/api/betting-strategies` | GET | List betting strategies |
| `/docs` | GET | Interactive API docs (Swagger) |

## Betting Strategies

| Strategy | Description |
|----------|-------------|
| Flat | Always bet 1 unit (default) |
| Martingale | Double after loss, reset after win |
| Reverse Martingale | Double after win, reset after loss |
| 1-3-2-6 | Cycle through 1-3-2-6 units on consecutive wins |
| Paroli | Double after win, reset after 3 wins or any loss |
| D'Alembert | +1 unit after loss, -1 unit after win |
| Fibonacci | Follow Fibonacci sequence on losses, step back 2 on win |

Progressive betting systems change variance but do not change EV per unit bet.

## Running Tests

```bash
pytest tests/ -v
```

159 passing tests covering all modules including 25 betting strategy tests.

## Deployment

Deployed on AWS Lightsail ($5/mo). See `deploy/` for configs.

Update the live server:
```bash
sudo git -C /opt/blackjack pull
sudo systemctl restart blackjack
```

## Version History

- **v0.12** - Betting strategies, AWS deployment, 100M reference data with 6:5 variants
- **v0.11** - EV convergence analysis, strategy reference page, deck-specific strategies
- **v0.10** - Strategy editor fixes, mimic-the-dealer strategy
- **v0.9** - Performance optimization (1.57x speedup), chart enhancements
- **v0.8** - Time estimation and elapsed time reporting
- **v0.7** - Enhanced visualizations (histograms, session statistics)
- **v0.6** - Split implementation and strategy verification
- **v0.5** - Web interface (FastAPI + static frontend)
- **v0.4** - Results export (CSV, JSON)
- **v0.3** - Strategy & simulation engine
- **v0.2** - Core game logic
- **v0.1** - Foundation & documentation
