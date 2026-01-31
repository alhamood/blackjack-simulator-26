"""
Demo script showing strategy system in action.
"""

from src.cards import Shoe, Card
from src.hand import Hand
from src.game import BlackjackGame, GameRules
from src.player import Strategy


def demo_load_strategies():
    """Demonstrate loading different strategies."""
    print("=== Loading Strategies ===")

    basic = Strategy('config/strategies/basic_strategy_h17.json')
    print(f"Loaded: {basic.name}")
    print(f"  Description: {basic.description}")
    print(f"  Rules: {basic.rules}")
    print()

    never_bust = Strategy('config/strategies/never_bust.json')
    print(f"Loaded: {never_bust.name}")
    print(f"  Description: {never_bust.description}")
    print()


def demo_strategy_lookups():
    """Demonstrate strategy action lookups."""
    print("=== Strategy Lookups ===")

    basic = Strategy('config/strategies/basic_strategy_h17.json')
    dealer_upcard = Card('10', '♦')

    # Hard 16 vs 10
    hand1 = Hand()
    hand1.add_card(Card('K', '♠'))
    hand1.add_card(Card('6', '♥'))
    action1 = basic.get_action(hand1, dealer_upcard, can_surrender=True)
    print(f"Hard 16 vs dealer 10: {action1.value}")

    # Hard 11 vs 10
    hand2 = Hand()
    hand2.add_card(Card('6', '♠'))
    hand2.add_card(Card('5', '♥'))
    action2 = basic.get_action(hand2, dealer_upcard, can_double=True)
    print(f"Hard 11 vs dealer 10: {action2.value}")

    # Soft 18 vs 9
    hand3 = Hand()
    hand3.add_card(Card('A', '♠'))
    hand3.add_card(Card('7', '♥'))
    dealer_9 = Card('9', '♦')
    action3 = basic.get_action(hand3, dealer_9)
    print(f"Soft 18 vs dealer 9: {action3.value}")

    # Pair of 8s vs 5
    hand4 = Hand()
    hand4.add_card(Card('8', '♠'))
    hand4.add_card(Card('8', '♥'))
    dealer_5 = Card('5', '♦')
    action4 = basic.get_action(hand4, dealer_5, can_split=True)
    print(f"Pair of 8s vs dealer 5: {action4.value}")
    print()


def demo_strategy_fallbacks():
    """Demonstrate fallback action handling."""
    print("=== Strategy Fallbacks ===")

    basic = Strategy('config/strategies/basic_strategy_h17.json')

    # Hard 11 - double if allowed, else hit
    hand = Hand()
    hand.add_card(Card('6', '♠'))
    hand.add_card(Card('5', '♥'))
    dealer_upcard = Card('6', '♦')

    action_double = basic.get_action(hand, dealer_upcard, can_double=True)
    print(f"Hard 11 vs 6 (can double): {action_double.value}")

    action_no_double = basic.get_action(hand, dealer_upcard, can_double=False)
    print(f"Hard 11 vs 6 (can't double): {action_no_double.value}")

    # Hard 16 - surrender if allowed, else hit
    hand2 = Hand()
    hand2.add_card(Card('K', '♠'))
    hand2.add_card(Card('6', '♥'))
    dealer_10 = Card('10', '♦')

    action_surrender = basic.get_action(hand2, dealer_10, can_surrender=True)
    print(f"Hard 16 vs 10 (can surrender): {action_surrender.value}")

    action_no_surrender = basic.get_action(hand2, dealer_10, can_surrender=False)
    print(f"Hard 16 vs 10 (can't surrender): {action_no_surrender.value}")
    print()


def demo_strategy_vs_strategy():
    """Compare basic strategy vs never bust strategy."""
    print("=== Basic Strategy vs Never Bust ===")

    basic = Strategy('config/strategies/basic_strategy_h17.json')
    never_bust = Strategy('config/strategies/never_bust.json')

    # Hard 12 vs dealer 2
    hand = Hand()
    hand.add_card(Card('7', '♠'))
    hand.add_card(Card('5', '♥'))
    dealer_2 = Card('2', '♦')

    basic_action = basic.get_action(hand, dealer_2)
    never_bust_action = never_bust.get_action(hand, dealer_2)

    print(f"Hard 12 vs dealer 2:")
    print(f"  Basic strategy: {basic_action.value}")
    print(f"  Never bust: {never_bust_action.value}")

    # Hard 16 vs dealer 7
    hand2 = Hand()
    hand2.add_card(Card('K', '♠'))
    hand2.add_card(Card('6', '♥'))
    dealer_7 = Card('7', '♦')

    basic_action2 = basic.get_action(hand2, dealer_7)
    never_bust_action2 = never_bust.get_action(hand2, dealer_7)

    print(f"\nHard 16 vs dealer 7:")
    print(f"  Basic strategy: {basic_action2.value}")
    print(f"  Never bust: {never_bust_action2.value}")
    print()


def demo_play_with_strategy():
    """Play a hand using a loaded strategy."""
    print("=== Playing with Basic Strategy ===")

    shoe = Shoe(num_decks=6, infinite=True)
    rules = GameRules(dealer_hits_soft_17=True, surrender_allowed=True)
    game = BlackjackGame(shoe, rules=rules)

    # Load basic strategy
    basic = Strategy('config/strategies/basic_strategy_h17.json')

    # Create strategy function for the game
    def strategy_func(player_hand, dealer_upcard):
        # Determine what actions are allowed
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

    # Play a hand
    result = game.play_hand(strategy_func=strategy_func)

    print(f"Player hand: {result.player_hand}")
    print(f"Dealer hand: {result.dealer_hand}")
    print(f"Outcome: {result.outcome.value}")
    print(f"Payout: {result.payout:+.2f}")
    print()


def demo_multiple_hands_with_strategy():
    """Play multiple hands and track results."""
    print("=== Playing 10 Hands with Basic Strategy ===")

    shoe = Shoe(num_decks=6, infinite=True)
    rules = GameRules(dealer_hits_soft_17=True, surrender_allowed=True)
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

    total_payout = 0.0
    outcomes = []

    for i in range(10):
        game = BlackjackGame(shoe, rules=rules)
        result = game.play_hand(strategy_func=strategy_func)
        total_payout += result.payout
        outcomes.append(result.outcome.value)

        print(f"Hand {i+1}: {result.outcome.value:20s} ({result.payout:+.2f})")

    print(f"\nTotal payout: {total_payout:+.2f}")
    print(f"Average: {total_payout / 10:+.4f} per hand")
    print()


if __name__ == '__main__':
    demo_load_strategies()
    demo_strategy_lookups()
    demo_strategy_fallbacks()
    demo_strategy_vs_strategy()
    demo_play_with_strategy()
    demo_multiple_hands_with_strategy()

    print("✓ Strategy system demo complete!")
    print("\nWe can now load and execute JSON-based strategies!")
