# Blackjack Simulator - Project Context

**Last Updated:** 2026-02-02
**Project Status:** v0.12 - Betting Strategies & 6:5 Reference Data
**Repository:** Public GitHub repository (alhamood/blackjack-simulator-26)
**Live Site:** Deployed on AWS Lightsail (blackjack.hamood.com, pending DNS/SSL)

---

## Project Overview

A Python-based blackjack simulator designed to test various playing strategies and betting systems against different game conditions. The simulator runs up to 100M hands to provide statistical analysis of strategy performance.

### Key Capabilities

1. **Strategy Testing**: Evaluate blackjack playing strategies across up to 100M simulated hands
2. **Betting Strategies**: 7 progressive betting systems (Martingale, Fibonacci, etc.) with EV-per-unit-bet tracking
3. **Configurable Game Conditions**: Support various rule variations (H17/S17, surrender, DAS, 3:2/6:5 BJ payout)
4. **Flexible Deck Configurations**: Support 1-8 physical decks or infinite deck (CSM) simulation
5. **Web Interface**: Full web UI for running simulations, editing strategies, and viewing reference data
6. **Strategy Reference**: Pre-computed EV data for all strategies at 100M hands (3:2 and 6:5 payouts)
7. **Results Export**: Output results as CSV or JSON

---

## Technical Architecture

### Project Structure

```
blackjack-simulator-26/
├── README.md                    # User-facing documentation
├── PROJECT_CONTEXT.md           # This file - AI handoff context
├── NEXT_STEPS.md                # Future enhancements roadmap
├── requirements.txt             # Python dependencies (FastAPI, uvicorn, pydantic)
├── config/
│   ├── game_rules.json          # Default game conditions
│   ├── strategies/              # 10 playing strategy JSON files
│   │   ├── basic_strategy_h17.json
│   │   ├── basic_strategy_s17.json
│   │   ├── basic_strategy_single_deck_H17.json
│   │   ├── basic_strategy_single_deck_S17.json
│   │   ├── basic_strategy_double_deck_H17.json
│   │   ├── basic_strategy_double_deck_S17.json
│   │   ├── basic_strategy_4to8deck_H17.json
│   │   ├── basic_strategy_4to8deck_S17.json
│   │   ├── mimic_the_dealer.json
│   │   └── never_bust.json
│   └── betting_strategies/      # 7 betting strategy JSON configs
│       ├── flat.json
│       ├── martingale.json
│       ├── reverse_martingale.json
│       ├── 1-3-2-6.json
│       ├── paroli.json
│       ├── dalembert.json
│       └── fibonacci.json
├── src/
│   ├── __init__.py
│   ├── cards.py                 # Card, Deck, Shoe classes (with perf optimizations)
│   ├── hand.py                  # Hand evaluation (cached value/soft)
│   ├── dealer.py                # Dealer behavior (H17/S17)
│   ├── player.py                # Player strategy execution from JSON
│   ├── game.py                  # Single hand game logic (accepts variable bet)
│   ├── simulator.py             # Multi-hand simulation engine (betting strategy support)
│   ├── reporter.py              # Results analysis and CSV/JSON export
│   └── betting.py               # Betting strategy system (7 progressive strategies)
├── web/
│   ├── api.py                   # FastAPI server (simulation, strategies, betting APIs)
│   └── static/
│       ├── index.html           # Main simulation page
│       ├── styles.css           # Shared styling
│       ├── app.js               # Main page logic (~1050 lines)
│       ├── strategy-editor.html # Visual strategy builder
│       ├── strategy-editor.js   # Editor logic
│       ├── strategy-reference.html # Pre-computed EV reference table
│       └── data/
│           └── strategy_reference.json  # 100M-hand reference data
├── scripts/
│   └── generate_reference_data.py  # Generate reference data (supports --hands flag)
├── deploy/
│   ├── setup.sh                 # One-shot Lightsail server setup
│   ├── blackjack.service        # systemd unit file
│   └── blackjack-nginx.conf     # nginx reverse proxy config
├── tests/
│   ├── test_cards.py
│   ├── test_hand.py
│   ├── test_dealer.py
│   ├── test_game.py
│   ├── test_player.py
│   ├── test_simulator.py
│   ├── test_reporter.py
│   ├── test_api.py
│   └── test_betting.py          # 25 tests for all betting strategies
└── results/
    └── .gitkeep
```

### Key Design Patterns

- **Playing Strategy**: JSON lookup tables mapping (player_hand, dealer_upcard) → action. Loaded by `src/player.py`.
- **Betting Strategy**: `BettingStrategy` base class with `get_bet()`, `update(outcome, payout, bet)`, `reset()` lifecycle. 7 concrete implementations in `src/betting.py`. Loaded from JSON configs via `BettingStrategy.from_json()`.
- **Simulation Pipeline**: `Simulator.run_simulation()` → `run_session()` → per-hand loop calling `BlackjackGame.play_hand()`. Betting strategy threaded through: `get_bet()` before hand, `update()` after.
- **Web API**: FastAPI with endpoints for simulation, strategies, betting strategies, defaults, and time estimation.
- **Reference Data**: Pre-computed via `scripts/generate_reference_data.py --hands 100000000`. Stored as static JSON, rendered client-side.

---

## Current State (v0.12)

### Recent Work (2026-02-01 to 2026-02-02)

**Deployment (Live):**
- AWS Lightsail instance: Ubuntu 24.04 LTS, $5/mo (2 vCPUs, 512MB RAM)
- nginx reverse proxy → uvicorn on port 8000
- systemd service for auto-restart
- App accessible via IP address; DNS pending for blackjack.hamood.com
- SSL via certbot pending DNS propagation

**Betting Strategies (Phase 1 - Complete):**
- `src/betting.py`: Base class + 7 strategies (Flat, Martingale, Reverse Martingale, 1-3-2-6, Paroli, D'Alembert, Fibonacci)
- `config/betting_strategies/`: 7 JSON config files
- `src/game.py`: Accepts variable `bet` parameter (used for split hands too)
- `src/simulator.py`: Threads betting strategy through simulation, tracks `total_wagered`, `ev_per_unit_bet`
- `web/api.py`: `/api/betting-strategies` endpoint, betting strategy in request/response
- `web/static/index.html`: Betting strategy dropdown with description text
- `web/static/app.js`: Populates dropdown, sends betting_strategy in payload, shows EV Per Unit Bet and Avg Bet Size cards for non-flat strategies
- `tests/test_betting.py`: 25 unit tests (all passing)

**100M Reference Data:**
- All 10 strategies × their configs run at 100M hands (completed in ~401 min)
- 6:5 blackjack payout variants being generated (running now, ~13 hours)
- Reference page shows BJ Pays column (3:2 / 6:5), sortable
- Convergence analysis section removed (redundant with 100M data)

**Card Counting (Phase 2 - Planned, not started):**
- Hi-Lo running/true count tracking in `Shoe`
- `CardCountingBetting` class with configurable bet spreads
- Planned per the plan file

### Test Status
- 159 passing, 3 pre-existing failures in test_api.py (unrelated to recent work)
- Pre-existing failures: `test_get_defaults` (H17 default changed), `test_simulate_invalid_strategy` (500 vs 400), `test_simulate_validation_max_hands` (limit increased)

---

## Implementation History

| Version | Stage | Description |
|---------|-------|-------------|
| v0.1 | 1 | Foundation & documentation |
| v0.2 | 2 | Core game logic (cards, hand, dealer, game) - 74 tests |
| v0.3 | 3 | Strategy & simulation engine - 115 tests |
| v0.4 | 4 | Results export (CSV, JSON) - 127 tests |
| v0.5 | 5 | Web interface (FastAPI + static frontend) - 139 tests |
| v0.6 | 6 | Split implementation & strategy verification |
| v0.7 | 7 | Enhanced visualizations (bar charts, histograms) |
| v0.8 | 8 | Time estimation & elapsed time reporting |
| v0.9 | 9 | Performance optimization (1.57x speedup) & chart enhancements |
| v0.10 | 10 | Strategy editor fixes & mimic-the-dealer |
| v0.11 | 11 | EV convergence analysis, strategy reference page, deck-specific strategies |
| v0.12 | 12 | Deployment, betting strategies, 100M reference data, 6:5 variants |

---

## Development Environment

**Platform:** macOS (Darwin 25.2.0)
**Python Version:** 3.9.12
**Working Directory:** /Users/alberthamood/projects/blackjack-simulator-26

**Deployment:**
- AWS Lightsail: Ubuntu 24.04 LTS, $5/mo
- Domain: hamood.com (Namecheap), subdomain blackjack.hamood.com
- DNS: Namecheap BasicDNS, A record pointing to Lightsail IP
- Server setup: `deploy/setup.sh` (one-shot script)
- Update server: `sudo git -C /opt/blackjack pull && sudo systemctl restart blackjack`

---

## Notes for AI Handoffs

**User (alhamood):**
- Data scientist background, not a software engineer
- Prefers Python and straightforward solutions
- Values clear documentation and simple code
- Working across multiple AI sessions
- Has AWS Lightsail server running the app

**Key files to read first:**
1. This file (PROJECT_CONTEXT.md) for overview
2. `src/betting.py` for betting strategy pattern
3. `src/simulator.py` for simulation pipeline
4. `web/api.py` for API endpoints
5. `.claude/plans/merry-marinating-rainbow.md` for betting strategy plan (Phase 2 pending)

**Active background task:**
- 100M simulation with 6:5 variants running locally (`reference_65.log`)
- When complete, `web/static/data/strategy_reference.json` needs to be committed/pushed and pulled on server
