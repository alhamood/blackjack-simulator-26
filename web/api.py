"""
FastAPI web server for blackjack simulator.

Provides REST API endpoints for running simulations and managing strategies.
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
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
    """Simulation configuration."""
    total_hands: int = Field(default=10000, ge=100, le=1000000)
    num_sessions: int = Field(default=1, ge=1, le=1000)
    strategy: str = "basic_strategy_h17"
    track_hands: bool = False
    custom_strategy: Optional[CustomStrategyRequest] = None


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
            "dealer_hits_soft_17": False,
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
            "total_hands": 10000,
            "num_sessions": 1,
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
        result = sim.run_simulation(
            request.simulation.total_hands,
            strategy_func,
            num_sessions=request.simulation.num_sessions,
            track_hands=request.simulation.track_hands,
            max_tracked_hands=100 if request.simulation.track_hands else 0
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
            if request.simulation.track_hands and session.hand_results:
                session_data['hands'] = [
                    {
                        'outcome': hand.outcome.name,
                        'player_value': hand.player_hand.value(),
                        'player_soft': hand.player_hand.is_soft(),
                        'dealer_value': hand.dealer_hand.value(),
                        'dealer_soft': hand.dealer_hand.is_soft(),
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
