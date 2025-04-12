import { useState, useEffect } from 'react'
import './App.css'
import SudokuBoard from './components/SudokuBoard'
import InfoPanel from './components/InfoPanel'

function App() {
  const [board, setBoard] = useState(null)
  const [selectedCell, setSelectedCell] = useState(null)
  const [message, setMessage] = useState('Welcome to Quantum Sudoku!')
  const [loading, setLoading] = useState(true)
  const [difficulty, setDifficulty] = useState('medium')

  // Fetch the initial board state when the component mounts
  useEffect(() => {
    fetchBoard()
  }, [])

  const fetchBoard = async () => {
    try {
      setLoading(true)
      const response = await fetch('http://localhost:8000/board')
      const data = await response.json()
      setBoard(data)
      setMessage('Board loaded. Click on a cell to start playing!')
    } catch (error) {
      setMessage('Error loading board: ' + error.message)
      console.error('Error fetching board:', error)
    } finally {
      setLoading(false)
    }
  }

  const resetBoard = async (newDifficulty = difficulty) => {
    try {
      setLoading(true)
      const response = await fetch(`http://localhost:8000/reset?difficulty=${newDifficulty}`, {
        method: 'POST',
      })
      const data = await response.json()
      if (data.success) {
        fetchBoard()
        setDifficulty(newDifficulty)
        setMessage(`Board reset to ${newDifficulty} difficulty!`)
      } else {
        setMessage('Error resetting board: ' + data.message)
      }
    } catch (error) {
      setMessage('Error resetting board: ' + error.message)
      console.error('Error resetting board:', error)
    }
  }

  const assignCellValues = async (row, col, candidates) => {
    try {
      setLoading(true)
      const response = await fetch('http://localhost:8000/assign', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          row,
          col,
          candidates,
        }),
      })
      const data = await response.json()
      if (data.success) {
        setBoard(data.board)
        setMessage(data.message)
      } else {
        setMessage('Error assigning values: ' + data.detail)
      }
    } catch (error) {
      setMessage('Error assigning values: ' + error.message)
      console.error('Error assigning values:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCellClick = (row, col) => {
    setSelectedCell({ row, col })
    
    // Get the current possibilities for this cell
    if (board && board[row] && board[row][col]) {
      const cell = board[row][col]
      if (cell.value !== undefined) {
        setMessage(`Cell (${row}, ${col}) is already fixed to ${cell.value}`)
      } else {
        const possibilities = Object.keys(cell.possibilities).map(Number).sort()
        setMessage(`Cell (${row}, ${col}) - Select numbers from: ${possibilities.join(', ')}`)
      }
    }
  }

  const handleNumberSelection = (numbers) => {
    if (!selectedCell) {
      setMessage('Please select a cell first!')
      return
    }

    const { row, col } = selectedCell
    if (board[row][col].value !== undefined) {
      setMessage(`Cell (${row}, ${col}) is already fixed and cannot be changed.`)
      return
    }

    // Validate that the numbers are in the cell's current possibilities
    const currentPossibilities = Object.keys(board[row][col].possibilities).map(Number)
    const validNumbers = numbers.filter(n => currentPossibilities.includes(n))
    
    if (validNumbers.length === 0) {
      setMessage('Selected numbers are not valid for this cell!')
      return
    }

    if (validNumbers.length !== numbers.length) {
      setMessage(`Only ${validNumbers.join(', ')} are valid for this cell.`)
    }

    assignCellValues(row, col, validNumbers)
  }

  const handleDifficultyChange = (newDifficulty) => {
    if (newDifficulty !== difficulty) {
      resetBoard(newDifficulty)
    }
  }

  return (
    <div className="app-container">
      <header>
        <h1>Quantum Sudoku</h1>
        <p>Where numbers exist in quantum superposition until you decide!</p>
      </header>

      <main>
        <div className="game-container">
          {loading ? (
            <div className="loading">Loading...</div>
          ) : (
            <div className="sudoku-container">
              <SudokuBoard 
                board={board} 
                selectedCell={selectedCell}
                onCellClick={handleCellClick} 
              />
              <div className="probability-explanation">
                <span>Probability: </span>
                <span className="low-prob"></span> <span>Lower</span>
                <span className="high-prob"></span> <span>Higher</span>
              </div>
            </div>
          )}
          
          <InfoPanel 
            message={message}
            selectedCell={selectedCell}
            cellData={selectedCell && board ? board[selectedCell.row][selectedCell.col] : null}
            onNumberSelection={handleNumberSelection}
            onReset={resetBoard}
            difficulty={difficulty}
            onDifficultyChange={handleDifficultyChange}
          />
        </div>
      </main>
      
      <footer>
        <p>A quantum-inspired sudoku game</p>
      </footer>
    </div>
  )
}

export default App
