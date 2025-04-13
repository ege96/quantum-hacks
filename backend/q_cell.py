import copy
from typing import List, Dict, Optional, Tuple

# Global Constants for Standard 9x9 Sudoku (changeable for different sizes)
BOARD_SIZE = 9
BLOCK_SIZE = 3
DIGITS = set(range(1, BOARD_SIZE + 1))


class SudokuCell:
    """
    Represents an individual cell on the Quantum Sudoku board.
    
    Attributes:
        fixed_value (Optional[int]): The collapsed value if the cell has been set to a single number.
        possibilities (Dict[int, float]): A mapping of candidate numbers to their probability weights.
            For a cell in a full superposition state, this dict holds all possible numbers (per sudoku rules)
            with equal probabilities. A "partial collapse" is represented by a reduced dictionary.
    """
    def __init__(self, fixed_value: Optional[int] = None):
        self.fixed_value = fixed_value
        
        # If the cell is not fixed, it starts with an empty possibility set.
        # This will be initialized later with valid candidates.
        self.possibilities: Dict[int, float] = {}

    def is_collapsed(self) -> bool:
        """Return True if the cell is fully collapsed (only one possibility/fixed)."""
        return self.fixed_value is not None or len(self.possibilities) == 1

    def collapse(self, number: int):
        """
        Collapse the cell to a single fixed value.
        
        Sets the fixed_value to the provided number and resets possibilities to that number only.
        """
        self.fixed_value = number
        self.possibilities = {number: 1.0}

    def update_possibilities(self, candidates: List[int]):
        """
        Update a cell with a set of candidate values provided by a multi-value user assignment.
        
        The new probability for each candidate is 1/len(candidates).
        """
        if not candidates:
            raise ValueError("Candidate list cannot be empty.")
        probability = 1.0 / len(candidates)
        self.fixed_value = None  # clear any previous fixed assignment
        self.possibilities = {num: probability for num in candidates}

    def remove_candidate(self, candidate: int):
        """
        Remove a candidate from the possibility set (if present) and re-normalize probabilities.
        If the removal reduces the possibility list to a single candidate, collapse the cell.
        """
        if candidate in self.possibilities:
            del self.possibilities[candidate]
            if len(self.possibilities) == 1:
                # Auto-collapse if there is only one possibility remaining.
                remaining_number = next(iter(self.possibilities))
                self.collapse(remaining_number)
            else:
                # Recalculate equal probabilities
                n = len(self.possibilities)
                self.possibilities = {num: 1.0 / n for num in self.possibilities}

    def __repr__(self):
        if self.fixed_value is not None:
            return f"{self.fixed_value}"
        return f"{self.possibilities}"


class QuantumSudokuBoard:
    """
    Represents the Quantum Sudoku board.
    
    Methods include board initialization, handling user inputs (single or multi-value),
    constraint propagation across rows, columns, and blocks, and serialization of board state.
    """
    def __init__(self):
        # Create a 9x9 grid of cells
        self.board: List[List[SudokuCell]] = [
            [SudokuCell() for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)
        ]
        self.initialize_board()

    def initialize_from_array(self, initial_board: List[List[int]]):
        """
        Initialize the board from a 2D array representation.
        
        Args:
            initial_board: A 9x9 array where 0 represents empty cells and 1-9 are initial values
        """
        # First create the cells with fixed values
        self.board = []
        for i in range(BOARD_SIZE):
            row = []
            for j in range(BOARD_SIZE):
                value = initial_board[i][j]
                if value != 0:
                    # Create a cell with a fixed value
                    cell = SudokuCell(fixed_value=value)
                else:
                    # Create an empty cell
                    cell = SudokuCell()
                row.append(cell)
            self.board.append(row)
        
        # Then initialize possibilities for the empty cells
        self.initialize_board()

    def initialize_board(self):
        """
        Initialize the board's cells.
        
        For each cell that does not have a fixed value (or given initial puzzle value),
        assign the full set of valid digits as possibilities with equal probability.
        Here we assume an empty board: you could adapt this to an initial puzzle by setting
        fixed values before calling this method.
        """
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                cell = self.board[i][j]
                if cell.fixed_value is None:
                    valid_candidates = self.get_valid_candidates(i, j)
                    if valid_candidates:
                        probability = 1.0 / len(valid_candidates)
                        cell.possibilities = {num: probability for num in valid_candidates}

    def get_valid_candidates(self, row: int, col: int) -> List[int]:
        """
        Get valid candidates for the cell at position (row, col)
        by excluding digits already fixed in the same row, column, or block.
        """
        used = set()

        # Get numbers in the same row
        used.update(self.get_row_values(row))
        # Get numbers in the same column
        used.update(self.get_column_values(col))
        # Get numbers in the same block
        used.update(self.get_block_values(row, col))
        
        # Exclude the already used numbers
        valid = list(DIGITS - used)
        return valid

    def get_row_values(self, row: int) -> set:
        """Return all fixed values in a given row."""
        return {cell.fixed_value for cell in self.board[row] if cell.fixed_value is not None}

    def get_column_values(self, col: int) -> set:
        """Return all fixed values in a given column."""
        return {self.board[i][col].fixed_value for i in range(BOARD_SIZE) if self.board[i][col].fixed_value is not None}

    def get_block_values(self, row: int, col: int) -> set:
        """Return all fixed values in the block containing the cell (row, col)."""
        block_row_start = (row // BLOCK_SIZE) * BLOCK_SIZE
        block_col_start = (col // BLOCK_SIZE) * BLOCK_SIZE
        values = set()
        for i in range(block_row_start, block_row_start + BLOCK_SIZE):
            for j in range(block_col_start, block_col_start + BLOCK_SIZE):
                if self.board[i][j].fixed_value is not None:
                    values.add(self.board[i][j].fixed_value)
        return values

    def user_assign(self, row: int, col: int, candidates: List[int]):
        """
        Process user input for the cell at (row, col).
        
        If the candidate list contains a single number, collapse the cell to that number.
        If multiple numbers are provided, update the cell's superposition state accordingly.
        Before updating, ensure that the candidates are valid (i.e. they appear in the cell's current possibilities).
        After the update, propagate constraints to all affected cells.
        """
        cell = self.board[row][col]
        
        # Check if the cell is already fixed
        if cell.fixed_value is not None:
            raise ValueError(f"Cannot modify cell ({row}, {col}) as it is already fixed to {cell.fixed_value}")
            
        current_possibilities = set(cell.possibilities.keys())
        if not set(candidates).issubset(current_possibilities):
            raise ValueError(f"User input error: the candidates {candidates} are not all valid for cell ({row}, {col}).")
        
        # Update the cell based on user selection
        if len(candidates) == 1:
            cell.collapse(candidates[0])
        else:
            cell.update_possibilities(candidates)
        
        # Propagate updated constraints to all cells that share the same row, column, and block
        self.propagate_constraints(row, col, candidates)

    def propagate_constraints(self, row: int, col: int, assigned_candidates: List[int]):
        """
        Propagate constraints from the modified cell (row, col) to its neighbors.
        
        Two possible approaches for partial (multi-value) assignments:
          - Exclusive Constraint: Treat the multi-value assignment as reserving those numbers,
            removing them from possibility sets of other cells.
          - Probabilistic Influence: Adjust probability weights to reflect uncertainty.
        
        For simplicity, this implementation uses the exclusive constraint:
          For any neighboring cell (that is not collapsed), remove any candidate that appears in assigned_candidates.
        
        After removal, if a neighboring cell has only one possibility left, automatically collapse it.
        """
        # If single value (collapsed cell), enforce strict Sudoku rules
        if len(assigned_candidates) == 1:
            candidate = assigned_candidates[0]
            neighbors = self.get_neighbors(row, col)
            for n_row, n_col in neighbors:
                neighbor_cell = self.board[n_row][n_col]
                # Skip already collapsed cells
                if neighbor_cell.fixed_value is not None:
                    continue
                
                # Remove this candidate from neighbor's possibilities
                neighbor_cell.remove_candidate(candidate)
        else:
            # For multi-value assignments, use probabilistic constraints
            neighbors = self.get_neighbors(row, col)
            for n_row, n_col in neighbors:
                neighbor_cell = self.board[n_row][n_col]
                # If neighbor is collapsed, skip updating
                if neighbor_cell.is_collapsed():
                    continue
                
                # Remove each assigned candidate from the neighbor possibilities
                # This implements exclusive constraint strategy
                for candidate in assigned_candidates:
                    neighbor_cell.remove_candidate(candidate)
        
        # Add additional validation to ensure no invalid Sudoku state
        self.validate_board_consistency()

    def get_neighbors(self, row: int, col: int) -> List[Tuple[int, int]]:
        """
        Get coordinates of all cells in the same row, column, and block as (row, col)
        excluding the cell itself.
        """
        neighbors = set()
        # Row neighbors
        for j in range(BOARD_SIZE):
            if j != col:
                neighbors.add((row, j))
        # Column neighbors
        for i in range(BOARD_SIZE):
            if i != row:
                neighbors.add((i, col))
        # Block neighbors
        block_row_start = (row // BLOCK_SIZE) * BLOCK_SIZE
        block_col_start = (col // BLOCK_SIZE) * BLOCK_SIZE
        for i in range(block_row_start, block_row_start + BLOCK_SIZE):
            for j in range(block_col_start, block_col_start + BLOCK_SIZE):
                if (i, j) != (row, col):
                    neighbors.add((i, j))
        return list(neighbors)

    def validate_board_consistency(self):
        """
        Validate the entire board for any Sudoku rule violations.
        Ensures that fixed/collapsed cells maintain valid Sudoku constraints across
        rows, columns, and blocks.
        
        Raises:
            ValueError: If any Sudoku rule is violated (duplicate values in row/column/block)
        """
        # Check all rows for duplicates
        for i in range(BOARD_SIZE):
            row_values = self.get_row_values(i)
            if len(row_values) < len([cell for cell in self.board[i] if cell.fixed_value is not None]):
                raise ValueError(f"Row {i} contains duplicate fixed values: {row_values}")
                
        # Check all columns for duplicates
        for j in range(BOARD_SIZE):
            col_values = self.get_column_values(j)
            fixed_in_col = sum(1 for i in range(BOARD_SIZE) if self.board[i][j].fixed_value is not None)
            if len(col_values) < fixed_in_col:
                raise ValueError(f"Column {j} contains duplicate fixed values: {col_values}")
                
        # Check all 3x3 blocks for duplicates
        for block_row in range(0, BOARD_SIZE, BLOCK_SIZE):
            for block_col in range(0, BOARD_SIZE, BLOCK_SIZE):
                # Get all fixed values in this block
                block_values = set()
                fixed_count = 0
                for i in range(block_row, block_row + BLOCK_SIZE):
                    for j in range(block_col, block_col + BLOCK_SIZE):
                        if self.board[i][j].fixed_value is not None:
                            block_values.add(self.board[i][j].fixed_value)
                            fixed_count += 1
                
                if len(block_values) < fixed_count:
                    raise ValueError(f"Block at ({block_row},{block_col}) contains duplicate fixed values: {block_values}")
        
        # Check for cells with no remaining valid candidates
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                cell = self.board[i][j]
                if cell.fixed_value is None and not cell.possibilities:
                    raise ValueError(f"Cell at ({i},{j}) has no valid candidates, making the puzzle unsolvable")

    def serialize_board(self) -> List[List[dict]]:
        """
        Prepare the board state for transmission to a client.
        
        For each cell, if it has a fixed value, return that value.
        Otherwise, return the list of candidates with corresponding probability percentages.
        """
        serialized = []
        for i in range(BOARD_SIZE):
            row_serial = []
            for j in range(BOARD_SIZE):
                cell = self.board[i][j]
                if cell.fixed_value is not None:
                    row_serial.append({"value": cell.fixed_value})
                else:
                    # Display probabilities as percentages rounded to 2 decimals.
                    probs = {num: round(prob * 100, 2) for num, prob in cell.possibilities.items()}
                    row_serial.append({"possibilities": probs})
            serialized.append(row_serial)
        return serialized

    def print_board(self):
        """
        A simple utility function to print the board state to console.
        Collapsed cells show their fixed value, and non-collapsed cells show their probability sets.
        """
        for i in range(BOARD_SIZE):
            row_str = []
            for j in range(BOARD_SIZE):
                cell = self.board[i][j]
                if cell.fixed_value is not None:
                    row_str.append(str(cell.fixed_value))
                else:
                    # Show the candidates (without probabilities) for brevity.
                    row_str.append("{" + ",".join(str(num) for num in sorted(cell.possibilities)) + "}")
            print(" ".join(row_str))
        print("\n")


# --- Testing and Simulation ---

def simulate_game_scenario():
    """
    Run a sample simulation of the Quantum Sudoku game flow:
    
    1. Initialize the board.
    2. Print the initial state.
    3. Process a user input for a cell that assigns multiple candidates.
    4. Print the board after the input to show constraint propagation.
    5. (Optionally) further simulate a single-value assignment and automatic collapses.
    """
    print("Initializing Quantum Sudoku board...")
    board = QuantumSudokuBoard()
    board.print_board()

    # Example: User assigns a multi-value candidate to cell (0,0)
    # (Assumes (0,0) was originally in full superposition; valid candidates derived from sudoku rules.)
    cell_candidates = list(board.board[0][0].possibilities.keys())
    if len(cell_candidates) >= 2:
        # For example, choose two candidates from the available ones (simulate uncertainty)
        selected_candidates = cell_candidates[:2]
    else:
        selected_candidates = cell_candidates

    print(f"User assigns cell (0,0) with candidates {selected_candidates} (partial collapse)")
    board.user_assign(0, 0, selected_candidates)
    board.print_board()

    # Further simulation: Suppose later the user collapses cell (4,4) to a single value.
    valid_at_4_4 = list(board.board[4][4].possibilities.keys())
    if valid_at_4_4:
        chosen_number = valid_at_4_4[0]
        print(f"User collapses cell (4,4) to {chosen_number}")
        board.user_assign(4, 4, [chosen_number])
        board.print_board()

    # Show serialized board state
    serialized = board.serialize_board()
    print("Serialized board state:")
    for row in serialized:
        print(row)


if __name__ == "__main__":
    simulate_game_scenario()
