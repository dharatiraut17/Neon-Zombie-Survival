<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Battlegrounds Survival - 10 Levels</title>
    <style>
        body {
            margin: 0;
            overflow: hidden;
            background: #202820; /* Dark Grass Color */
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            touch-action: none;
        }
        canvas {
            display: block;
        }
        #ui-layer {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            display: flex;
            flex-direction: column;
            justify_content: space-between;
        }
        #hud {
            padding: 20px;
            display: flex;
            justify-content: space-between;
            color: #fff;
            font-size: 20px;
            font-weight: 800;
            text-transform: uppercase;
            text-shadow: 2px 2px 0 #000;
        }
        .hud-box {
            background: rgba(0,0,0,0.5);
            padding: 10px 20px;
            border-radius: 5px;
            border: 1px solid #555;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .hud-label { color: #ffcc00; font-size: 14px; }
        .hud-value { font-size: 24px; }
        
        #health-bar-container {
            width: 200px;
            height: 20px;
            background: rgba(0,0,0,0.8);
            border: 2px solid #fff;
            border-radius: 4px;
            overflow: hidden;
            transform: skewX(-15deg);
            margin-top: 5px;
        }
        #health-fill {
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, #ff9900, #ffff00);
            transition: width 0.2s;
        }
        
        /* Level Up Notification */
        #level-up-screen {
            position: absolute;
            top: 20%;
            width: 100%;
            text-align: center;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.5s;
        }
        #level-up-text {
            font-size: 60px;
            color: #00ff00;
            text-shadow: 0 0 20px #000;
            font-weight: 900;
            font-style: italic;
        }

        .screen {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.85);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            pointer-events: auto;
            backdrop-filter: blur(5px);
            z-index: 10;
        }
        h1 {
            color: #ffcc00;
            font-size: 56px;
            margin-bottom: 10px;
            text-shadow: 3px 3px 0 #000;
            text-align: center;
            font-style: italic;
        }
        p {
            color: #fff;
            margin-bottom: 30px;
            text-align: center;
            font-size: 18px;
            text-shadow: 1px 1px 0 #000;
        }
        button {
            background: linear-gradient(180deg, #ffcc00, #ff9900);
            color: #000;
            border: 2px solid #fff;
            padding: 15px 50px;
            font-size: 24px;
            font-weight: bold;
            font-family: inherit;
            cursor: pointer;
            text-transform: uppercase;
            box-shadow: 0 5px 0 #cc7a00;
            border-radius: 5px;
            transition: all 0.1s;
        }
        button:active {
            transform: translateY(4px);
            box-shadow: 0 1px 0 #cc7a00;
        }
        .hidden { display: none !important; }

        /* Mobile Controls */
        .touch-zone {
            position: absolute;
            bottom: 40px;
            width: 140px;
            height: 140px;
            border: 2px solid rgba(255,255,255,0.3);
            border-radius: 50%;
            pointer-events: none;
            display: none; 
            background: rgba(255,255,255,0.1);
        }
        #zone-left { left: 40px; }
        #zone-left::after { content: 'RUN'; position:absolute; top: 50%; left:50%; transform:translate(-50%, -50%); color:rgba(255,255,255,0.6); font-weight:bold;}
        #zone-right { right: 40px; border-color: rgba(255, 200, 0, 0.3); }
        #zone-right::after { content: 'FIRE'; position:absolute; top: 50%; left:50%; transform:translate(-50%, -50%); color:rgba(255,200,0,0.6); font-weight:bold;}

        @media (max-width: 768px) {
            .touch-zone { display: block; }
        }
    </style>
</head>
<body>

    <canvas id="gameCanvas"></canvas>

    <!-- Level Up Text -->
    <div id="level-up-screen">
        <div id="level-up-text">LEVEL UP!</div>
    </div>

    <div id="ui-layer">
        <div id="hud">
            <div class="hud-box">
                <span class="hud-label">LEVEL</span>
                <span class="hud-value" id="level-display">1</span>
            </div>
            
            <div style="text-align:center">
                <div id="health-bar-container"><div id="health-fill"></div></div>
                <div style="color:#fff; font-size:12px; margin-top:5px;">HP</div>
            </div>

            <div class="hud-box">
                <span class="hud-label">KILLS</span>
                <span class="hud-value" id="score">0</span>
            </div>
        </div>
        
        <div id="zone-left" class="touch-zone"></div>
        <div id="zone-right" class="touch-zone"></div>
    </div>

    <!-- Start Screen -->
    <div id="start-screen" class="screen">
        <h1>SURVIVOR BATTLE</h1>
        <p>Complete 10 Levels of Zombie Waves<br>Audio Enabled</p>
        <button onclick="startGame()">START MISSION</button>
    </div>

    <!-- Game Over Screen -->
    <div id="game-over-screen" class="screen hidden">
        <h1 id="go-title" style="color: #ff3333;">KHEL KHATAM</h1>
        <p id="go-msg">You survived until Level 1</p>
        <button onclick="resetGame()">REPLAY</button>
    </div>

    <script>
        // --- AUDIO SYSTEM (Web Audio API) ---
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        let audioCtx;

        function initAudio() {
            if (!audioCtx) {
                audioCtx = new AudioContext();
            }
            if (audioCtx.state === 'suspended') {
                audioCtx.resume();
            }
        }

        function playSound(type) {
            if (!audioCtx) return;
            const osc = audioCtx.createOscillator();
            const gainNode = audioCtx.createGain();
            osc.connect(gainNode);
            gainNode.connect(audioCtx.destination);

            const now = audioCtx.currentTime;

            if (type === 'shoot') {
                // Gunshot: Short decay, Sawtooth
                osc.type = 'sawtooth';
                osc.frequency.setValueAtTime(800, now);
                osc.frequency.exponentialRampToValueAtTime(100, now + 0.1);
                gainNode.gain.setValueAtTime(0.3, now);
                gainNode.gain.exponentialRampToValueAtTime(0.01, now + 0.1);
                osc.start(now);
                osc.stop(now + 0.1);
            } 
            else if (type === 'hit') {
                // Zombie Hit: Low thud
                osc.type = 'square';
                osc.frequency.setValueAtTime(150, now);
                osc.frequency.exponentialRampToValueAtTime(50, now + 0.1);
                gainNode.gain.setValueAtTime(0.2, now);
                gainNode.gain.linearRampToValueAtTime(0, now + 0.1);
                osc.start(now);
                osc.stop(now + 0.1);
            }
            else if (type === 'levelup') {
                // Level Up: Arpeggio
                osc.type = 'sine';
                gainNode.gain.value = 0.3;
                
                osc.frequency.setValueAtTime(440, now);
                osc.frequency.setValueAtTime(554, now + 0.1); // C#
                osc.frequency.setValueAtTime(659, now + 0.2); // E
                osc.frequency.setValueAtTime(880, now + 0.3); // A
                
                gainNode.gain.setValueAtTime(0.3, now);
                gainNode.gain.linearRampToValueAtTime(0, now + 0.6);
                
                osc.start(now);
                osc.stop(now + 0.6);
            }
            else if (type === 'win') {
                // Victory sound
                 osc.type = 'triangle';
                 osc.frequency.setValueAtTime(523.25, now);
                 osc.frequency.setValueAtTime(659.25, now+0.2);
                 osc.frequency.setValueAtTime(783.99, now+0.4);
                 osc.frequency.setValueAtTime(1046.50, now+0.6);
                 gainNode.gain.linearRampToValueAtTime(0, now + 1.0);
                 osc.start(now);
                 osc.stop(now + 1.0);
            }
        }

        // --- GAME ENGINE ---

        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        
        // Game State
        let gameRunning = false;
        let animationId;
        
        // Level System
        let level = 1;
        const MAX_LEVEL = 10;
        let score = 0;
        let levelKills = 0;
        let killsToNextLevel = 10;
        
        // Entities
        let player;
        let bullets = [];
        let zombies = [];
        let particles = [];

        // Inputs
        const keys = { w: false, a: false, s: false, d: false };
        const mouse = { x: 0, y: 0, down: false };
        const touchInput = { active: false, moveX: 0, moveY: 0, shootX: 0, shootY: 0, shooting: false };

        function resize() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }
        window.addEventListener('resize', resize);
        resize();

        // --- Helper: Draw Humanoid (Player/Zombie) ---
        function drawHumanoid(ctx, x, y, radius, angle, colorSkin, colorClothes, isZombie) {
            ctx.save();
            ctx.translate(x, y);
            ctx.rotate(angle);

            // Shoulders/Body
            ctx.fillStyle = colorClothes;
            ctx.beginPath();
            ctx.roundRect(-12, -10, 24, 20, 5); 
            ctx.fill();

            // Arms
            ctx.fillStyle = isZombie ? colorSkin : colorClothes; 
            if (isZombie) {
                ctx.beginPath();
                ctx.roundRect(10, -12, 15, 6, 3); 
                ctx.roundRect(10, 6, 15, 6, 3);
                ctx.fill();
            } else {
                ctx.beginPath();
                ctx.roundRect(0, -12, 20, 6, 3); 
                ctx.roundRect(0, 6, 20, 6, 3);
                ctx.fill();
                // Gun
                ctx.fillStyle = '#1a1a1a';
                ctx.fillRect(15, -4, 25, 8);
            }

            // Head
            ctx.beginPath();
            ctx.arc(0, 0, radius * 0.7, 0, Math.PI * 2);
            ctx.fillStyle = colorSkin;
            ctx.fill();

            // Helmet / Details
            if (!isZombie) {
                ctx.beginPath();
                ctx.arc(0, 0, radius * 0.65, 0, Math.PI * 2);
                ctx.fillStyle = '#3a4a3a'; 
                ctx.fill();
            } else {
                ctx.fillStyle = '#8a0a0a';
                ctx.beginPath();
                ctx.arc(4, -3, 3, 0, Math.PI*2);
                ctx.fill();
            }
            ctx.restore();
        }

        // --- Classes ---

        class Player {
            constructor() { this.reset(); }
            reset() {
                this.x = canvas.width / 2;
                this.y = canvas.height / 2;
                this.radius = 16;
                this.speed = 4;
                this.hp = 100;
                this.maxHp = 100;
                this.angle = 0;
                this.lastShot = 0;
                this.fireRate = 120;
            }
            draw() { drawHumanoid(ctx, this.x, this.y, this.radius, this.angle, '#ffdbac', '#556b2f', false); }
            update() {
                let dx = 0, dy = 0;
                if (touchInput.active) {
                    dx = touchInput.moveX * this.speed;
                    dy = touchInput.moveY * this.speed;
                } else {
                    if (keys.w) dy -= this.speed;
                    if (keys.s) dy += this.speed;
                    if (keys.a) dx -= this.speed;
                    if (keys.d) dx += this.speed;
                }
                this.x += dx;
                this.y += dy;
                this.x = Math.max(this.radius, Math.min(canvas.width - this.radius, this.x));
                this.y = Math.max(this.radius, Math.min(canvas.height - this.radius, this.y));

                if (touchInput.active && (touchInput.shootX !== 0 || touchInput.shootY !== 0)) {
                    this.angle = Math.atan2(touchInput.shootY, touchInput.shootX);
                } else if (!touchInput.active) {
                    this.angle = Math.atan2(mouse.y - this.y, mouse.x - this.x);
                }

                const now = Date.now();
                if ((mouse.down || touchInput.shooting) && now - this.lastShot > this.fireRate) {
                    this.shoot();
                    this.lastShot = now;
                }
            }
            shoot() {
                const muzzleDist = 30;
                const bx = this.x + Math.cos(this.angle) * muzzleDist;
                const by = this.y + Math.sin(this.angle) * muzzleDist;
                particles.push(new Particle(bx, by, '#ffff00', 3, 0.5));
                bullets.push(new Bullet(bx, by, this.angle));
                playSound('shoot');
            }
        }

        class Bullet {
            constructor(x, y, angle) {
                this.x = x;
                this.y = y;
                this.vx = Math.cos(angle) * 18;
                this.vy = Math.sin(angle) * 18;
                this.radius = 2;
            }
            draw() {
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                ctx.fillStyle = '#ffaa00';
                ctx.fill();
            }
            update() { this.x += this.vx; this.y += this.vy; }
        }

        class Zombie {
            constructor() {
                if (Math.random() < 0.5) {
                    this.x = Math.random() < 0.5 ? -30 : canvas.width + 30;
                    this.y = Math.random() * canvas.height;
                } else {
                    this.x = Math.random() * canvas.width;
                    this.y = Math.random() < 0.5 ? -30 : canvas.height + 30;
                }
                // Difficulty increases with level
                let baseSpeed = 1.5 + (level * 0.2); 
                this.speed = baseSpeed + Math.random();
                this.radius = 16;
                this.hp = 2 + Math.floor(level / 2); // HP increases slightly every 2 levels
                
                const clothes = ['#5a5a5a', '#3e2723', '#263238', '#424242']; 
                this.clothColor = clothes[Math.floor(Math.random() * clothes.length)];
                this.skinColor = '#a8bfa8';
            }
            draw() {
                const angle = Math.atan2(player.y - this.y, player.x - this.x);
                drawHumanoid(ctx, this.x, this.y, this.radius, angle, this.skinColor, this.clothColor, true);
            }
            update() {
                const angle = Math.atan2(player.y - this.y, player.x - this.x);
                this.x += Math.cos(angle) * this.speed;
                this.y += Math.sin(angle) * this.speed;
            }
        }

        class Particle {
            constructor(x, y, color, size, lifeSpeed) {
                this.x = x;
                this.y = y;
                const angle = Math.random() * Math.PI * 2;
                const speed = Math.random() * 4;
                this.vx = Math.cos(angle) * speed;
                this.vy = Math.sin(angle) * speed;
                this.alpha = 1;
                this.color = color;
                this.size = Math.random() * size + 2;
                this.lifeSpeed = lifeSpeed || 0.05;
            }
            draw() {
                ctx.save();
                ctx.globalAlpha = this.alpha;
                ctx.fillStyle = this.color;
                ctx.beginPath();
                ctx.rect(this.x, this.y, this.size, this.size);
                ctx.fill();
                ctx.restore();
            }
            update() {
                this.x += this.vx;
                this.y += this.vy;
                this.alpha -= this.lifeSpeed;
            }
        }

        // --- Logic ---

        function init() {
            player = new Player();
            bullets = [];
            zombies = [];
            particles = [];
            score = 0;
            level = 1;
            levelKills = 0;
            setNextLevelGoal();
            updateUI();
        }

        function setNextLevelGoal() {
            killsToNextLevel = 10 + (level * 5); // 15, 20, 25...
            // Reset zombies when level starts? No, keep it continuous flow
        }

        function checkLevelUp() {
            if (levelKills >= killsToNextLevel) {
                if (level < MAX_LEVEL) {
                    level++;
                    levelKills = 0;
                    setNextLevelGoal();
                    playSound('levelup');
                    
                    // Show notification
                    const el = document.getElementById('level-up-screen');
                    document.getElementById('level-up-text').innerText = "LEVEL " + level;
                    el.style.opacity = 1;
                    setTimeout(() => el.style.opacity = 0, 2000);

                    // Heal player slightly
                    player.hp = Math.min(player.maxHp, player.hp + 20);
                } else {
                    gameWin();
                }
            }
            updateUI();
        }

        function spawnZombie() {
            // Spawn rate increases with level
            const spawnChance = 0.02 + (level * 0.005); 
            if (Math.random() < spawnChance) {
                zombies.push(new Zombie());
            }
        }

        function createBlood(x, y) {
            for (let i = 0; i < 5; i++) {
                particles.push(new Particle(x, y, '#8a0a0a', 4, 0.03));
            }
        }

        function checkCollisions() {
            // Bullets
            for (let i = bullets.length - 1; i >= 0; i--) {
                for (let j = zombies.length - 1; j >= 0; j--) {
                    const b = bullets[i];
                    const z = zombies[j];
                    if (!b || !z) continue;
                    const dist = Math.hypot(b.x - z.x, b.y - z.y);
                    if (dist < z.radius + 10) { 
                        z.hp--;
                        bullets.splice(i, 1);
                        createBlood(z.x, z.y);
                        playSound('hit');
                        if (z.hp <= 0) {
                            zombies.splice(j, 1);
                            score++;
                            levelKills++;
                            checkLevelUp();
                            for(let k=0; k<8; k++) particles.push(new Particle(z.x, z.y, '#8a0a0a', 6, 0.02));
                        }
                        break;
                    }
                }
            }
            // Player
            for (let i = 0; i < zombies.length; i++) {
                const z = zombies[i];
                const dist = Math.hypot(z.x - player.x, z.y - player.y);
                if (dist < z.radius + player.radius) {
                    player.hp -= 0.5; // Damage per frame contact
                    updateUI();
                    if (Math.random() < 0.1) particles.push(new Particle(player.x, player.y, '#ff0000', 3, 0.1));
                    if (player.hp <= 0) gameOver();
                }
            }
        }

        function updateUI() {
            document.getElementById('score').innerText = score;
            document.getElementById('level-display').innerText = level;
            const healthPct = Math.max(0, (player.hp / player.maxHp) * 100);
            document.getElementById('health-fill').style.width = healthPct + '%';
        }

        function drawGround() {
            ctx.fillStyle = '#2b3626'; 
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.strokeStyle = '#323e2d';
            ctx.lineWidth = 2;
            const size = 100;
            for (let x = 0; x < canvas.width; x += size) {
                ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height); ctx.stroke();
            }
            for (let y = 0; y < canvas.height; y += size) {
                ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(canvas.width, y); ctx.stroke();
            }
        }

        function loop() {
            if (!gameRunning) return;
            drawGround();

            player.update();
            player.draw();

            for (let i = bullets.length - 1; i >= 0; i--) {
                bullets[i].update();
                bullets[i].draw();
                if (bullets[i].x < 0 || bullets[i].x > canvas.width || 
                    bullets[i].y < 0 || bullets[i].y > canvas.height) bullets.splice(i, 1);
            }

            spawnZombie();

            for (let i = 0; i < zombies.length; i++) {
                zombies[i].update();
                zombies[i].draw();
            }

            for (let i = particles.length - 1; i >= 0; i--) {
                particles[i].update();
                particles[i].draw();
                if (particles[i].alpha <= 0) particles.splice(i, 1);
            }
            checkCollisions();
            animationId = requestAnimationFrame(loop);
        }

        function startGame() {
            initAudio(); // Initialize sound context
            document.getElementById('start-screen').classList.add('hidden');
            document.getElementById('game-over-screen').classList.add('hidden');
            gameRunning = true;
            init();
            loop();
        }

        function gameOver() {
            gameRunning = false;
            cancelAnimationFrame(animationId);
            document.getElementById('go-title').innerText = "KHEL KHATAM";
            document.getElementById('go-title').style.color = "#ff3333";
            document.getElementById('go-msg').innerText = "Total Kills: " + score + " (Level " + level + ")";
            document.getElementById('game-over-screen').classList.remove('hidden');
        }

        function gameWin() {
            gameRunning = false;
            cancelAnimationFrame(animationId);
            playSound('win');
            document.getElementById('go-title').innerText = "BOOYAH!";
            document.getElementById('go-title').style.color = "#00ff00";
            document.getElementById('go-msg').innerText = "Mission Complete! Kills: " + score;
            document.getElementById('game-over-screen').classList.remove('hidden');
        }

        function resetGame() { startGame(); }

        // --- Input Listeners ---
        window.addEventListener('keydown', e => {
            if (e.key === 'w' || e.key === 'ArrowUp') keys.w = true;
            if (e.key === 'a' || e.key === 'ArrowLeft') keys.a = true;
            if (e.key === 's' || e.key === 'ArrowDown') keys.s = true;
            if (e.key === 'd' || e.key === 'ArrowRight') keys.d = true;
        });
        window.addEventListener('keyup', e => {
            if (e.key === 'w' || e.key === 'ArrowUp') keys.w = false;
            if (e.key === 'a' || e.key === 'ArrowLeft') keys.a = false;
            if (e.key === 's' || e.key === 'ArrowDown') keys.s = false;
            if (e.key === 'd' || e.key === 'ArrowRight') keys.d = false;
        });
        window.addEventListener('mousemove', e => { mouse.x = e.clientX; mouse.y = e.clientY; });
        window.addEventListener('mousedown', () => mouse.down = true);
        window.addEventListener('mouseup', () => mouse.down = false);
        window.addEventListener('touchstart', handleTouch, {passive: false});
        window.addEventListener('touchmove', handleTouch, {passive: false});
        window.addEventListener('touchend', endTouch);

        function handleTouch(e) {
            e.preventDefault();
            touchInput.active = true;
            let moveTouch = null;
            let shootTouch = null;
            for (let i = 0; i < e.touches.length; i++) {
                const t = e.touches[i];
                if (t.clientX < window.innerWidth / 2) moveTouch = t;
                else shootTouch = t;
            }
            if (moveTouch) {
                const centerX = window.innerWidth / 4;
                const centerY = window.innerHeight - 110; 
                const dx = moveTouch.clientX - centerX;
                const dy = moveTouch.clientY - centerY;
                const dist = Math.hypot(dx, dy);
                touchInput.moveX = dx / dist || 0;
                touchInput.moveY = dy / dist || 0;
            } else { touchInput.moveX = 0; touchInput.moveY = 0; }

            if (shootTouch) {
                touchInput.shooting = true;
                const centerX = (window.innerWidth / 4) * 3;
                const centerY = window.innerHeight - 110;
                touchInput.shootX = shootTouch.clientX - centerX;
                touchInput.shootY = shootTouch.clientY - centerY;
            } else { touchInput.shooting = false; }
        }
        function endTouch(e) {
            if (e.touches.length === 0) {
                touchInput.active = false;
                touchInput.moveX = 0;
                touchInput.moveY = 0;
                touchInput.shooting = false;
            } else { handleTouch(e); }
        }
    </script>
</body>
</html>
