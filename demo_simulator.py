"""
Demo script showing simulation system in action.
"""

from src.simulator import Simulator
from src.game import GameRules, PlayerAction
from src.player import Strategy


def demo_simple_simulation():
    """Demonstrate a simple simulation."""
    print("=== Simple Simulation (1000 hands) ===")

    sim = Simulator(infinite_shoe=True)

    # Simple strategy: hit to 17
    def hit_to_17(player_hand, dealer_upcard):
        if player_hand.value() < 17:
            return PlayerAction.HIT
        return PlayerAction.STAND

    result = sim.run_simulation(1000, hit_to_17, num_sessions=1)
    print(result.summary())
    print()


def demo_basic_strategy_simulation():
    """Demonstrate simulation with loaded basic strategy."""
    print("=== Basic Strategy Simulation (10,000 hands) ===")

    # Load basic strategy
    basic = Strategy('config/strategies/basic_strategy_h17.json')

    # Match game rules to strategy rules
    rules = GameRules(
        dealer_hits_soft_17=True,
        surrender_allowed=True,
        blackjack_payout=1.5
    )

    sim = Simulator(rules=rules, infinite_shoe=True)

    # Create strategy function
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

    result = sim.run_simulation(10000, strategy_func, num_sessions=1)
    print(result.summary())
    print()


def demo_multi_session_simulation():
    """Demonstrate multi-session simulation to measure variance."""
    print("=== Multi-Session Simulation ===")
    print("100 sessions of 100 hands each (10,000 total hands)")
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

    result = sim.run_simulation(10000, strategy_func, num_sessions=100)

    print(result.summary())
    print()

    # Show variance across sessions
    print("Session variance analysis:")
    evs = [s.ev_per_hand for s in result.sessions]
    print(f"  Best session: {max(evs):+.6f}")
    print(f"  Worst session: {min(evs):+.6f}")
    print(f"  Range: {max(evs) - min(evs):.6f}")
    print()


def demo_strategy_comparison():
    """Compare different strategies."""
    print("=== Strategy Comparison (10,000 hands each) ===")

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
            player_hand,
            dealer_upcard,
            can_double=can_double,
            can_surrender=can_surrender,
            can_split=can_split
        )

    def never_bust_func(player_hand, dealer_upcard):
        return never_bust.get_action(player_hand, dealer_upcard)

    def always_stand(player_hand, dealer_upcard):
        return PlayerAction.STAND

    # Compare strategies
    results = sim.compare_strategies(
        strategy_funcs=[basic_func, never_bust_func, always_stand],
        strategy_names=['Basic Strategy', 'Never Bust', 'Always Stand'],
        hands_per_strategy=10000
    )

    # Print comparison
    print(f"{'Strategy':<20} {'EV/Hand':<15} {'Win Rate':<12} {'Busts':<10}")
    print("-" * 60)
    for name, result in results.items():
        print(
            f"{name:<20} "
            f"{result.ev_per_hand:+.6f} ({result.ev_per_hand * 100:+.3f}%)  "
            f"{result.win_rate * 100:>6.2f}%      "
            f"{result.bust_count:>5}"
        )
    print()


def demo_different_game_rules():
    """Compare same strategy under different game rules."""
    print("=== Same Strategy, Different Rules (10,000 hands each) ===")

    basic = Strategy('config/strategies/basic_strategy_h17.json')

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

    # Test 1: Standard rules (S17, 3:2 BJ)
    rules_s17 = GameRules(
        dealer_hits_soft_17=False,
        blackjack_payout=1.5,
        surrender_allowed=True
    )
    sim_s17 = Simulator(rules=rules_s17, infinite_shoe=True)
    result_s17 = sim_s17.run_simulation(10000, strategy_func, num_sessions=1)

    # Test 2: House-favorable rules (H17, 3:2 BJ)
    rules_h17 = GameRules(
        dealer_hits_soft_17=True,
        blackjack_payout=1.5,
        surrender_allowed=True
    )
    sim_h17 = Simulator(rules=rules_h17, infinite_shoe=True)
    result_h17 = sim_h17.run_simulation(10000, strategy_func, num_sessions=1)

    # Test 3: Very unfavorable rules (H17, 6:5 BJ, no surrender)
    rules_bad = GameRules(
        dealer_hits_soft_17=True,
        blackjack_payout=1.2,  # 6:5
        surrender_allowed=False
    )
    sim_bad = Simulator(rules=rules_bad, infinite_shoe=True)
    result_bad = sim_bad.run_simulation(10000, strategy_func, num_sessions=1)

    print(f"{'Rules':<25} {'EV/Hand':<15} {'BJ Payout'}")
    print("-" * 55)
    print(
        f"{'S17, 3:2, Surrender':<25} "
        f"{result_s17.ev_per_hand:+.6f} ({result_s17.ev_per_hand * 100:+.3f}%)  "
        f"{result_s17.blackjack_count * 1.5:.0f} units"
    )
    print(
        f"{'H17, 3:2, Surrender':<25} "
        f"{result_h17.ev_per_hand:+.6f} ({result_h17.ev_per_hand * 100:+.3f}%)  "
        f"{result_h17.blackjack_count * 1.5:.0f} units"
    )
    print(
        f"{'H17, 6:5, No Surrender':<25} "
        f"{result_bad.ev_per_hand:+.6f} ({result_bad.ev_per_hand * 100:+.3f}%)  "
        f"{result_bad.blackjack_count * 1.2:.0f} units"
    )
    print()


def demo_time_estimation():
    """Demonstrate time estimation by calibrating with a small sample."""
    print("=== Time Estimation Demo ===")
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

    target_hands = 100000

    # Estimate time
    estimate = sim.estimate_time(target_hands, strategy_func)
    print(f"Estimated time for {target_hands:,} hands: {estimate:.2f} seconds")

    # Run actual simulation
    result = sim.run_simulation(target_hands, strategy_func, num_sessions=1)

    print(f"Actual time: {result.elapsed_seconds:.2f} seconds")
    if estimate > 0:
        error_pct = abs(result.elapsed_seconds - estimate) / estimate * 100
        print(f"Estimation error: {error_pct:.1f}%")
    print()


def demo_large_scale_simulation():
    """Demonstrate large-scale simulation for accurate EV."""
    print("=== Large-Scale Simulation (100,000 hands) ===")

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

    result = sim.run_simulation(100000, strategy_func, num_sessions=1)

    print(result.summary())
    print(f"Expected house edge with basic strategy: ~0.5%")
    print()


if __name__ == '__main__':
    demo_simple_simulation()
    demo_basic_strategy_simulation()
    demo_multi_session_simulation()
    demo_strategy_comparison()
    demo_different_game_rules()
    demo_time_estimation()
    demo_large_scale_simulation()

    print("✓ Simulation system demo complete!")
    print("\nWe can now run large-scale simulations to analyze strategies!")
