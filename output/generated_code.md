Here is the implementation of the Tic Tac Toe game project based on the provided design documents:

**Project Structure (Directory Layout)**
```
tic-tac-toe/
client/
index.html
styles.css
script.js
server/
app.js
models/
Game.js
Move.js
routes/
game.js
move.js
utils/
database.js
apiGateway.js
config.js
package.json
README.md
```
**Key Files with Complete Code Implementations**

**1. `client/index.html`**
```html
<!DOCTYPE html>
<html>
<head>
  <title>Tic Tac Toe</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <h1>Tic Tac Toe</h1>
  <div id="game-board">
    <table>
      <tr>
        <td id="0-0"></td>
        <td id="0-1"></td>
        <td id="0-2"></td>
      </tr>
      <tr>
        <td id="1-0"></td>
        <td id="1-1"></td>
        <td id="1-2"></td>
      </tr>
      <tr>
        <td id="2-0"></td>
        <td id="2-1"></td>
        <td id="2-2"></td>
      </tr>
    </table>
  </div>
  <button id="new-game">New Game</button>
  <script src="script.js"></script>
</body>
</html>
```
This file is the client-side HTML file that renders the game board and allows users to interact with it.

**2. `client/styles.css`**
```css
#game-board {
  border-collapse: collapse;
}

td {
  width: 50px;
  height: 50px;
  border: 1px solid black;
  text-align: center;
  font-size: 24px;
}

td:hover {
  background-color: #ccc;
}
```
This file is the client-side CSS file that styles the game board.

**3. `client/script.js`**
```javascript
const gameBoard = document.getElementById('game-board');
const newGameButton = document.getElementById('new-game');

let currentPlayer = 'X';
let gameId = null;

gameBoard.addEventListener('click', (event) => {
  const row = event.target.parentElement.rowIndex;
  const col = event.target.cellIndex;
  makeMove(row, col);
});

newGameButton.addEventListener('click', () => {
  startNewGame();
});

async function startNewGame() {
  const response = await fetch('/games', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });
  const gameId = await response.json();
  console.log(`Started new game with ID ${gameId}`);
}

async function makeMove(row, col) {
  const response = await fetch(`/games/${gameId}/moves`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ row, col, player: currentPlayer }),
  });
  const move = await response.json();
  updateGameBoard(move);
  checkGameStatus();
}

function updateGameBoard(move) {
  const cell = document.getElementById(`${move.row}-${move.col}`);
  cell.textContent = move.player;
}

async function checkGameStatus() {
  const response = await fetch(`/games/${gameId}`);
  const game = await response.json();
  if (game.winner) {
    alert(`Game over! Winner is ${game.winner}`);
  }
}
```
This file is the client-side JavaScript file that handles user interactions with the game board and communicates with the server-side API.

**4. `server/app.js`**
```javascript
const express = require('express');
const app = express();
const apiGateway = require('./utils/apiGateway');
const gameLogic = require('./utils/gameLogic');

app.use(express.json());

app.post('/games', async (req, res) => {
  const game = await apiGateway.createGame();
  res.json({ gameId: game.id });
});

app.get('/games/:id', async (req, res) => {
  const gameId = req.params.id;
  const game = await apiGateway.getGame(gameId);
  res.json(game);
});

app.put('/games/:id', async (req, res) => {
  const gameId = req.params.id;
  const game = await apiGateway.updateGame(gameId, req.body);
  res.json(game);
});

app.post('/games/:id/moves', async (req, res) => {
  const gameId = req.params.id;
  const move = await apiGateway.makeMove(gameId, req.body);
  res.json(move);
});

app.listen(3000, () => {
  console.log('Server started on port 3000');
});
```
This file is the server-side Node.js file that sets up the Express.js server and defines the API endpoints.

**5. `server/models/Game.js`**
```javascript
class Game {
  constructor(id, player1, player2, board, winner, createdAt, updatedAt) {
    this.id = id;
    this.player1 = player1;
    this.player2 = player2;
    this.board = board;
    this.winner = winner;
    this.createdAt = createdAt;
    this.updatedAt = updatedAt;
  }
}

module.exports = Game;
```
This file is the server-side model for the Game entity.

**6. `server/models/Move.js`**
```javascript
class Move {
  constructor(id, gameId, player, row, col, createdAt) {
    this.id = id;
    this.gameId = gameId;
    this.player = player;
    this.row = row;
    this.col = col;
    this.createdAt = createdAt;
  }
}

module.exports = Move;
```
This file is the server-side model for the Move entity.

**7. `server/utils/apiGateway.js`**
```javascript
const db = require('./database');

async function createGame() {
  const game = new Game(null, 'X', 'O', [['', '', ''], ['', '', ''], ['', '', '']], null, new Date(), new Date());
  await db.createGame(game);
  return game;
}

async function getGame(gameId) {
  const game = await db.getGame(gameId);
  return game;
}

async function updateGame(gameId, updates) {
  const game = await db.getGame(gameId);
  game.board = updates.board;
  game.winner = updates.winner;
  await db.updateGame(game);
  return game;
}

async function makeMove(gameId, move) {
  const game = await db.getGame(gameId);
  const newMove = new Move(null, gameId, move.player, move.row, move.col, new Date());
  await db.createMove(newMove);
  game.board[move.row][move.col] = move.player;
  await db.updateGame(game);
  return newMove;
}

module.exports = { createGame, getGame, updateGame, makeMove };
```
This file is the server-side API gateway that interacts with the database and performs business logic operations.

**8. `server/utils/database.js`**
```javascript
const mysql = require('mysql');

const db = mysql.createConnection({
  host: 'localhost',
  user: 'root',
  password: 'password',
  database: 'tic_tac_toe',
});

db.connect();

async function createGame(game) {
  const query = `INSERT INTO games (player1, player2, board, winner, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)`;
  const values = [game.player1, game.player2, JSON.stringify(game.board), game.winner, game.createdAt, game.updatedAt];
  await db.query(query, values);
  return game;
}

async function getGame(gameId) {
  const query = `SELECT * FROM games WHERE id = ?`;
  const values = [gameId];
  const result = await db.query(query, values);
  return result[0];
}

async function updateGame(game) {
  const query = `UPDATE games SET board = ?, winner = ?, updated_at = ? WHERE id = ?`;
  const values = [JSON.stringify(game.board), game.winner, game.updatedAt, game.id];
  await db.query(query, values);
  return game;
}

async function createMove(move) {
  const query = `INSERT INTO moves (game_id, player, row, col, created_at) VALUES (?, ?, ?, ?, ?)`;
  const values = [move.gameId, move.player, move.row, move.col, move.createdAt];
  await db.query(query, values);
  return move;
}

module.exports = { createGame, getGame, updateGame, createMove };
```
This file is the server-side database utility that interacts with the MySQL database.

**9. `package.json`**
```json
{
  "name": "tic-tac-toe",
  "version": "1.0.0",
  "scripts": {
    "start": "node server/app.js"
  },
  "dependencies": {
    "express": "^4.17.1",
    "mysql": "^2.18.1"
  }
}
```
This file is the package.json file that defines the project dependencies and scripts.

**10. `README.md`**
```
Tic Tac Toe Game
================

To run the game:

1. Install dependencies: `npm install`
2. Start the server: `npm start`
3. Open a web browser and navigate to `http://localhost:3000`

To play the game:

1. Click on a cell to make a move.
2. Click the "New Game" button to start a new game.
```
This file is the README.md file that provides instructions on how to run and play the game.

Note that this implementation assumes a MySQL database is set up and configured on the local machine. You may need to modify the `database.js` file to connect to a different database or adjust the schema to match your specific database setup.