# Next Steps for Blackjack Simulator

This document outlines planned enhancements and deployment steps for the blackjack simulator.

## Priority 1: Visualization Improvements ✓ COMPLETE

### Hand Outcomes Visualization ✓
- **Previous**: Pie chart showing distribution of hand outcomes
- **Implemented**: Column/bar chart sorted descending by count
  - X-axis: Outcome types (Blackjacks, Double Wins/Losses, Regular Wins/Losses, Surrenders, Pushes)
  - Y-axis: Count
  - Color-coded bars for visual distinction
  - Sorted left-to-right by frequency for better readability

### Session Outcomes Visualization ✓
- **Previous**: Pie chart showing winning/losing/break-even sessions
- **Implemented**: Histogram showing distribution of session-level payouts
  - X-axis: Session payout bins (using Sturges' rule for optimal bin count)
  - Y-axis: Frequency (number of sessions)
  - Color-coded: green for profitable bins, red for losing bins, gray for neutral
  - Shows full distribution shape (normal, skewed, etc.)
  - Helps visualize variance and risk

### Session Statistics Table ✓
- **Implemented**: Comprehensive session-level statistics
  - Percentiles: P10, P25, P50 (median), P75, P90
  - Mean payout per session
  - Standard deviation (volatility measure)
  - Descriptive text explaining each metric

### Layout ✓
- Reorganized into two clear sections:
  - Session-Level Analysis (histogram + statistics table)
  - Hand-Level Analysis (sorted bar chart + detailed breakdown)
- Visual separators and section headings
- Stacked vertically for easy comparison
- Responsive design maintained

## Priority 2: Performance & UX Improvements ✓ COMPLETE

### Performance Optimization ✓ COMPLETE (Stage 9)
- 1.57x simulation speedup (50K hands: 1.13s → 0.72s, ~70K hands/sec)
- Card: pre-computed `_value`/`is_ace`, `__slots__`, frozenset validation
- Hand: cached value/soft with dirty-flag invalidation in `_recalculate()`
- Shoe: reuse Card objects across reshuffles, integer threshold comparison
- Input limits increased 10x (10M hands/session, 100K sessions, 100M total)

### Chart Enhancements ✓ COMPLETE (Stage 9)
- Session histogram always breaks at 0 boundary (clean red/green separation)
- Payout labels on both charts (abbreviated format: +1.2k, -340)
- Tooltips include total payout per bin/category

### Estimated Time Display ✓ COMPLETE (Stage 8)
- Calibration-based estimation: runs small sample, extrapolates linearly
- Shown inline next to total hands count in config panel
- Updates automatically when parameters change (debounced)
- `/api/estimate` endpoint for pre-simulation prediction
- Calibration: 5K hands (single-session), 10-50 sessions (multi-session)
- Accuracy: <1% error in testing
- Elapsed time shown in results (stat card + CLI summary)
- Best/worst session stats added to session statistics table

## Priority 3: Additional Strategies

### Strategy Library Expansion
Add more default strategies for comparison:

1. **Basic Strategy Variants**
   - H17 (dealer hits soft 17) - already exists
   - S17 (dealer stands soft 17) - already exists
   - Single deck basic strategy
   - Double deck basic strategy
   - European no-hole-card basic strategy

2. **Card Counting Strategies**
   - Hi-Lo system (basic implementation)
   - Include bet ramping based on true count
   - Note: Infinite shoe should disable counting strategies

3. **Conservative Strategies**
   - Never bust (already exists as toy strategy)
   - Mimic the dealer
   - Always stand on 12+

4. **Comparison Strategies**
   - Always hit
   - Always stand
   - Random play

### Strategy Metadata
Enhance strategy files with:
- Author information
- Strategy description
- Recommended rules (decks, dealer behavior)
- Expected EV under optimal conditions
- Difficulty level (beginner/intermediate/advanced)
- Strategy type (basic/card-counting/variant)

## Priority 4: Strategy Editor Validation & Improvements

### Current State
- Visual editor exists and works
- Can create and edit custom strategies
- Can save/load strategies
- **Needs validation**: Editor functionality should be tested and potentially improved

### Planned Enhancements
1. **Validation**
   - Check all cells are filled
   - Highlight missing/invalid entries
   - Suggest common actions for cells

2. **Import/Export**
   - Import from CSV
   - Import from strategy description text
   - Export to shareable format

3. **Templates**
   - Pre-fill with basic strategy
   - Offer strategy templates (conservative, aggressive, etc.)

4. **Testing**
   - Quick test button (run 10k hands)
   - Show EV comparison vs basic strategy
   - Highlight problematic decisions

## Priority 5: Deployment to AWS

### Domain Setup
- User has domain names ready
- Need to configure DNS

### AWS Architecture Options

#### Option A: Simple (Recommended for MVP)
- **Hosting**: AWS Elastic Beanstalk
  - Automatic scaling
  - Load balancing
  - Easy deployment from Git
- **Domain**: Route 53 for DNS
- **SSL**: AWS Certificate Manager (free)
- **Cost**: ~$20-50/month depending on traffic

#### Option B: Serverless
- **API**: AWS Lambda + API Gateway
- **Frontend**: S3 + CloudFront CDN
- **Cost**: Pay per request, very cheap for low traffic
- **Complexity**: More setup, but better scaling

#### Option C: Container-based
- **Platform**: AWS ECS/Fargate
- **Frontend**: S3 + CloudFront
- **Cost**: ~$30-60/month
- **Benefits**: Better for long-running simulations

### Deployment Checklist
- [ ] Set up AWS account and IAM users
- [ ] Configure Route 53 for domain
- [ ] Set up SSL certificate
- [ ] Create deployment pipeline (GitHub Actions?)
- [ ] Set up monitoring (CloudWatch)
- [ ] Configure auto-scaling based on CPU/memory
- [ ] Add error tracking (Sentry or AWS X-Ray)
- [ ] Set up backup/restore for user strategies
- [ ] Create staging environment for testing
- [ ] Document deployment process

### Pre-deployment Tasks
- [ ] Add rate limiting to API
- [ ] Add input validation and sanitization
- [ ] Add error handling for edge cases
- [ ] Optimize simulation performance
- [ ] Add request logging
- [ ] Create health check endpoint
- [ ] Add API versioning
- [ ] Write deployment documentation

## Future Enhancements (Lower Priority)

### Betting Strategies
A significant enhancement would be to support different betting strategies beyond flat betting:

1. **Fixed Betting Systems**
   - Flat betting (current implementation - 1 unit per hand)
   - Fixed percentage of bankroll
   - Fixed amount per session

2. **Progressive Systems**
   - Martingale (double after loss)
   - Reverse Martingale (double after win)
   - D'Alembert (increase/decrease by 1 unit)
   - Fibonacci progression
   - Labouchere system

3. **Card Counting Based**
   - Hi-Lo true count betting ramp
   - Kelly Criterion with running count
   - Wong halves with bet spread

4. **Risk-Adjusted**
   - Kelly Criterion (optimal bet sizing)
   - Fractional Kelly (conservative variant)
   - Fixed risk of ruin percentage

**Implementation Considerations:**
- Add `BettingStrategy` class separate from playing strategy
- Track bankroll across sessions (currently each session is independent)
- Add risk of ruin calculations
- Show betting statistics (average bet, max bet, bet spread)
- Warn about gambler's fallacy for non-card-counting systems
- Educational content explaining why most systems don't change house edge

**Complexity:** High - requires architectural changes to track bankroll state, session dependencies, and potentially bet-level tracking rather than just hand-level.

### Advanced Features
- User accounts and saved simulations
- Strategy sharing community
- Comparative analysis (multiple strategies side-by-side)
- Risk of ruin calculator with different betting strategies
- Bankroll management tools and simulators

### Statistical Analysis
- Confidence intervals for EV
- Variance decomposition
- Hand-by-hand analysis
- Strategy heat maps showing EV by situation
- Monte Carlo confidence bands

### Performance
- Caching for common strategy simulations
- Database for storing results
- Background job processing for very large simulations
- Parallel processing for multi-strategy comparisons

### Mobile
- Progressive Web App (PWA)
- Touch-optimized interface
- Offline capability
- Mobile-first charts and tables

## Timeline (Tentative)

### Week 1-2: Visualization & Performance
- Replace pie charts with column charts and histograms
- Implement warning system for large simulations
- Add progress bar for long-running simulations

### Week 3: Strategy Expansion
- Add 5-10 additional default strategies
- Enhance strategy metadata
- Improve strategy editor validation

### Week 4: Deployment Preparation
- Security hardening
- Performance optimization
- Deployment documentation
- Staging environment setup

### Week 5+: AWS Deployment
- DNS configuration
- Elastic Beanstalk setup
- SSL configuration
- Production deployment
- Monitoring and logging setup

## Notes

- All changes should maintain backward compatibility
- Keep core simulation logic separate from web interface
- Maintain comprehensive test coverage
- Document all new features and API changes
- Consider internationalization for future expansion
