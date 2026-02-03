# Next Steps for Blackjack Simulator

**Last Updated:** 2026-02-02

## Completed

### 6:5 Reference Data Generation ✓
- 100M-hand simulations for all strategies with 6:5 blackjack payout
- Reference entries doubled from 16 to 32
- Pushed to production 2026-02-02

### DNS/SSL Setup ✓
- Domain: blackjack.hamood.com on Lightsail

## Priority 1: Card Counting Betting (Phase 2)

Per the plan in `.claude/plans/merry-marinating-rainbow.md`:

### Step 1: Add count tracking to Shoe (`src/cards.py`)
- `running_count` field, updated in `deal_card()` using Hi-Lo values (2-6: +1, 7-9: 0, 10-A: -1)
- `true_count` property (running_count / decks_remaining)
- Reset count on shuffle/rebuild

### Step 2: Add CardCountingBetting class (`src/betting.py`)
- Has reference to shoe (set via `set_shoe()`)
- `get_bet()` reads `shoe.true_count`, maps to bet via configurable spread
- Default spread: TC<=1 → 1 unit, TC=2 → 2, TC=3 → 4, TC>=4 → 8

### Step 3: Add configs (`config/betting_strategies/`)
- `hi_lo_1_8.json` — aggressive spread (1-2-4-8)
- `hi_lo_1_4.json` — conservative spread (1-2-3-4)

### Step 4: Wire shoe reference
- In `Simulator.run_session()`, after shoe creation: `betting_strategy.set_shoe(shoe)` (already scaffolded with `hasattr` check)
- Warn/block counting strategies with infinite shoe

### Verification
- Card counting should show positive EV per unit bet with basic strategy (expected result)
- Infinite shoe should disable or warn for counting strategies

## Priority 2: Fix Pre-existing Test Failures

Three tests in `tests/test_api.py` fail due to stale assertions:
1. `test_get_defaults` — expects `dealer_hits_soft_17=False`, now `True`
2. `test_simulate_invalid_strategy` — expects 400, gets 500
3. `test_simulate_validation_max_hands` — expects 422 for 2M hands, limit was raised to 100M

## Priority 3: Additional Strategies

- European no-hole-card basic strategy
- Always hit / always stand (toy comparison strategies)
- Card counting play deviations (Illustrious 18)

## Priority 4: Further Enhancements

### Statistical Analysis
- Confidence intervals for EV
- Variance decomposition
- Strategy heat maps showing EV by situation
- Streak statistics (longest winning/losing streaks, distribution of streaks)

### Custom Decks
- Ability to test modified/non-standard card decks (e.g. removed cards, extra cards)
- Useful for exploring how deck composition affects house edge

### Performance
- Background job processing for very large simulations
- Caching for common strategy simulations

### UX
- Rate limiting on API
- Strategy sharing/import via URL
- Mobile-responsive improvements
