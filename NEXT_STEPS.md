# Next Steps for Blackjack Simulator

**Last Updated:** 2026-02-02

## Completed

### Streak Statistics ✓
- Added `max_win_streak` and `max_loss_streak` to SessionResult and SimulationResult
- Pushes don't break streaks (neutral outcome)
- Aggregated across sessions, exposed in API response

### Card Counting Betting ✓
- Hi-Lo count tracking in Shoe (running_count, true_count)
- HiLoCountingBetting class with configurable bet spread
- Config files: `hi_lo_1_8.json` (aggressive), `hi_lo_1_4.json` (conservative)
- Wired into simulator via `set_shoe()` method

### Test Fixes ✓
- Fixed stale assertions in `test_api.py`:
  - `dealer_hits_soft_17` default now True
  - Invalid strategy returns 500 (internal error)
  - Max hands limit is 100M

### 6:5 Reference Data Generation ✓
- 100M-hand simulations for all strategies with 6:5 blackjack payout
- Reference entries doubled from 16 to 32
- Pushed to production 2026-02-02

### DNS/SSL Setup ✓
- Domain: blackjack.hamood.com on Lightsail

## Nice-to-Have (Future)

### Custom Decks
- Ability to test modified/non-standard card decks (removed cards, extra cards)
- **Parked:** Would benefit from a custom deck editor UI, which is a larger undertaking

### Additional Strategies
- European no-hole-card basic strategy
- Always hit / always stand (toy comparison strategies)
- Card counting play deviations (Illustrious 18)

### Statistical Analysis
- Confidence intervals for EV
- Variance decomposition
- Strategy heat maps showing EV by situation

### Performance
- Background job processing for very large simulations
- Caching for common strategy simulations

### UX
- Rate limiting on API
- Strategy sharing/import via URL
- Mobile-responsive improvements
