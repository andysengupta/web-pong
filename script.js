// Web PONG Game JavaScript

// Game variables
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const startBtn = document.getElementById('startButton');
const resetBtn = document.getElementById('resetButton');
const player1ScoreEl = document.getElementById('player1Score');
const player2ScoreEl = document.getElementById('player2Score');

// Game state
let gameRunning = false;
let animationId;

// Game objects
const game = {
    ball: {
        x: canvas.width / 2,
        y: canvas.height / 2,
        dx: 4,
        dy: 4,
        radius: 10
    },
    player1: {
        x: 10,
        y: canvas.height / 2 - 50,
        width: 10,
        height: 100,
        dy: 0,
        speed: 8
    },
    player2: {
        x: canvas.width - 20,
        y: canvas.height / 2 - 50,
        width: 10,
        height: 100,
        dy: 0,
        speed: 8
    },
    score: {
        player1: 0,
        player2: 0
    }
};

// Key states
const keys = {
    w: false,
    s: false,
    ArrowUp: false,
    ArrowDown: false
};

// Event listeners
document.addEventListener('keydown', (e) => {
    if (e.key in keys) {
        keys[e.key] = true;
        e.preventDefault();
    }
});

document.addEventListener('keyup', (e) => {
    if (e.key in keys) {
        keys[e.key] = false;
        e.preventDefault();
    }
});

startBtn.addEventListener('click', startGame);
resetBtn.addEventListener('click', resetGame);

// Game functions
function startGame() {
    if (!gameRunning) {
        gameRunning = true;
        startBtn.textContent = 'Pause';
        gameLoop();
    } else {
        gameRunning = false;
        startBtn.textContent = 'Start Game';
        cancelAnimationFrame(animationId);
    }
}

function resetGame() {
    gameRunning = false;
    cancelAnimationFrame(animationId);
    
    // Reset positions
    game.ball.x = canvas.width / 2;
    game.ball.y = canvas.height / 2;
    game.ball.dx = 4 * (Math.random() > 0.5 ? 1 : -1);
    game.ball.dy = 4 * (Math.random() > 0.5 ? 1 : -1);
    
    game.player1.y = canvas.height / 2 - 50;
    game.player2.y = canvas.height / 2 - 50;
    
    // Reset scores
    game.score.player1 = 0;
    game.score.player2 = 0;
    updateScore();
    
    startBtn.textContent = 'Start Game';
    draw();
}

function updatePaddles() {
    // Player 1 controls (W/S)
    if (keys.w && game.player1.y > 0) {
        game.player1.y -= game.player1.speed;
    }
    if (keys.s && game.player1.y < canvas.height - game.player1.height) {
        game.player1.y += game.player1.speed;
    }
    
    // Player 2 controls (Arrow Up/Down)
    if (keys.ArrowUp && game.player2.y > 0) {
        game.player2.y -= game.player2.speed;
    }
    if (keys.ArrowDown && game.player2.y < canvas.height - game.player2.height) {
        game.player2.y += game.player2.speed;
    }
}

function updateBall() {
    game.ball.x += game.ball.dx;
    game.ball.y += game.ball.dy;
    
    // Bounce off top and bottom walls
    if (game.ball.y - game.ball.radius <= 0 || game.ball.y + game.ball.radius >= canvas.height) {
        game.ball.dy = -game.ball.dy;
    }
    
    // Check paddle collisions
    // Player 1 paddle
    if (game.ball.x - game.ball.radius <= game.player1.x + game.player1.width &&
        game.ball.y >= game.player1.y &&
        game.ball.y <= game.player1.y + game.player1.height &&
        game.ball.dx < 0) {
        game.ball.dx = -game.ball.dx;
        // Add some angle based on where ball hits paddle
        const hitPos = (game.ball.y - game.player1.y - game.player1.height / 2) / (game.player1.height / 2);
        game.ball.dy += hitPos * 2;
    }
    
    // Player 2 paddle
    if (game.ball.x + game.ball.radius >= game.player2.x &&
        game.ball.y >= game.player2.y &&
        game.ball.y <= game.player2.y + game.player2.height &&
        game.ball.dx > 0) {
        game.ball.dx = -game.ball.dx;
        // Add some angle based on where ball hits paddle
        const hitPos = (game.ball.y - game.player2.y - game.player2.height / 2) / (game.player2.height / 2);
        game.ball.dy += hitPos * 2;
    }
    
    // Check for scoring
    if (game.ball.x < 0) {
        game.score.player2++;
        resetBall();
    } else if (game.ball.x > canvas.width) {
        game.score.player1++;
        resetBall();
    }
}

function resetBall() {
    game.ball.x = canvas.width / 2;
    game.ball.y = canvas.height / 2;
    game.ball.dx = 4 * (Math.random() > 0.5 ? 1 : -1);
    game.ball.dy = 4 * (Math.random() > 0.5 ? 1 : -1);
    updateScore();
}

function updateScore() {
    player1ScoreEl.textContent = game.score.player1;
    player2ScoreEl.textContent = game.score.player2;
}

function draw() {
    // Clear canvas
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Draw center line
    ctx.strokeStyle = '#00ff00';
    ctx.lineWidth = 2;
    ctx.setLineDash([5, 5]);
    ctx.beginPath();
    ctx.moveTo(canvas.width / 2, 0);
    ctx.lineTo(canvas.width / 2, canvas.height);
    ctx.stroke();
    ctx.setLineDash([]);
    
    // Draw paddles
    ctx.fillStyle = '#00ff00';
    ctx.fillRect(game.player1.x, game.player1.y, game.player1.width, game.player1.height);
    ctx.fillRect(game.player2.x, game.player2.y, game.player2.width, game.player2.height);
    
    // Draw ball
    ctx.beginPath();
    ctx.arc(game.ball.x, game.ball.y, game.ball.radius, 0, Math.PI * 2);
    ctx.fill();
}

function gameLoop() {
    if (!gameRunning) return;
    
    updatePaddles();
    updateBall();
    draw();
    
    animationId = requestAnimationFrame(gameLoop);
}

// Initialize game
function init() {
    draw();
    updateScore();
}

// Start when page loads
init();
