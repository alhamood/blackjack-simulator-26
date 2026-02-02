#!/usr/bin/env python3
"""
Generate Strategy Reference Data

Runs definitive simulations for all strategies and stores results
as a static JSON file for the web reference page.

Reads the convergence analysis results to determine hand count.

Output: web/static/data/strategy_reference.json
"""

import sys
import json
import time
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.simulator import Simulator
from src.game import GameRules
from src.player import Strategy

# Default hand count (overridden by convergence results if available)
DEFAULT_HANDS = 10_000_000
PENETRATION = 0.75

STRATEGIES_DIR = Path("config/strategies")
CONVERGENCE_PATH = Path("results/ev_convergence.json")
OUTPUT_PATH = Path("web/static/data/strategy_reference.json")

# Standard 6-deck H17 config for cross-testing
STANDARD_CONFIG = {
    "num_decks": 6,
    "dealer_hits_soft_17": True,
    "surrender_allowed": True,
    "double_after_split": True,
    "blackjack_payout": 1.5,
}


def create_strategy_func(strategy):
    """Create strategy wrapper function."""
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


def parse_deck_count(decks_str):
    """Map strategy rules.decks to a num_decks integer."""
    mapping = {"1": 1, "2": 2, "4+": 6, "4-8": 6}
    if decks_str in mapping:
        return mapping[decks_str]
    try:
        return int(decks_str)
    except (ValueError, TypeError):
        return 6  # default


def parse_bool(val, default=True):
    """Parse a bool that might be a string or None."""
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        return val.lower() not in ("false", "no", "0")
    return default


def get_natural_config(strategy_data):
    """Extract the natural configuration from strategy metadata."""
    rules = strategy_data.get("rules", {})
    num_decks = parse_deck_count(rules.get("decks", "6"))
    h17 = parse_bool(rules.get("dealer_hits_soft_17", True))
    surrender = parse_bool(rules.get("surrender_allowed", True))
    das = parse_bool(rules.get("double_after_split", True))
    bj_raw = rules.get("blackjack_payout", 1.5)
    try:
        bj_payout = float(bj_raw)
    except (ValueError, TypeError):
        bj_payout = 1.5  # default for "any" or invalid values

    return {
        "num_decks": num_decks,
        "dealer_hits_soft_17": h17,
        "surrender_allowed": surrender,
        "double_after_split": das,
        "blackjack_payout": bj_payout,
    }


def config_label(config):
    """Generate a short label for a config."""
    decks = config["num_decks"]
    dealer = "H17" if config["dealer_hits_soft_17"] else "S17"
    return f"{decks}-deck {dealer}"


def configs_match(a, b):
    """Check if two configs are equivalent."""
    return (
        a["num_decks"] == b["num_decks"]
        and a["dealer_hits_soft_17"] == b["dealer_hits_soft_17"]
        and a["surrender_allowed"] == b["surrender_allowed"]
        and a["double_after_split"] == b["double_after_split"]
        and a["blackjack_payout"] == b["blackjack_payout"]
    )


def run_simulation(strategy_path, config, total_hands):
    """Run a simulation and return result dict."""
    strategy = Strategy(str(strategy_path))
    strategy_func = create_strategy_func(strategy)

    rules = GameRules(
        dealer_hits_soft_17=config["dealer_hits_soft_17"],
        surrender_allowed=config["surrender_allowed"],
        double_after_split=config["double_after_split"],
        blackjack_payout=config["blackjack_payout"],
    )
    sim = Simulator(
        rules=rules,
        num_decks=config["num_decks"],
        penetration=PENETRATION
    )

    t0 = time.perf_counter()
    result = sim.run_simulation(total_hands, strategy_func, num_sessions=1)
    elapsed = time.perf_counter() - t0

    return {
        "total_hands": result.total_hands,
        "ev_per_hand": round(result.ev_per_hand, 8),
        "ev_percent": round(result.ev_per_hand * 100, 4),
        "house_edge_percent": round(-result.ev_per_hand * 100, 4),
        "win_rate": round(result.win_count / result.total_hands, 6) if result.total_hands > 0 else 0,
        "blackjack_rate": round(result.blackjack_count / result.total_hands, 6) if result.total_hands > 0 else 0,
        "bust_rate": round(result.bust_count / result.total_hands, 6) if result.total_hands > 0 else 0,
        "surrender_rate": round(result.surrender_count / result.total_hands, 6) if result.total_hands > 0 else 0,
        "double_rate": round(result.double_count / result.total_hands, 6) if result.total_hands > 0 else 0,
        "split_rate": round(result.split_count / result.total_hands, 6) if result.total_hands > 0 else 0,
        "push_rate": round(result.push_count / result.total_hands, 6) if result.total_hands > 0 else 0,
        "loss_rate": round(result.loss_count / result.total_hands, 6) if result.total_hands > 0 else 0,
        "elapsed_seconds": round(elapsed, 2),
    }


def get_hands_from_convergence():
    """Read convergence results to determine hand count."""
    if CONVERGENCE_PATH.exists():
        with open(CONVERGENCE_PATH) as f:
            data = json.load(f)
        rec = data.get("recommendation", {})
        min_hands = rec.get("min_hands_for_convergence")
        if min_hands:
            print(f"Using hand count from convergence analysis: {min_hands:,}")
            return min_hands
    print(f"No convergence data found, using default: {DEFAULT_HANDS:,}")
    return DEFAULT_HANDS


def main():
    parser = argparse.ArgumentParser(description="Generate strategy reference data")
    parser.add_argument("--hands", type=int, default=None,
                        help="Number of hands per simulation (overrides convergence result)")
    args = parser.parse_args()

    total_hands = args.hands if args.hands else get_hands_from_convergence()

    print("=" * 60)
    print("Strategy Reference Data Generation")
    print("=" * 60)
    print(f"Hands per simulation: {total_hands:,}")
    print()

    strategy_files = sorted(STRATEGIES_DIR.glob("*.json"))
    print(f"Found {len(strategy_files)} strategies")
    print()

    total_start = time.perf_counter()
    all_results = []

    for strategy_file in strategy_files:
        strategy_id = strategy_file.stem
        with open(strategy_file) as f:
            strat_data = json.load(f)

        strategy_name = strat_data.get("name", strategy_id)
        natural_config = get_natural_config(strat_data)

        # Run with natural config
        label = config_label(natural_config)
        print(f"[{len(all_results) + 1}] {strategy_name} @ {label} (natural)")
        result = run_simulation(strategy_file, natural_config, total_hands)
        all_results.append({
            "strategy_id": strategy_id,
            "strategy_name": strategy_name,
            "config": natural_config,
            "config_label": label,
            "is_natural_config": True,
            "results": result,
        })
        print(f"    EV: {result['ev_percent']:+.4f}%  "
              f"House Edge: {result['house_edge_percent']:.4f}%  "
              f"({result['elapsed_seconds']:.1f}s)")

        # Cross-test with standard 6-deck H17 if different
        if not configs_match(natural_config, STANDARD_CONFIG):
            label = config_label(STANDARD_CONFIG)
            print(f"[{len(all_results) + 1}] {strategy_name} @ {label} (cross-test)")
            result = run_simulation(strategy_file, STANDARD_CONFIG, total_hands)
            all_results.append({
                "strategy_id": strategy_id,
                "strategy_name": strategy_name,
                "config": STANDARD_CONFIG,
                "config_label": label,
                "is_natural_config": False,
                "results": result,
            })
            print(f"    EV: {result['ev_percent']:+.4f}%  "
                  f"House Edge: {result['house_edge_percent']:.4f}%  "
                  f"({result['elapsed_seconds']:.1f}s)")

        print()

    total_elapsed = time.perf_counter() - total_start

    # Load convergence summary if available
    convergence_summary = None
    if CONVERGENCE_PATH.exists():
        with open(CONVERGENCE_PATH) as f:
            conv_data = json.load(f)
        convergence_summary = {
            "levels": [
                {
                    "hand_count": level["hand_count"],
                    "ev_mean_percent": round(level["ev_mean"] * 100, 4),
                    "ev_stdev_percent": level["ev_stdev_percent"],
                    "ev_range_percent": level["ev_range_percent"],
                    "converged": level["converged"],
                }
                for level in conv_data["levels"]
            ],
            "recommendation": conv_data["recommendation"],
            "metadata": conv_data["metadata"],
        }

    output = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "hands_per_simulation": total_hands,
            "total_simulations": len(all_results),
            "total_elapsed_minutes": round(total_elapsed / 60, 1),
        },
        "convergence": convergence_summary,
        "results": all_results,
    }

    # Write output
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=2)

    print("=" * 60)
    print(f"Total elapsed: {total_elapsed / 60:.1f} minutes")
    print(f"Simulations run: {len(all_results)}")
    print(f"Output saved to: {OUTPUT_PATH}")
    print("=" * 60)


if __name__ == "__main__":
    main()
