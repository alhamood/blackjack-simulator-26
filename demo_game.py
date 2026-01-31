"""
Demo script showing complete blackjack games in action.
"""

from src.cards import Shoe
from src.game import BlackjackGame, GameRules, PlayerAction


def demo_simple_game():
    """Demonstrate a simple blackjack game."""
    print("=== Simple Blackjack Game ===")

    shoe = Shoe(num_decks=6, infinite=True)
    game = BlackjackGame(shoe)

    # Play a hand (player stands by default)
    result = game.play_hand()

    print(f"Player hand: {result.player_hand}")
    print(f"Dealer hand: {result.dealer_hand}")
    print(f"Outcome: {result.outcome.value}")
    print(f"Payout: {result.payout:+.2f} (bet: {result.bet})")
    print()


def demo_multiple_hands():
    """Demonstrate playing multiple hands."""
    print("=== Playing 5 Hands ===")

    shoe = Shoe(num_decks=6, infinite=True)

    wins = 0
    losses = 0
    pushes = 0

    for i in range(5):
        game = BlackjackGame(shoe)
        result = game.play_hand()

        print(f"\nHand {i+1}:")
        print(f"  Player: {result.player_hand}")
        print(f"  Dealer: {result.dealer_hand}")
        print(f"  Result: {result.outcome.value} ({result.payout:+.2f})")

        if result.payout > 0:
            wins += 1
        elif result.payout < 0:
            losses += 1
        else:
            pushes += 1

    print(f"\nSummary: {wins} wins, {losses} losses, {pushes} pushes")
    print()


def demo_basic_strategy():
    """Demonstrate using a simple strategy."""
    print("=== Using Basic Strategy (simplified) ===")

    shoe = Shoe(num_decks=6, infinite=True)
    game = BlackjackGame(shoe)

    # Simplified strategy: hit on < 17, stand on >= 17
    def simple_strategy(player_hand, dealer_upcard):
        if player_hand.value() < 17:
            return PlayerAction.HIT
        return PlayerAction.STAND

    result = game.play_hand(strategy_func=simple_strategy)

    print(f"Player final hand: {result.player_hand}")
    print(f"Dealer final hand: {result.dealer_hand}")
    print(f"Outcome: {result.outcome.value}")
    print(f"Payout: {result.payout:+.2f}")
    print()


def demo_doubling_down():
    """Demonstrate doubling down."""
    print("=== Doubling Down Demo ===")

    shoe = Shoe(num_decks=6, infinite=True)
    game = BlackjackGame(shoe)

    # Strategy: double on 10 or 11
    def double_on_10_11(player_hand, dealer_upcard):
        value = player_hand.value()
        if len(player_hand) == 2 and value in [10, 11]:
            return PlayerAction.DOUBLE
        elif value < 17:
            return PlayerAction.HIT
        return PlayerAction.STAND

    result = game.play_hand(strategy_func=double_on_10_11)

    print(f"Player final hand: {result.player_hand}")
    print(f"Dealer final hand: {result.dealer_hand}")
    print(f"Bet: {result.bet} (doubled: {result.bet == 2.0})")
    print(f"Outcome: {result.outcome.value}")
    print(f"Payout: {result.payout:+.2f}")
    print()


def demo_surrender():
    """Demonstrate surrendering."""
    print("=== Surrender Demo ===")

    shoe = Shoe(num_decks=6, infinite=True)
    rules = GameRules(surrender_allowed=True)
    game = BlackjackGame(shoe, rules=rules)

    # Strategy: surrender on hard 16 vs dealer 10 or A
    def surrender_16_vs_10_A(player_hand, dealer_upcard):
        value = player_hand.value()
        dealer_value = dealer_upcard.value()

        # Surrender hard 16 vs 10 or A
        if (len(player_hand) == 2 and
            value == 16 and
            not player_hand.is_soft() and
            dealer_value in [10, 11]):
            return PlayerAction.SURRENDER
        elif value < 17:
            return PlayerAction.HIT
        return PlayerAction.STAND

    result = game.play_hand(strategy_func=surrender_16_vs_10_A)

    print(f"Player hand: {result.player_hand}")
    print(f"Dealer upcard: {game.dealer.upcard()}")
    print(f"Outcome: {result.outcome.value}")
    print(f"Payout: {result.payout:+.2f} (surrendered: {result.payout == -0.5})")
    print()


def demo_different_rules():
    """Demonstrate different game rules."""
    print("=== Different Game Rules Demo ===")

    # Standard rules (dealer stands on soft 17)
    print("Standard rules (S17):")
    shoe = Shoe(num_decks=6, infinite=True)
    rules_s17 = GameRules(dealer_hits_soft_17=False)
    game1 = BlackjackGame(shoe, rules=rules_s17)
    result1 = game1.play_hand()
    print(f"  Player: {result1.player_hand}")
    print(f"  Dealer: {result1.dealer_hand}")
    print(f"  Outcome: {result1.outcome.value}")

    # House-favorable rules (dealer hits soft 17, 6:5 blackjack)
    print("\nHouse-favorable rules (H17, 6:5 BJ):")
    rules_h17 = GameRules(
        dealer_hits_soft_17=True,
        blackjack_payout=1.2  # 6:5 instead of 3:2
    )
    game2 = BlackjackGame(shoe, rules=rules_h17)
    result2 = game2.play_hand()
    print(f"  Player: {result2.player_hand}")
    print(f"  Dealer: {result2.dealer_hand}")
    print(f"  Outcome: {result2.outcome.value}")
    print()


def demo_blackjack_scenarios():
    """Demonstrate various blackjack scenarios."""
    print("=== Special Scenarios ===")

    shoe = Shoe(num_decks=6, infinite=True)

    scenarios = [
        "Random hand 1",
        "Random hand 2",
        "Random hand 3",
    ]

    for scenario in scenarios:
        game = BlackjackGame(shoe)
        result = game.play_hand()

        print(f"\n{scenario}:")
        print(f"  Player: {result.player_hand}", end="")
        if result.player_hand.is_blackjack():
            print(" ← BLACKJACK!", end="")
        elif result.player_hand.is_bust():
            print(" ← BUST!", end="")
        print()

        print(f"  Dealer: {result.dealer_hand}", end="")
        if result.dealer_hand.is_blackjack():
            print(" ← BLACKJACK!", end="")
        elif result.dealer_hand.is_bust():
            print(" ← BUST!", end="")
        print()

        print(f"  Winner: {result.outcome.value} ({result.payout:+.2f})")

    print()


if __name__ == '__main__':
    demo_simple_game()
    demo_multiple_hands()
    demo_basic_strategy()
    demo_doubling_down()
    demo_surrender()
    demo_different_rules()
    demo_blackjack_scenarios()

    print("✓ Game module demo complete!")
    print("\nWe can now play complete hands of blackjack!")
