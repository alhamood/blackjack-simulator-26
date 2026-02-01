#!/usr/bin/env python3
"""
EV Convergence Analysis

Determines how many hands are needed for EV estimates to converge by running
simulations at increasing hand counts with multiple independent trials.

Output: results/ev_convergence.json
"""

import sys
import json
import time
import statistics
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.simulator import Simulator
from src.game import GameRules
from src.player import Strategy

# Configuration
HAND_COUNTS = [10_000, 50_000, 100_000, 500_000, 1_000_000, 5_000_000, 10_000_000]
NUM_TRIALS = 10
CONVERGENCE_THRESHOLD = 0.0001  # 0.01% in decimal EV

STRATEGY_PATH = "config/strategies/basic_strategy_h17.json"
NUM_DECKS = 6
PENETRATION = 0.75


def create_strategy_func(strategy):
    """Create strategy wrapper function (same pattern as web/api.py)."""
    def strategy_func(player_hand, dealer_upcard):
        can_double = len(player_hand) == 2
        can_surrender = len(player_hand) == 2
        can_split = player_hand.is_pair() and len(player_hand) == 2
        return strategy.get_action(
            player_hand, dealer_upcard,
            can_double=can_double,
            can_surrender=can_surrender,
            can_split=can_split
        )
    return strategy_func


def main():
    print("=" * 60)
    print("EV Convergence Analysis")
    print("=" * 60)
    print(f"Strategy: {STRATEGY_PATH}")
    print(f"Config: {NUM_DECKS}-deck, H17, surrender, DAS, 3:2 BJ")
    print(f"Hand counts: {[f'{h:,}' for h in HAND_COUNTS]}")
    print(f"Trials per level: {NUM_TRIALS}")
    print(f"Convergence threshold: {CONVERGENCE_THRESHOLD * 100:.2f}% stdev")
    print()

    strategy = Strategy(STRATEGY_PATH)
    strategy_func = create_strategy_func(strategy)
    rules = GameRules(
        dealer_hits_soft_17=True,
        surrender_allowed=True,
        double_after_split=True,
        blackjack_payout=1.5
    )

    total_start = time.perf_counter()
    levels = []

    for hand_count in HAND_COUNTS:
        print(f"--- {hand_count:,} hands per trial ---")
        trial_results = []

        for trial_num in range(1, NUM_TRIALS + 1):
            sim = Simulator(
                rules=rules,
                num_decks=NUM_DECKS,
                penetration=PENETRATION
            )
            t0 = time.perf_counter()
            result = sim.run_simulation(hand_count, strategy_func, num_sessions=1)
            elapsed = time.perf_counter() - t0

            ev = result.ev_per_hand
            trial_results.append({
                "trial": trial_num,
                "ev": round(ev, 8),
                "elapsed_seconds": round(elapsed, 3)
            })
            print(f"  Trial {trial_num:2d}: EV = {ev * 100:+.4f}%  ({elapsed:.1f}s)")

        # Compute statistics
        evs = [t["ev"] for t in trial_results]
        ev_mean = statistics.mean(evs)
        ev_stdev = statistics.stdev(evs) if len(evs) > 1 else 0.0
        ev_min = min(evs)
        ev_max = max(evs)
        ev_range = ev_max - ev_min
        converged = ev_stdev < CONVERGENCE_THRESHOLD

        level_data = {
            "hand_count": hand_count,
            "trials": trial_results,
            "ev_mean": round(ev_mean, 8),
            "ev_stdev": round(ev_stdev, 8),
            "ev_stdev_percent": round(ev_stdev * 100, 6),
            "ev_min": round(ev_min, 8),
            "ev_max": round(ev_max, 8),
            "ev_range": round(ev_range, 8),
            "ev_range_percent": round(ev_range * 100, 6),
            "converged": converged
        }
        levels.append(level_data)

        status = "CONVERGED" if converged else "not converged"
        print(f"  => Mean: {ev_mean * 100:+.4f}%  Stdev: {ev_stdev * 100:.4f}%  "
              f"Range: {ev_range * 100:.4f}%  [{status}]")
        print()

    total_elapsed = time.perf_counter() - total_start

    # Determine recommendation
    min_hands = None
    for level in levels:
        if level["converged"]:
            min_hands = level["hand_count"]
            break

    recommendation = {
        "min_hands_for_convergence": min_hands,
        "threshold_used": CONVERGENCE_THRESHOLD,
        "threshold_percent": CONVERGENCE_THRESHOLD * 100,
    }
    if min_hands:
        recommendation["note"] = (
            f"EV stdev drops below {CONVERGENCE_THRESHOLD * 100:.2f}% "
            f"at {min_hands:,} hands"
        )
    else:
        recommendation["note"] = (
            f"EV stdev did not drop below {CONVERGENCE_THRESHOLD * 100:.2f}% "
            f"at any tested hand count"
        )

    # Load strategy name
    with open(STRATEGY_PATH) as f:
        strat_data = json.load(f)

    output = {
        "metadata": {
            "strategy_id": Path(STRATEGY_PATH).stem,
            "strategy_name": strat_data.get("name", "Unknown"),
            "rules": {
                "num_decks": NUM_DECKS,
                "dealer_hits_soft_17": True,
                "surrender_allowed": True,
                "double_after_split": True,
                "blackjack_payout": 1.5,
                "penetration": PENETRATION
            },
            "trials_per_level": NUM_TRIALS,
            "convergence_threshold": CONVERGENCE_THRESHOLD,
            "generated_at": datetime.now().isoformat(),
            "total_elapsed_seconds": round(total_elapsed, 1)
        },
        "levels": levels,
        "recommendation": recommendation
    }

    # Write output
    output_path = Path("results/ev_convergence.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print("=" * 60)
    print(f"Total elapsed: {total_elapsed / 60:.1f} minutes")
    print(f"Recommendation: {recommendation['note']}")
    print(f"Output saved to: {output_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
