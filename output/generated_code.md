Here is the implementation of the Tic Tac Toe game project:

**Project Structure (Directory Layout)**
```
tic-tac-toe/
client/
components/
GameBoard.js
GameLogic.js
index.js
containers/
App.js
index.js
public/
index.html
server/
api/
games.js
moves.js
index.js
models/
Game.js
Move.js
index.js
app.js
package.json
README.md
```
**Key Files with Complete Code Implementations**

**1. `client/components/GameBoard.js`**
```
import React, { useState, useEffect } from 'react';

const GameBoard = () => {
  const [gameBoard, setGameBoard] = useState([
    ['', '', ''],
    ['', '', ''],
    ['', '', '']
  ]);

  const [currentPlayer, setCurrentPlayer] = useState('X');

  const handleMove = (row, col) => {
    if (gameBoard[row][col] === '') {
      const newGameBoard = [...gameBoard];
      newGameBoard[row][col] = currentPlayer;
      setGameBoard(newGameBoard);
      setCurrentPlayer(currentPlayer === 'X' ? 'O' : 'X');
    }
  };

  return (
    <div className="game-board">
      {gameBoard.map((row, rowIndex) => (
        <div key={rowIndex} className="row">
          {row.map((cell, colIndex) => (
            <div key={colIndex} className="cell" onClick={() => handleMove(rowIndex, colIndex)}>
              {cell}
            </div>
          ))}
        </div>
      ))}
    </div>
  );
};

export default GameBoard;
```
This component renders the game board and handles user input (moves).

**2. `client/containers/App.js`**
```
import React from 'react';
import GameBoard from '../components/GameBoard';

const App = () => {
  return (
    <div className="app">
      <GameBoard />
    </div>
  );
};

export default App;
```
This component is the main application container and renders the game board.

**3. `server/api/games.js`**
```
import express from 'express';
import mongoose from 'mongoose';

const router = express.Router();
const Game = mongoose.model('Game');

router.post('/', async (req, res) => {
  const game = new Game();
  await game.save();
  res.json({ gameId: game.id });
});

router.get('/:gameId', async (req, res) => {
  const gameId = req.params.gameId;
  const game = await Game.findById(gameId);
  res.json({ gameBoard: game.gameBoard });
});

export default router;
```
This API endpoint handles creating a new game and retrieving the game board for a specific game.

**4. `server/api/moves.js`**
```
import express from 'express';
import mongoose from 'mongoose';

const router = express.Router();
const Move = mongoose.model('Move');

router.post('/:gameId', async (req, res) => {
  const gameId = req.params.gameId;
  const move = new Move({ gameId, player: req.body.player, square: req.body.square });
  await move.save();
  res.json({ message: 'Move made successfully' });
});

export default router;
```
This API endpoint handles making a move in a specific game.

**5. `server/models/Game.js`**
```
import mongoose from 'mongoose';

const gameSchema = new mongoose.Schema({
  gameBoard: [
    [String],
    [String],
    [String]
  ],
  player1: String,
  player2: String,
  winner: String
});

const Game = mongoose.model('Game', gameSchema);

export default Game;
```
This model defines the Game entity.

**6. `server/models/Move.js`**
```
import mongoose from 'mongoose';

const moveSchema = new mongoose.Schema({
  gameId: { type: mongoose.Schema.Types.ObjectId, ref: 'Game' },
  player: String,
  square: Number
});

const Move = mongoose.model('Move', moveSchema);

export default Move;
```
This model defines the Move entity.

**7. `server/app.js`**
```
import express from 'express';
import mongoose from 'mongoose';
import gamesRouter from './api/games';
import movesRouter from './api/moves';

const app = express();

app.use(express.json());
app.use('/api/games', gamesRouter);
app.use('/api/moves', movesRouter);

mongoose.connect('mongodb://localhost/tic-tac-toe', { useNewUrlParser: true, useUnifiedTopology: true });

app.listen(3000, () => {
  console.log('Server started on port 3000');
});
```
This is the main server file that sets up the Express app and API endpoints.

**8. `package.json`**
```
{
  "name": "tic-tac-toe",
  "version": "1.0.0",
  "scripts": {
    "start": "node server/app.js"
  },
  "dependencies": {
    "express": "^4.17.1",
    "mongoose": "^5.9.20",
    "react": "^17.0.2",
    "react-dom": "^17.0.2"
  }
}
```
This file lists the project dependencies and scripts.

**9. `README.md`**
```
# Tic Tac Toe Game

## Setup

1. Clone the repository: `git clone https://github.com/username/tic-tac-toe.git`
2. Install dependencies: `npm install`
3. Start the server: `npm start`

## Usage

1. Open `http://localhost:3000` in your browser to play the game.
```
This file provides setup and usage instructions for the project.

Note that this implementation uses a simple MongoDB schema and does not include caching, load balancing, or optimized database queries as mentioned in the design document. Those features can be added in a future iteration of the project.