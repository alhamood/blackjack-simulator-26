"""
FastAPI web server for blackjack simulator.

Provides REST API endpoints for running simulations and managing strategies.
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from collections import defaultdict
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
import tempfile

# Import simulator modules
import sys
sys.path.append(str(Path(__file__).parent.parent))
from src.simulator import Simulator, SimulationResult
from src.game import GameRules, PlayerAction
from src.player import Strategy
from src.reporter import export_to_json


# Pydantic models for request validation
class GameRulesRequest(BaseModel):
    """Game rules configuration."""
    dealer_hits_soft_17: bool = False
    surrender_allowed: bool = True
    double_after_split: bool = True
    blackjack_payout: float = Field(default=1.5, ge=1.0, le=2.0)


class ShoeRequest(BaseModel):
    """Shoe configuration."""
    num_decks: int = Field(default=6, ge=1, le=8)
    penetration: float = Field(default=0.75, ge=0.1, le=1.0)
    infinite_shoe: bool = False


class CustomStrategyData(BaseModel):
    """Custom strategy definition."""
    hard_totals: Dict[str, Dict[str, str]]
    soft_totals: Dict[str, Dict[str, str]]
    pairs: Dict[str, Dict[str, str]]


class CustomStrategyRequest(BaseModel):
    """Custom strategy with metadata."""
    name: str
    description: Optional[str] = None
    strategy: CustomStrategyData


class SimulationConfig(BaseModel):
    """Simulation configuration.

    Note: total_hands represents hands PER SESSION.
    Actual total = total_hands × num_sessions.
    """
    total_hands: int = Field(default=100, ge=100, le=1000000, description="Hands per session")
    num_sessions: int = Field(default=1000, ge=1, le=10000, description="Number of sessions")
    strategy: str = "basic_strategy_h17"
    track_hands: bool = False
    debug_mode: bool = False
    custom_strategy: Optional[CustomStrategyRequest] = None

    @field_validator('num_sessions')
    @classmethod
    def validate_total_hands_limit(cls, v, info):
        """Ensure total hands (hands_per_session × num_sessions) doesn't exceed 10M."""
        hands_per_session = info.data.get('total_hands')
        if hands_per_session and (hands_per_session * v) > 10000000:
            raise ValueError(
                f'Total hands ({hands_per_session:,} × {v:,} = {hands_per_session * v:,}) '
                f'exceeds limit of 10,000,000'
            )
        return v


class SimulationRequest(BaseModel):
    """Complete simulation request."""
    game_rules: GameRulesRequest = Field(default_factory=GameRulesRequest)
    shoe: ShoeRequest = Field(default_factory=ShoeRequest)
    simulation: SimulationConfig = Field(default_factory=SimulationConfig)


# Initialize FastAPI app
app = FastAPI(
    title="Blackjack Simulator API",
    description="REST API for blackjack strategy simulation",
    version="0.5.0"
)

# Configure CORS
cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Helper functions
def get_strategies_dir() -> Path:
    """Get path to strategies directory."""
    return Path(__file__).parent.parent / "config" / "strategies"


def load_strategy_metadata(strategy_id: str) -> Dict[str, Any]:
    """Load strategy metadata from JSON file."""
    strategy_path = get_strategies_dir() / f"{strategy_id}.json"

    if not strategy_path.exists():
        raise HTTPException(status_code=404, detail=f"Strategy '{strategy_id}' not found")

    with open(strategy_path, 'r') as f:
        data = json.load(f)

    return data


def create_strategy_wrapper(strategy: Strategy) -> callable:
    """Create strategy wrapper function for simulator."""
    def strategy_func(player_hand, dealer_upcard):
        can_double = len(player_hand) == 2
        can_surrender = len(player_hand) == 2
        can_split = player_hand.is_pair() and len(player_hand) == 2

        return strategy.get_action(
            player_hand,
            dealer_upcard,
            can_double=can_double,
            can_surrender=can_surrender,
            can_split=can_split
        )

    return strategy_func


def categorize_hands_by_strategy(sessions_data: List[Dict]) -> Dict[str, List[Dict[str, Any]]]:
    """Categorize hand results by strategy situation for debugging.

    Returns a dictionary mapping strategy keys (e.g., "hard_10_vs_A") to lists of hand examples.
    """
    categories = defaultdict(list)

    for session in sessions_data:
        if 'hands' not in session or not session['hands']:
            continue

        for hand in session['hands']:
            # Skip if missing dealer upcard
            if hand.get('dealer_upcard') is None:
                continue

            # Get dealer upcard
            dealer_upcard = hand['dealer_upcard']
            dealer_upcard_str = 'A' if dealer_upcard == 1 else str(dealer_upcard)

            # Get player hand info
            player_value = hand['player_value']
            player_soft = hand['player_soft']
            player_pair = hand['player_pair']
            player_blackjack = hand['player_blackjack']

            # Determine hand type and create key
            if player_blackjack:
                key = f"blackjack_vs_{dealer_upcard_str}"
            elif player_pair and len(hand.get('player_cards', [])) == 2:
                # Get the rank of the paired card
                card_str = hand['player_cards'][0][:hand['player_cards'][0].find(hand['player_cards'][0][-1])]
                if card_str == '1':  # Ace
                    card_str = 'A'
                key = f"pair_{card_str}_vs_{dealer_upcard_str}"
            elif player_soft:
                key = f"soft_{player_value}_vs_{dealer_upcard_str}"
            else:
                key = f"hard_{player_value}_vs_{dealer_upcard_str}"

            # Store hand example (already in correct format)
            categories[key].append({
                'player_cards': hand.get('player_cards', []),
                'player_value': player_value,
                'player_soft': player_soft,
                'player_pair': player_pair,
                'dealer_upcard': dealer_upcard_str,
                'dealer_value': hand['dealer_value'],
                'outcome': hand['outcome'],
                'bet': hand['bet'],
                'payout': hand['payout']
            })

    # Convert defaultdict to regular dict and limit examples per category
    return {k: v[:5] for k, v in sorted(categories.items())}  # Keep first 5 examples per category


def create_custom_strategy_wrapper(strategy_data: CustomStrategyData) -> callable:
    """Create strategy wrapper function for custom strategy."""
    # Create temporary strategy file
    temp_strategy = {
        "name": "Custom Strategy",
        "description": "User-defined custom strategy",
        "strategy": {
            "hard_totals": strategy_data.hard_totals,
            "soft_totals": strategy_data.soft_totals,
            "pairs": strategy_data.pairs
        }
    }

    # Write to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(temp_strategy, f)
        temp_path = f.name

    try:
        # Load strategy
        strategy = Strategy(temp_path)

        def strategy_func(player_hand, dealer_upcard):
            can_double = len(player_hand) == 2
            can_surrender = len(player_hand) == 2
            can_split = player_hand.is_pair() and len(player_hand) == 2

            return strategy.get_action(
                player_hand,
                dealer_upcard,
                can_double=can_double,
                can_surrender=can_surrender,
                can_split=can_split
            )

        return strategy_func
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)


# API Endpoints
@app.get("/api/defaults")
async def get_defaults():
    """Get default simulation parameters and available strategies."""
    strategies_dir = get_strategies_dir()
    available_strategies = []

    for strategy_file in strategies_dir.glob("*.json"):
        strategy_id = strategy_file.stem
        try:
            data = load_strategy_metadata(strategy_id)
            available_strategies.append({
                "id": strategy_id,
                "name": data.get("name", strategy_id),
                "description": data.get("description", "")
            })
        except Exception:
            continue

    return {
        "game_rules": {
            "dealer_hits_soft_17": True,
            "surrender_allowed": True,
            "double_after_split": True,
            "blackjack_payout": 1.5
        },
        "shoe": {
            "num_decks": 6,
            "penetration": 0.75,
            "infinite_shoe": False
        },
        "simulation": {
            "total_hands": 100,
            "num_sessions": 1000,
            "track_hands": False
        },
        "available_strategies": available_strategies
    }


@app.get("/api/strategies")
async def list_strategies():
    """List all available strategies with metadata."""
    strategies_dir = get_strategies_dir()
    strategies = []

    for strategy_file in strategies_dir.glob("*.json"):
        strategy_id = strategy_file.stem
        try:
            data = load_strategy_metadata(strategy_id)
            strategies.append({
                "id": strategy_id,
                "name": data.get("name", strategy_id),
                "description": data.get("description", ""),
                "rules": data.get("rules", {})
            })
        except Exception:
            continue

    return {"strategies": strategies}


@app.get("/api/strategies/{strategy_id}")
async def get_strategy(strategy_id: str):
    """Get full strategy JSON for editing."""
    data = load_strategy_metadata(strategy_id)
    return data


@app.post("/api/simulate")
async def run_simulation(request: SimulationRequest):
    """Run a blackjack simulation with the provided parameters."""
    try:
        # Create game rules
        rules = GameRules(
            dealer_hits_soft_17=request.game_rules.dealer_hits_soft_17,
            surrender_allowed=request.game_rules.surrender_allowed,
            double_after_split=request.game_rules.double_after_split,
            blackjack_payout=request.game_rules.blackjack_payout
        )

        # Create simulator
        if request.shoe.infinite_shoe:
            sim = Simulator(rules=rules, infinite_shoe=True)
        else:
            sim = Simulator(
                rules=rules,
                num_decks=request.shoe.num_decks,
                penetration=request.shoe.penetration
            )

        # Load or create strategy
        if request.simulation.strategy == "custom" and request.simulation.custom_strategy:
            # Use custom strategy
            strategy_func = create_custom_strategy_wrapper(
                request.simulation.custom_strategy.strategy
            )
        else:
            # Load strategy from file
            strategy_path = get_strategies_dir() / f"{request.simulation.strategy}.json"
            if not strategy_path.exists():
                raise HTTPException(
                    status_code=400,
                    detail=f"Strategy '{request.simulation.strategy}' not found"
                )

            strategy = Strategy(str(strategy_path))
            strategy_func = create_strategy_wrapper(strategy)

        # Run simulation
        # Note: total_hands represents hands PER SESSION
        # Multiply by num_sessions to get actual total hands for the simulator
        hands_per_session = request.simulation.total_hands
        num_sessions = request.simulation.num_sessions
        actual_total_hands = hands_per_session * num_sessions

        # Determine tracking parameters
        track_hands = request.simulation.track_hands or request.simulation.debug_mode
        max_tracked = 10000 if request.simulation.debug_mode else (100 if request.simulation.track_hands else 0)

        result = sim.run_simulation(
            actual_total_hands,
            strategy_func,
            num_sessions=num_sessions,
            track_hands=track_hands,
            max_tracked_hands=max_tracked
        )

        # Convert to JSON format (using reporter module pattern)
        # Build JSON structure matching export_to_json format
        data = {
            'summary': {
                'total_hands': result.total_hands,
                'total_payout': round(result.total_payout, 2),
                'ev_per_hand': round(result.ev_per_hand, 6),
                'ev_percent': round(result.ev_per_hand * 100, 4),
                'win_count': result.win_count,
                'loss_count': result.loss_count,
                'push_count': result.push_count,
                'win_rate': round(result.win_rate, 6),
                'blackjack_count': result.blackjack_count,
                'bust_count': result.bust_count,
                'surrender_count': result.surrender_count,
                'double_count': result.double_count
            },
            'sessions': []
        }

        # Add session data
        for i, session in enumerate(result.sessions, start=1):
            session_data = {
                'session_num': i,
                'hands_played': session.hands_played,
                'total_payout': round(session.total_payout, 2),
                'ev_per_hand': round(session.ev_per_hand, 6),
                'ev_percent': round(session.ev_per_hand * 100, 4),
                'win_count': session.win_count,
                'loss_count': session.loss_count,
                'push_count': session.push_count,
                'win_rate': round(session.win_rate, 6),
                'blackjack_count': session.blackjack_count,
                'bust_count': session.bust_count,
                'surrender_count': session.surrender_count,
                'double_count': session.double_count
            }

            # Include hand data if tracked
            if (request.simulation.track_hands or request.simulation.debug_mode) and session.hand_results:
                session_data['hands'] = [
                    {
                        'outcome': hand.outcome.name,
                        'player_cards': [f"{c.rank}{c.suit[0]}" for c in hand.player_hand.cards],
                        'player_value': hand.player_hand.value(),
                        'player_soft': hand.player_hand.is_soft(),
                        'player_pair': hand.player_hand.is_pair(),
                        'player_blackjack': hand.player_hand.is_blackjack(),
                        'dealer_upcard': hand.dealer_hand.cards[0].rank if hand.dealer_hand.cards else None,
                        'dealer_value': hand.dealer_hand.value(),
                        'dealer_soft': hand.dealer_hand.is_soft(),
                        'dealer_blackjack': hand.dealer_hand.is_blackjack(),
                        'bet': round(hand.bet, 2),
                        'payout': round(hand.payout, 2)
                    }
                    for hand in session.hand_results
                ]

            data['sessions'].append(session_data)

        # Add variance statistics if multi-session
        if len(result.sessions) > 1:
            data['variance'] = {
                'session_ev_mean': round(result.session_ev_mean, 6),
                'session_ev_stdev': round(result.session_ev_stdev, 6)
            }

        # Add debug information if debug mode enabled
        if request.simulation.debug_mode:
            data['debug'] = {
                'strategy_examples': categorize_hands_by_strategy(data['sessions']),
                'total_tracked_hands': sum(len(s.get('hands', [])) for s in data['sessions'])
            }

        return data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Serve static files
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/")
async def read_index():
    """Serve index.html."""
    index_path = static_dir / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"message": "Blackjack Simulator API - Frontend not yet deployed"}


@app.get("/strategy-editor.html")
async def read_strategy_editor():
    """Serve strategy editor page."""
    editor_path = static_dir / "strategy-editor.html"
    if editor_path.exists():
        return FileResponse(str(editor_path))
    raise HTTPException(status_code=404, detail="Strategy editor not found")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
