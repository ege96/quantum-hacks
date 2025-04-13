import React, { useState } from 'react';
import './InfoPanel.css';

const InfoPanel = ({ 
  message, 
  selectedCell, 
  cellData, 
  onNumberSelection, 
  onReset,
  difficulty = 'medium',
  onDifficultyChange
}) => {
  const [selectedNumbers, setSelectedNumbers] = useState([]);
  
  // Generate numbers 1-9 for the number picker
  const numbers = Array.from({ length: 9 }, (_, i) => i + 1);
  
  const handleNumberToggle = (number) => {
    if (selectedNumbers.includes(number)) {
      // Remove number if already selected
      setSelectedNumbers(selectedNumbers.filter(n => n !== number));
    } else {
      // Add number if not already selected
      setSelectedNumbers([...selectedNumbers, number]);
    }
  };
  
  const handleAssign = () => {
    if (selectedNumbers.length === 0) {
      alert('Please select at least one number!');
      return;
    }
    
    onNumberSelection(selectedNumbers);
    setSelectedNumbers([]); // Reset selections after assignment
  };
  
  const isNumberAvailable = (number) => {
    // If no cell is selected or the cell is fixed, all numbers are disabled
    if (!selectedCell || !cellData || cellData.value !== undefined) {
      return false;
    }
    
    // Check if the number is in the cell's possibilities
    return Object.keys(cellData.possibilities).map(Number).includes(number);
  };

  const handleResetWithDifficulty = (newDifficulty) => {
    // First update the difficulty
    if (onDifficultyChange) {
      onDifficultyChange(newDifficulty);
    } else {
      // Fall back to simple reset if difficulty handler isn't provided
      onReset(newDifficulty);
    }
  };

  return (
    <div className="info-panel">
      <div className="message-box">
        <p>{message}</p>
      </div>
      
      <div className="selection-info">
        {selectedCell ? (
          <p>Selected: Cell ({selectedCell.row}, {selectedCell.col})</p>
        ) : (
          <p>Select a cell on the board</p>
        )}
      </div>
      
      <div className="number-picker">
        <h3>Select Numbers</h3>
        <div className="number-grid">
          {numbers.map(number => (
            <button
              key={`number-${number}`}
              className={`number-button ${selectedNumbers.includes(number) ? 'selected' : ''} ${!isNumberAvailable(number) ? 'disabled' : ''}`}
              onClick={() => handleNumberToggle(number)}
              disabled={!isNumberAvailable(number)}
            >
              {number}
            </button>
          ))}
        </div>
        
        <div className="quantum-explanation">
          <p>
            <strong>Quantum Sudoku:</strong> You can select multiple numbers for a cell,
            representing a quantum superposition of possibilities.
          </p>
        </div>
        
        <div className="action-buttons">
          <button
            className="assign-button"
            onClick={handleAssign}
            disabled={selectedNumbers.length === 0 || !selectedCell}
          >
            Assign Selected Numbers
          </button>
          
          <div className="difficulty-selector">
            <p>Difficulty:</p>
            <div className="difficulty-buttons">
              <button 
                className={`difficulty-button ${difficulty === 'easy' ? 'active' : ''}`}
                onClick={() => handleResetWithDifficulty('easy')}
              >
                Easy
              </button>
              <button 
                className={`difficulty-button ${difficulty === 'medium' ? 'active' : ''}`}
                onClick={() => handleResetWithDifficulty('medium')}
              >
                Medium
              </button>
              <button 
                className={`difficulty-button ${difficulty === 'hard' ? 'active' : ''}`}
                onClick={() => handleResetWithDifficulty('hard')}
              >
                Hard
              </button>
            </div>
          </div>
          
          <button className="reset-button" onClick={() => onReset()}>
            New Game
          </button>
        </div>
      </div>
    </div>
  );
};

export default InfoPanel; 