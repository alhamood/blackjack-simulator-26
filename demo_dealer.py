"""
Demo script showing the dealer module in action.
"""

from src.cards import Card, Shoe
from src.dealer import Dealer


def demo_dealer_basic():
    """Demonstrate basic dealer behavior."""
    print("=== Basic Dealer Demo ===")

    dealer = Dealer()
    shoe = Shoe(num_decks=6, infinite=True)

    dealer.deal_initial_cards(shoe)
    print(f"Dealer initial hand: {dealer.hand}")
    print(f"Dealer upcard: {dealer.upcard()}")
    print(f"Dealer hole card: {dealer.holecard()} (hidden from players)")
    print()


def demo_dealer_play_hand():
    """Demonstrate dealer playing out a hand."""
    print("=== Dealer Play Hand Demo ===")

    dealer = Dealer()
    shoe = Shoe(num_decks=6, infinite=True)

    # Give dealer a starting hand
    dealer.hand.add_card(Card('K', '♠'))
    dealer.hand.add_card(Card('6', '♥'))
    print(f"Dealer starts with: {dealer.hand}")
    print(f"Dealer upcard: {dealer.upcard()}")

    # Dealer plays
    print("\nDealer playing hand...")
    final_hand = dealer.play_hand(shoe)

    print(f"Dealer final hand: {final_hand}")
    if final_hand.is_bust():
        print("Dealer BUSTS!")
    else:
        print(f"Dealer stands on {final_hand.value()}")
    print()


def demo_soft_17_rule():
    """Demonstrate the dealer hits soft 17 rule."""
    print("=== Soft 17 Rule Demo ===")

    # Dealer stands on soft 17 (default)
    dealer1 = Dealer(hits_soft_17=False)
    dealer1.hand.add_card(Card('A', '♠'))
    dealer1.hand.add_card(Card('6', '♥'))
    print(f"Dealer (S17 rule) has: {dealer1.hand}")
    print(f"Should hit? {dealer1.should_hit()}")

    # Dealer hits soft 17
    dealer2 = Dealer(hits_soft_17=True)
    dealer2.hand.add_card(Card('A', '♠'))
    dealer2.hand.add_card(Card('6', '♥'))
    print(f"\nDealer (H17 rule) has: {dealer2.hand}")
    print(f"Should hit? {dealer2.should_hit()}")

    # Play out the H17 hand
    shoe = Shoe(num_decks=6, infinite=True)
    final_hand = dealer2.play_hand(shoe)
    print(f"After playing: {final_hand}")
    print()


def demo_dealer_blackjack():
    """Demonstrate dealer blackjack."""
    print("=== Dealer Blackjack Demo ===")

    dealer = Dealer()
    dealer.hand.add_card(Card('A', '♠'))
    dealer.hand.add_card(Card('K', '♥'))

    print(f"Dealer hand: {dealer.hand}")
    print(f"Has blackjack? {dealer.has_blackjack()}")
    print(f"Dealer upcard: {dealer.upcard()}")
    print()


def demo_dealer_bust():
    """Demonstrate dealer busting."""
    print("=== Dealer Bust Demo ===")

    dealer = Dealer()
    shoe = Shoe(num_decks=6, infinite=True)

    # Give dealer a hand that will likely bust
    dealer.hand.add_card(Card('10', '♠'))
    dealer.hand.add_card(Card('6', '♥'))
    print(f"Dealer starts with: {dealer.hand}")

    # Keep hitting until bust (for demo purposes)
    while not dealer.is_bust() and dealer.hand.value() < 21:
        card = shoe.deal_card()
        dealer.hand.add_card(card)
        print(f"Dealer hits: {card} → {dealer.hand}")

        if dealer.is_bust():
            print(f"Dealer BUSTS with {dealer.value()}!")
            break
        elif not dealer.should_hit():
            print(f"Dealer stands on {dealer.value()}")
            break
    print()


def demo_multiple_hands():
    """Demonstrate dealer playing multiple hands."""
    print("=== Multiple Hands Demo ===")

    dealer = Dealer()
    shoe = Shoe(num_decks=6, infinite=True)

    for i in range(3):
        dealer.clear_hand()
        dealer.deal_initial_cards(shoe)

        print(f"Hand {i+1}:")
        print(f"  Starting: {dealer.hand}")

        final_hand = dealer.play_hand(shoe)

        if final_hand.is_bust():
            result = f"BUST ({final_hand.value()})"
        elif final_hand.is_blackjack():
            result = "BLACKJACK!"
        else:
            result = f"stands on {final_hand.value()}"

        print(f"  Final: {final_hand} → {result}")
        print()


if __name__ == '__main__':
    demo_dealer_basic()
    demo_dealer_play_hand()
    demo_soft_17_rule()
    demo_dealer_blackjack()
    demo_dealer_bust()
    demo_multiple_hands()

    print("✓ Dealer module demo complete!")
