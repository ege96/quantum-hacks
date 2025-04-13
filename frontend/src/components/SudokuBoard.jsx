import React from 'react';
import './SudokuBoard.css';

const SudokuBoard = ({ board, selectedCell, onCellClick }) => {
  if (!board) return <div>Loading board...</div>;

  // Helper function to convert probability to color
  const getProbabilityColor = (probability) => {
    // Convert probability (0-100) to a white-to-green color
    // Lower probability = more white, higher probability = more green
    const normalizedProb = probability / 100;
    // RGB values: Red and blue decrease with probability, green stays high
    const red = Math.round(255 * (1 - normalizedProb));
    const green = 255;
    const blue = Math.round(255 * (1 - normalizedProb));
    return `rgb(${red}, ${green}, ${blue})`;
  };

  // Helper function to sort possibilities by number
  const sortPossibilities = (possibilities) => {
    // Create an array of [number, probability] pairs and sort by number
    return Object.entries(possibilities)
      .map(([number, probability]) => [parseInt(number, 10), probability])
      .sort((a, b) => a[0] - b[0]);
  };

  return (
    <div className="sudoku-board">
      {board.map((row, rowIndex) => (
        <div key={`row-${rowIndex}`} className="sudoku-row">
          {row.map((cell, colIndex) => {
            // Determine if this cell is selected
            const isSelected = selectedCell && selectedCell.row === rowIndex && selectedCell.col === colIndex;
            
            // Determine if this is a fixed cell or one with possibilities
            const isFixed = cell.value !== undefined;
            
            // Generate CSS classes for the cell
            const cellClasses = [
              'sudoku-cell',
              isSelected ? 'selected' : '',
              isFixed ? 'fixed' : '',
              // Add block styling for visual grouping (3x3 blocks)
              `block-${Math.floor(rowIndex / 3)}-${Math.floor(colIndex / 3)}`
            ].filter(Boolean).join(' ');

            return (
              <div
                key={`cell-${rowIndex}-${colIndex}`}
                className={cellClasses}
                onClick={() => onCellClick(rowIndex, colIndex)}
              >
                {isFixed ? (
                  <div className="fixed-value">{cell.value}</div>
                ) : (
                  <div className="possibilities">
                    {sortPossibilities(cell.possibilities).map(([number, probability]) => (
                      <div 
                        key={`possibility-${rowIndex}-${colIndex}-${number}`} 
                        className="possibility"
                        style={{ 
                          backgroundColor: getProbabilityColor(probability),
                          color: probability > 50 ? '#333' : '#333' // Dark text for better contrast with white/green
                        }}
                        data-probability={`${probability.toFixed(0)}%`}
                      >
                        {number}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      ))}
    </div>
  );
};

export default SudokuBoard; 