# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Polish checkers (warcaby) tournament framework** for a university competition. The system allows teams to develop AI bots that play English checkers (8x8 board) against each other. The tournament is scheduled for January 20, 2025.

## Development Commands

### Running a game
```bash
python3 gra.py
```

The game will run between `bot1` and `bot2` defined in `gra.py`. Modify these variables to test different bots.

### Testing your bot
Edit `gra.py` to set:
```python
bot1 = twoj_bot  # Your bot instance
bot2 = "random_bot"  # Or another bot from boty/ folder
```

## Code Architecture

### Core Components

**`silnik.py`** - The game engine (`GRA` class)
- Manages the 8x8 checkers board represented as 4x8 numpy array (only dark squares)
- Handles move validation, piece movement, king promotion
- Implements perspective switching between players

**`gra.py`** - Game runner
- Entry point for running games
- Template for bot implementation
- Loads bots from `boty/` folder or accepts bot instances directly

**`boty/`** - Bot implementations directory
- Each bot must be a separate `.py` file
- Must contain a `bot` class with a `move(plansza, ruchy)` method
- Example: `random_bot.py` selects random legal moves

### Board Representation

**IMPORTANT:** The engine was completely rewritten to use a simple 8x8 board representation (December 2025).

The board is a **8x8 numpy array** representing the full checkerboard:

```python
# Example: starting position from player 1's perspective
# Columns: 0    1     2    3     4    5     6    7
[[None,  2,  None,  2,  None,  2,  None,  2],   # Row 0 - opponent
 [  2, None,  2,  None,  2,  None,  2,  None],  # Row 1
 [None,  2,  None,  2,  None,  2,  None,  2],   # Row 2
 [  0, None,  0,  None,  0,  None,  0,  None],  # Row 3 - empty
 [None,  0,  None,  0,  None,  0,  None,  0],   # Row 4 - empty
 [  1, None,  1,  None,  1,  None,  1,  None],  # Row 5 - player
 [None,  1,  None,  1,  None,  1,  None,  1],   # Row 6
 [  1, None,  1,  None,  1,  None,  1,  None]]  # Row 7
```

**Square encoding:**
- `None` = white (unplayable) square - displayed as empty space
- `0` = empty dark square
- `1` = current player's pawn
- `2` = opponent's pawn
- `3` = current player's king
- `4` = opponent's king

**Dark squares**: Located where `(row + col) % 2 == 1`

**Perspective switching**: After each move, `zamien_perspektywe()` rotates the board 180° and swaps piece ownership so the active player always sees their pieces as `1` and `3`.

### Move Representation

Moves are tuples of tuples: `((start_row, start_col), (end_row, end_col))`

Example: `[((5,1), (4,1)), ((5,2), (4,1)), ((5,2), (4,2))]`

### Bot Interface

Every bot must implement:

```python
class bot():
    def __init__(self):
        pass

    def move(self, plansza, ruchy):
        '''
        Args:
            plansza: 4x8 numpy array from current player's perspective
            ruchy: list of legal moves as ((start_row, start_col), (end_row, end_col))
        Returns:
            chosen move from ruchy list
        '''
        # Your algorithm here
        return chosen_move
```

### Loading Bots

Bots can be loaded two ways:
1. **By filename** (string): `GRA(bot1="random_bot", bot2="my_bot")` - loads from `boty/random_bot.py` and `boty/my_bot.py`
2. **By instance**: `GRA(bot1=my_bot_instance, bot2=another_bot_instance)`

The `_zaladuj_bota()` method in `silnik.py` uses `importlib` for dynamic loading.

### Diagonal Movement Logic

**Simple ±1, ±1 approach:**

- **Regular moves**: Diagonal neighbors are always at `(row ± 1, col ± 1)`
  - Pawns move forward only: `(row - 1, col - 1)` or `(row - 1, col + 1)`
  - Kings move in all 4 diagonal directions: `±1, ±1`

- **Captures**: Landing square is at `(row ± 2, col ± 2)`
  - Captured piece is at the middle: `(row ± 1, col ± 1)`
  - Both pawns and kings can capture in all 4 diagonal directions

This simple logic is implemented in:
- `_znajdz_ruchy()`: Regular diagonal moves (±1, ±1)
- `_znajdz_bicia()`: Capture moves (±2, ±2) with opponent at (±1, ±1)

## Tournament Rules (from README.md)

### Constraints
- **Time limit**: ~1 minute per game (scaled to specific hardware)
- **Memory limit**: 1 GiB RAM
- **Code size limit**: 4 MiB
- **No internet access** during matches

### Match Format
- Each pair plays 2 matches (alternating first move)
- If tied 1-1: overtime with random piece removal, then 2 more matches
- 3-fold repetition = draw
- 20 moves without pawn movement/capture = draw

### Game Rules (English/American Checkers)
- **Captures are mandatory** but can choose any legal capture (no maximum capture rule)
- **Multi-jump captures**: After a capture, if the same piece can capture again, it must continue (implemented)
- **Automatic moves**: When only one legal move exists, it executes automatically without asking the bot
- **Kings move only 1 square diagonally** (not long-distance like Polish checkers)
- Pawns capture forward or backward but move only forward
- Kings can move and capture in all diagonal directions

## C++ Integration (Optional)

Teams can use C++ with pybind11. See README.md for compilation commands:

```bash
g++ -O3 -Wall -shared -std=c++11 -fPIC \
    $(python3 -m pybind11 --includes) \
    kod_cpp.cpp -o kod_cpp$(python3-config --extension-suffix)
```

## Complete Rewrite (December 2025)

The entire game engine was rewritten from scratch with a much simpler architecture:

### What Changed
1. **Board representation**: Changed from compressed 4x8 to full 8x8 array
2. **Movement logic**: Simplified to straightforward ±1, ±1 for moves and ±2, ±2 for captures
3. **No coordinate conversions**: Direct array indexing eliminates conversion bugs
4. **Cleaner code**: ~400 lines vs ~550 lines, easier to understand and maintain

### Features Implemented
- ✅ Multi-jump captures with same piece
- ✅ Automatic moves when only one legal move exists
- ✅ Mandatory captures (bicia obowiązkowe)
- ✅ King promotion at row 0
- ✅ Perspective switching via 180° rotation

### Known Limitations
1. **Draw detection incomplete**: 3-fold repetition and 20-move rule not yet implemented (see README.md for draw conditions)
