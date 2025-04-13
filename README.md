# Quantum Sudoku

A quantum-inspired Sudoku game where cells can exist in superposition of multiple values until measured.

## Features

- **Quantum Mechanics Inspiration**: Cells can exist in a superposition of multiple possible values with associated probabilities
- **Multiple Value Assignment**: Users can assign one or multiple values to cells
- **Constraint Propagation**: Changes to one cell propagate through the board following Sudoku rules
- **Interactive UI**: Modern, responsive React frontend with a FastAPI backend

## Project Structure

- **backend/**: FastAPI server with quantum sudoku logic
- **frontend/**: React-based user interface

## Running the Application

### Backend

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the server:
```bash
cd backend
uvicorn api:app --reload
```
The backend will be running at http://localhost:8000

### Frontend

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start the development server:
```bash
cd frontend
npm run dev
```
The frontend will be running at http://localhost:5173

## How to Play

1. **Select a cell** on the board by clicking on it
2. **Choose numbers** from the number picker on the right
   - You can select a single number to fully collapse the cell
   - You can select multiple numbers to keep the cell in a partial superposition
3. **Click "Assign Selected Numbers"** to update the cell
4. **Watch how your choice affects other cells** through constraint propagation

## Technical Details

- The backend models quantum superposition with cells having probabilistic states
- When a cell collapses to a single value, it propagates constraints to related cells
- Partial collapse allows maintaining uncertainty by assigning multiple possible values

## Credits

This project combines concepts from quantum mechanics and classic Sudoku to create a novel gaming experience.
