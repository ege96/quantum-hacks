from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Any
import uvicorn
import json
import random

from q_cell import QuantumSudokuBoard, BOARD_SIZE

app = FastAPI(
    title="Quantum Sudoku API",
    description="Backend API for a Quantum Sudoku game that allows users to assign multiple values to cells",
    version="1.0.0"
)

# Add CORS middleware to allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify actual origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def solve_sudoku(board):
    """
    Solve the Sudoku board using backtracking.
    Returns True if a solution exists, False otherwise.
    Modifies the board in-place with a solution if one exists.
    """
    # Find empty cell
    empty_cell = find_empty(board)
    if not empty_cell:
        return True  # Board is complete
    
    row, col = empty_cell
    
    # Try each number 1-9
    for num in range(1, 10):
        if is_valid_placement(board, row, col, num):
            # Place the number
            board[row][col] = num
            
            # Recursively try to solve the rest of the board
            if solve_sudoku(board):
                return True
            
            # If we get here, this number didn't work
            # Backtrack and try another number
            board[row][col] = 0
    
    # No solution found with any number
    return False

def find_empty(board):
    """Find an empty cell (cell with value 0) in the board"""
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i][j] == 0:
                return (i, j)
    return None

def generate_solved_board():
    """
    Generate a completely solved Sudoku board by starting with
    an empty board and using the solver.
    """
    # Start with an empty board
    board = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    
    # Fill in the first few cells randomly to create variety
    # Place a few random numbers to seed the solver
    for _ in range(5):
        row = random.randint(0, BOARD_SIZE - 1)
        col = random.randint(0, BOARD_SIZE - 1)
        if board[row][col] == 0:  # Only if cell is empty
            # Try numbers until we find a valid one
            nums = list(range(1, 10))
            random.shuffle(nums)
            for num in nums:
                if is_valid_placement(board, row, col, num):
                    board[row][col] = num
                    break
    
    # Solve the board
    solve_sudoku(board)
    return board

# Function to generate a random Sudoku board with some filled cells
def generate_random_sudoku(difficulty='medium'):
    """
    Generate a random initial Sudoku board with some cells already filled.
    Ensures the board has a valid solution.
    
    Args:
        difficulty (str): 'easy', 'medium', or 'hard', determines number of filled cells
        
    Returns:
        list: 2D list representing the initial board (0 for empty cells)
    """
    # Generate a fully solved board
    solved_board = generate_solved_board()
    
    # Create a puzzle by removing some numbers
    puzzle = [row[:] for row in solved_board]  # Make a deep copy
    
    # Determine how many cells to keep based on difficulty
    if difficulty == 'easy':
        cells_to_keep = random.randint(35, 40)
    elif difficulty == 'medium':
        cells_to_keep = random.randint(25, 34)
    else:  # hard
        cells_to_keep = random.randint(17, 24)
    
    # Calculate how many cells to remove
    cells_to_remove = 81 - cells_to_keep
    
    # Remove cells randomly
    removed = 0
    while removed < cells_to_remove:
        row = random.randint(0, BOARD_SIZE - 1)
        col = random.randint(0, BOARD_SIZE - 1)
        
        # Only remove if the cell is not already empty
        if puzzle[row][col] != 0:
            # Temporarily store the value
            temp = puzzle[row][col]
            puzzle[row][col] = 0
            removed += 1
            
            # Optional: Check if puzzle still has a unique solution
            # For simplicity, we're skipping this check, but it could be added
            # to ensure the puzzle has a unique solution
    
    return puzzle

def is_valid_placement(board, row, col, val):
    """
    Check if placing 'val' at board[row][col] would be a valid Sudoku move.
    """
    # Check row
    for c in range(BOARD_SIZE):
        if board[row][c] == val:
            return False
    
    # Check column
    for r in range(BOARD_SIZE):
        if board[r][col] == val:
            return False
    
    # Check 3x3 block
    block_row = (row // 3) * 3
    block_col = (col // 3) * 3
    for r in range(block_row, block_row + 3):
        for c in range(block_col, block_col + 3):
            if board[r][c] == val:
                return False
    
    return True

# Store the board instance (could be replaced with a database or session-based approach)
initial_board = generate_random_sudoku('medium')
quantum_board = QuantumSudokuBoard()
quantum_board.initialize_from_array(initial_board)

class CellAssignment(BaseModel):
    """Model for cell assignment requests"""
    row: int = Field(..., ge=0, lt=BOARD_SIZE)
    col: int = Field(..., ge=0, lt=BOARD_SIZE)
    candidates: List[int] = Field(..., min_items=1)
    
    @validator('candidates')
    def validate_candidates(cls, v):
        """Ensure all candidates are valid digits (1-9 for standard Sudoku)"""
        for digit in v:
            if digit < 1 or digit > BOARD_SIZE:
                raise ValueError(f"Invalid digit {digit}. Must be between 1 and {BOARD_SIZE}.")
        return v

@app.post("/assign", response_model=Dict[str, Any])
async def assign_cell_values(assignment: CellAssignment):
    """
    Assign one or more candidate values to a cell.
    
    If a single value is provided, the cell will be fully collapsed.
    If multiple values are provided, the cell will be in a partial superposition.
    The response includes the updated state of the entire board.
    """
    try:
        # Apply the user assignment
        quantum_board.user_assign(
            assignment.row,
            assignment.col,
            assignment.candidates
        )
        
        # Return the updated board state
        return {
            "success": True,
            "message": f"Cell ({assignment.row}, {assignment.col}) updated with candidates {assignment.candidates}",
            "board": quantum_board.serialize_board()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.get("/board")
async def get_board():
    """
    Get the current state of the Quantum Sudoku board.
    
    Returns a 9x9 grid where each cell contains either a fixed value or a set of possibilities.
    """
    return quantum_board.serialize_board()

@app.post("/reset")
async def reset_board(difficulty: str = 'medium'):
    """
    Reset the Quantum Sudoku board with a new random puzzle.
    
    Args:
        difficulty: 'easy', 'medium', or 'hard' - determines the number of pre-filled cells
    """
    global quantum_board
    global initial_board
    
    # Generate a new random board with the specified difficulty
    initial_board = generate_random_sudoku(difficulty)
    quantum_board = QuantumSudokuBoard()
    quantum_board.initialize_from_array(initial_board)
    
    return {
        "success": True, 
        "message": f"Board has been reset to a new {difficulty} puzzle"
    }

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True) 