#!/usr/bin/env python3
"""
Parse CSV strategy files and update JSON strategy files.
"""

import csv
import json
from pathlib import Path


def parse_csv_strategy(csv_path):
    """Parse a CSV strategy file and return structured data."""
    # Map CSV abbreviations to action codes
    action_map = {
        'H': 'hit',
        'S': 'stand',
        'P': 'split',
        'Dh': 'double_else_hit',
        'Ds': 'double_else_stand',
        'Rh': 'surrender_else_hit',
        'Rs': 'surrender_else_stand',
        'Rp': 'surrender_else_split',
        'Ph': 'split'  # Simplified: treat as split (ignoring DAS condition)
    }

    # Dealer upcards in order from CSV
    dealer_cards = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'A']

    hard_totals = {}
    soft_totals = {}
    pairs = {}

    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            hand_type = row['hand_type']
            player_hand = row['player_hand']

            # Build action mapping for this hand
            actions = {}
            for dealer_card in dealer_cards:
                csv_action = row[dealer_card]
                actions[dealer_card] = action_map.get(csv_action, csv_action)

            if hand_type == 'hard':
                # Handle ranges like "4-8", "18+", "17+"
                if '-' in player_hand:
                    # Range like "4-8"
                    start, end = player_hand.split('-')
                    for total in range(int(start), int(end) + 1):
                        hard_totals[str(total)] = actions.copy()
                elif '+' in player_hand:
                    # Range like "18+" or "17+"
                    start = int(player_hand.replace('+', ''))
                    for total in range(start, 22):  # Up to 21
                        hard_totals[str(total)] = actions.copy()
                else:
                    # Single value
                    hard_totals[player_hand] = actions

            elif hand_type == 'soft':
                # Handle ranges like "20+", "19+"
                if '+' in player_hand:
                    start = int(player_hand.replace('+', ''))
                    for total in range(start, 22):  # Up to 21
                        soft_totals[str(total)] = actions.copy()
                else:
                    soft_totals[player_hand] = actions

            elif hand_type == 'split':
                # Handle pairs like "2,2", "A,A"
                # Extract the card value
                card = player_hand.split(',')[0]
                pairs[card] = actions

    # Ensure we have entries for pair 5 and 10 (not in CSVs because you don't split them)
    # They should behave like their hard total equivalents
    if '5' not in pairs:
        # Pair of 5s = hard 10
        pairs['5'] = hard_totals['10'].copy()
    if '10' not in pairs:
        # Pair of 10s = hard 20, always stand
        pairs['10'] = {card: 'stand' for card in dealer_cards}

    return {
        'hard_totals': hard_totals,
        'soft_totals': soft_totals,
        'pairs': pairs
    }


def update_strategy_json(json_path, csv_path, strategy_name, description, rules_note):
    """Update a strategy JSON file with data from CSV."""
    # Parse CSV
    strategy_data = parse_csv_strategy(csv_path)

    # Build complete strategy JSON
    strategy_json = {
        "name": strategy_name,
        "description": description,
        "rules": {
            "decks": "4+",
            "dealer_hits_soft_17": "H17" in str(csv_path),
            "surrender_allowed": True,
            "double_after_split": True,
            "blackjack_payout": 1.5,
            "notes": rules_note
        },
        "strategy": strategy_data,
        "action_codes": {
            "hit": "Take another card",
            "stand": "End turn with current hand",
            "double": "Double bet and take exactly one card (if not allowed, use fallback)",
            "double_else_hit": "Double if allowed, otherwise hit",
            "double_else_stand": "Double if allowed, otherwise stand",
            "split": "Split pair into two hands (deferred to future implementation)",
            "split_else_hit": "Split if allowed (DAS), otherwise hit",
            "surrender": "Forfeit hand and lose half bet (if not allowed, use fallback)",
            "surrender_else_hit": "Surrender if allowed, otherwise hit",
            "surrender_else_split": "Surrender if allowed, otherwise split",
            "surrender_else_stand": "Surrender if allowed, otherwise stand"
        }
    }

    # Write to JSON file
    with open(json_path, 'w') as f:
        json.dump(strategy_json, f, indent=2)

    print(f"Updated {json_path.name}")


def main():
    """Main function to update both strategy files."""
    base_dir = Path(__file__).parent
    csv_dir = base_dir / "csvs_added"
    strategies_dir = base_dir / "config" / "strategies"

    # Update H17 strategy
    update_strategy_json(
        strategies_dir / "basic_strategy_h17.json",
        csv_dir / "basic_strategy_4to8deck_H17.csv",
        "Basic Strategy (H17, Surrender)",
        "Mathematically optimal basic strategy for 4+ deck blackjack",
        "Based on Wizard of Odds strategy for 4+ decks, dealer hits soft 17"
    )

    # Update S17 strategy
    update_strategy_json(
        strategies_dir / "basic_strategy_s17.json",
        csv_dir / "basic_strategy_4to8deck_S17.csv",
        "Basic Strategy (S17, Surrender)",
        "Mathematically optimal basic strategy for 4+ deck blackjack, dealer stands on soft 17",
        "Based on Wizard of Odds strategy for 4+ decks, dealer stands on soft 17"
    )

    print("\nStrategy files updated successfully!")


if __name__ == "__main__":
    main()
