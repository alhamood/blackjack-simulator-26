"""
Demo script showing results export functionality.

Demonstrates how to export simulation results to CSV and JSON formats.
"""

from src.simulator import Simulator
from src.game import GameRules
from src.player import Strategy
from src.reporter import export_all_csv, export_to_json
import os


def demo_basic_export():
    """Demonstrate basic CSV and JSON export."""
    print("=== Basic Export Demo ===")
    print("Running simulation with 1,000 hands...")
    print()

    # Load basic strategy
    basic = Strategy('config/strategies/basic_strategy_h17.json')
    rules = GameRules(dealer_hits_soft_17=True, surrender_allowed=True)
    sim = Simulator(rules=rules, infinite_shoe=True)

    def strategy_func(player_hand, dealer_upcard):
        can_double = len(player_hand) == 2
        can_surrender = len(player_hand) == 2
        can_split = player_hand.is_pair() and len(player_hand) == 2

        return basic.get_action(
            player_hand,
            dealer_upcard,
            can_double=can_double,
            can_surrender=can_surrender,
            can_split=can_split
        )

    # Run simulation with hand tracking
    result = sim.run_simulation(
        1000,
        strategy_func,
        num_sessions=1,
        track_hands=True,
        max_tracked_hands=100
    )

    # Export to CSV
    print("Exporting results to CSV...")
    files = export_all_csv(result, 'results/demo_basic')

    for file_type, path in files.items():
        print(f"  ✓ Created {path}")

    # Export to JSON
    json_path = 'results/demo_basic.json'
    export_to_json(result, json_path, include_hands=True)
    print(f"  ✓ Created {json_path}")
    print()

    # Show summary
    print("Simulation Summary:")
    print(f"  Total hands: {result.total_hands:,}")
    print(f"  EV per hand: {result.ev_per_hand:+.6f} ({result.ev_per_hand * 100:+.4f}%)")
    print(f"  Win rate: {result.win_rate * 100:.2f}%")
    print(f"  Hands tracked: {len(result.sessions[0].hand_results)}")
    print()


def demo_multi_session_export():
    """Demonstrate multi-session export."""
    print("=== Multi-Session Export Demo ===")
    print("Running 10 sessions of 100 hands each (1,000 total)...")
    print()

    basic = Strategy('config/strategies/basic_strategy_h17.json')
    rules = GameRules(dealer_hits_soft_17=True, surrender_allowed=True)
    sim = Simulator(rules=rules, infinite_shoe=True)

    def strategy_func(player_hand, dealer_upcard):
        can_double = len(player_hand) == 2
        can_surrender = len(player_hand) == 2
        can_split = player_hand.is_pair() and len(player_hand) == 2

        return basic.get_action(
            player_hand,
            dealer_upcard,
            can_double=can_double,
            can_surrender=can_surrender,
            can_split=can_split
        )

    # Run multi-session simulation
    result = sim.run_simulation(
        1000,
        strategy_func,
        num_sessions=10,
        track_hands=True,
        max_tracked_hands=50  # Track first 50 hands of first session
    )

    # Export to CSV (will include sessions.csv)
    print("Exporting results to CSV...")
    files = export_all_csv(result, 'results/demo_multi_session')

    for file_type, path in files.items():
        print(f"  ✓ Created {path}")

    # Export to JSON
    json_path = 'results/demo_multi_session.json'
    export_to_json(result, json_path, include_hands=False)
    print(f"  ✓ Created {json_path}")
    print()

    # Show variance stats
    print("Session Variance:")
    print(f"  Mean EV: {result.session_ev_mean:+.6f}")
    print(f"  StdDev: {result.session_ev_stdev:.6f}")
    evs = [s.ev_per_hand for s in result.sessions]
    print(f"  Best session: {max(evs):+.6f}")
    print(f"  Worst session: {min(evs):+.6f}")
    print()


def demo_large_scale_export():
    """Demonstrate export with large simulation (no hand tracking)."""
    print("=== Large-Scale Export Demo ===")
    print("Running 10,000 hands (no hand tracking for efficiency)...")
    print()

    basic = Strategy('config/strategies/basic_strategy_h17.json')
    rules = GameRules(dealer_hits_soft_17=True, surrender_allowed=True)
    sim = Simulator(rules=rules, infinite_shoe=True)

    def strategy_func(player_hand, dealer_upcard):
        can_double = len(player_hand) == 2
        can_surrender = len(player_hand) == 2
        can_split = player_hand.is_pair() and len(player_hand) == 2

        return basic.get_action(
            player_hand,
            dealer_upcard,
            can_double=can_double,
            can_surrender=can_surrender,
            can_split=can_split
        )

    # Run simulation without hand tracking
    result = sim.run_simulation(
        10000,
        strategy_func,
        num_sessions=1,
        track_hands=False  # No hand tracking for large sims
    )

    # Export to CSV (only summary, no hands)
    print("Exporting results to CSV...")
    files = export_all_csv(result, 'results/demo_large_scale')

    for file_type, path in files.items():
        print(f"  ✓ Created {path}")

    # Export to JSON
    json_path = 'results/demo_large_scale.json'
    export_to_json(result, json_path, include_hands=False)
    print(f"  ✓ Created {json_path}")
    print()

    print("Large Simulation Results:")
    print(f"  Total hands: {result.total_hands:,}")
    print(f"  EV per hand: {result.ev_per_hand:+.6f} ({result.ev_per_hand * 100:+.4f}%)")
    print(f"  Total payout: {result.total_payout:+.2f} units")
    print()


def demo_strategy_comparison_export():
    """Demonstrate exporting strategy comparison results."""
    print("=== Strategy Comparison Export Demo ===")
    print("Comparing 3 strategies (5,000 hands each)...")
    print()

    # Load strategies
    basic = Strategy('config/strategies/basic_strategy_h17.json')
    never_bust = Strategy('config/strategies/never_bust.json')

    rules = GameRules(dealer_hits_soft_17=True, surrender_allowed=True)
    sim = Simulator(rules=rules, infinite_shoe=True)

    # Create strategy functions
    def basic_func(player_hand, dealer_upcard):
        can_double = len(player_hand) == 2
        can_surrender = len(player_hand) == 2
        can_split = player_hand.is_pair() and len(player_hand) == 2
        return basic.get_action(
            player_hand, dealer_upcard,
            can_double=can_double,
            can_surrender=can_surrender,
            can_split=can_split
        )

    def never_bust_func(player_hand, dealer_upcard):
        return never_bust.get_action(player_hand, dealer_upcard)

    # Run each strategy and export
    strategies = {
        'basic_strategy': basic_func,
        'never_bust': never_bust_func
    }

    for name, func in strategies.items():
        result = sim.run_simulation(
            5000,
            func,
            num_sessions=1,
            track_hands=True,
            max_tracked_hands=100
        )

        # Export results
        files = export_all_csv(result, f'results/compare_{name}')
        print(f"{name}:")
        print(f"  EV: {result.ev_per_hand:+.6f} ({result.ev_per_hand * 100:+.4f}%)")
        print(f"  Win rate: {result.win_rate * 100:.2f}%")
        print(f"  Files: {', '.join(files.keys())}")
        print()


if __name__ == '__main__':
    print("Results Export Demonstration")
    print("=" * 60)
    print()

    demo_basic_export()
    demo_multi_session_export()
    demo_large_scale_export()
    demo_strategy_comparison_export()

    print("✓ Reporter demo complete!")
    print("\nCheck the results/ directory for exported CSV and JSON files.")
    print("These files can be used for further analysis or imported into")
    print("spreadsheet applications.")
