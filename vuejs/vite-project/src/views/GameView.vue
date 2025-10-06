<template>
<button @click="showMovesDialog">Moves</button>
<button @click="showGamesDialog">Games  <span v-if="turnCount">({{turnCount}})</span></button>
<div class="three-columns">
    <div> <!-- left col -->
        <div v-if="curGame?.finished" class="error">GAME OVER MAN</div>

        <div v-if="curGame" class="cur-game">
            <div :class="(myTurn) ? 'current' : ''" >
                <div class="user">You</div>
                <div class="score">{{curGame.scores[authUsername]}}</div>
            </div>
            <div :class="(!myTurn) ? 'current' : ''" >
                <div class="user">{{curGame.opponent}}</div>
                <div class="score">{{curGame.scores[curGame.opponent]}}</div>
            </div>
        </div>

        <div class="unseen" v-if="curGame">
            <div class="box">
                <div class="title">Unseen Tiles</div>
                <span v-for="(count, letter) in unseenLetters">
                {{ letter.repeat(count) }}
                &nbsp;
                </span>
                <br><br>
                <div>{{ unseenVowels + unseenConsonants }} tiles</div>
                <div>{{ unseenVowels }} vowels | {{ unseenConsonants }} consonants</div>
            </div>
            </div>
        <div>
        </div>

        <div class="box" v-if="playScore">
            <div class="title">Words in Play</div>
        <div
            v-for="(score, word) in playedWords"
            :class="{ 'invalid-word': invalidWords.includes(word) }"
        >
        {{word}}: {{score}}
        </div>
        <div>TOTAL: {{ playScore }}</div>
        </div>
    </div> <!-- end lef col -->

    <div class="centerize"> <!-- main col begin -->
    <Dialog ref="movesDialog">
        <!-- moves -->
        <div class="moves">
        <div v-for="(move) in curGame.moves" :class="['move', move.username===authUsername ? 'you' : '']">
            <div>{{ move.username }}</div>
            <div class="{{move.type}}">{{ move.main_word || move.exchange || move.type.toUpperCase() }}</div>
            <div>{{ move.tally }} +{{ move.score }}</div>
            <div></div>
            <div>{{move.rack}}</div>
            <div>{{ move.tally + move.score }}</div>
        </div>
        </div>
    </Dialog>
    <Dialog ref="gamesDialog">
        <!-- active games -->
        <div class="title">Active Games</div>
        <div class="other-games">
        <div v-for="(game) in games"
            @click="changeGame(game.id)"
            class="game clickable"
        >
        <div :class="(game.my_turn) ? 'current' : ''">
            <div class="user">You {{ game.scores[authUsername] }}</div>
        </div>
        <div :class="(!game.my_turn) ? 'current' : ''">
            <div class="user">{{ game.opponent }} {{ game.scores[game.opponent] }}</div>
        </div>
        </div>
        </div>
    </Dialog>
    <Dialog ref="passDialog">
        <div>You sure about that?</div>
        <button @click="pass(true)">Pass</button>
        <button @click="closePassDialog">Cancel</button>
    </Dialog>
    <Dialog ref="exhangeDialog">
        <div class="letter-choice">
            <div
                v-for="col in 7"
                class="rack-cell"
                :style="{gridColumn: col, gridRow: 1}"
                v-on:dragover="allowDrop"
                v-on:drop="exchangeDrop"
            >
            </div>
            <div
                v-for="col in 7"
                class="board-cell"
                :style="{gridColumn: col, gridRow: 2}"
                v-on:dragover="allowDrop"
                v-on:drop="exchangeDrop"
            ></div>
            <div
                v-for="(tile, col) in playerTiles"
                :key="`exchange-letter-${col}`"
                class="board-cell tile"
                :letter="tile.letter"
                :style="{gridColumn: col + 1, gridRow: 1}"
                v-on:dragstart="exchangeDragging"
                v-on:dragend="nodrop"
                draggable="true"
            >
                {{ tile.sub || tile.letter }}
                <small class="points">{{ letterPoints[tile.letter] || '' }}</small>
            </div>
        </div>
        <button @click="completeExchange">Exchange</button>
    </Dialog>
    <Dialog ref="blanksDialog">
        <div class="letter-choice">
        <div v-for="(value, letter) in letterPoints" class="tile" @click="pickBlankReplacement(letter)">{{letter}}</div>
        </div>
    </Dialog>

    <div class="board" id="board">

        <!-- underlying board -->
        <template v-for="(row, rowIndex) in board">
            <template v-for="(cell, colIndex) in row">
                <div
                        :class="['bonus-text','board-cell', getCellClass(cell)]"
                        v-on:drop="drop"
                        v-on:dragover="allowDrop"
                        :style="{gridColumn: colIndex + 1, gridRow: rowIndex + 1}"
                        @click="placeMarker"
                        >
                        {{ getBonusText(cell.type) }}
                </div>
            </template>
        </template>


        <!-- Rack -->
        <div class="rack-bumper" :style="{gridColumn: 1, gridRow: rackRow, gridColumnEnd: 'span 4'}">
            <button @click="shuffleTray" :disabled="gameOverMan">Shuffle</button>
            <button @click="recallTiles" :disabled="gameOverMan">Recall</button>
        </div>
        <div
            v-for="(col) in [...Array(7).keys()]"
            :class="['board-cell','rack-cell']"
            :style="{gridColumn: col + 5, gridRow: 16}"
            v-on:drop="drop"
            v-on:dragover="allowDrop"
        />
        <div class="rack-bumper" :style="{gridColumn: 12, gridRow: rackRow, gridColumnEnd: 'span 4'}">
            <button @click="play"           :disabled="!myTurn || !validPlay">Submit</button>
            <button @click="pass(false)"    :disabled="!myTurn">Pass</button>
            <button @click="exchange(null)" :disabled="!myTurn">Exchange</button>
        </div>

        <!-- User Tiles -->
        <div
                v-for="(tile, index) in playerTiles"
                :key="`tile-${index}`"
                :class="['tile', validClass(tile), tile.sub ? 'blank' : '']"
                :style="{gridColumn: tile.col, gridRow: tile.row}"
                draggable="true"
                :letter="tile.letter"
                :index="index"
                v-on:dragstart="dragging"
                v-on:dragend="nodrop"
                v-on:dragover="allowDrop"
                v-on:drop="swapTiles"
                @dblclick="showBlankDialog(tile)"
                >
                <div class="tile-letter">
                    <span class="letter">{{ tile.sub || tile.letter }}</span>
                    <small class="points">{{ letterPoints[tile.letter] || '' }}</small>
                </div>
        </div>

        <!-- played tiles superimposed on board -->
        <div
            v-for="(tile, index) in existingTiles"
            :key="`played-${index}`"
            :class="['tile', 'played', tile.sub ? 'blank' : '']"
            :style="{gridColumn: tile.col, gridRow: tile.row}"
            v-on:dragstart="dragging"
            v-on:dragend="nodrop"
            draggable="true"
        >
        <div class="tile-letter">
            <span class="letter">{{tile.sub || tile.letter}}</span>
            <small class="points">{{ letterPoints[tile.letter] || '' }}</small>
        </div>
    </div>
    <div
        @click="changeDirection"
        ref="marker"
        class="hidden marker"
        style="grid-area: 8 / 8"
        @dragover="allowDrop"
        v-on:drop="dropOnMarker"
    >&#9654;</div>
    </div> <!-- board end -->
    </div> <!-- main col end -->

    <div class="hide-mobile"> <!-- column 3 -->

    </div> <!-- column 3 -->
    </div> <!-- three column grid -->
</template>
<script setup>
    import { http } from '@/helpers/api.js';
    import { ref, onMounted, onUnmounted, useTemplateRef, watch } from 'vue'
    import { router } from '@/helpers/router.js'
    import { useRoute } from 'vue-router';
    import { useAuthStore } from '@/stores/auth.store.js'
    import Dialog from '@/components/Dialog.vue'

    const route = useRoute()
    const playerTiles = ref([])
    const validPlay = ref(false);
    const board = ref([])
    const existingTiles = ref([])
    const playedCoords = ref(new Map)
    const scores = ref([])
    const games = ref([])
    const marker = ref(null)
    const textRight = ref(true)

    const authUsername = useAuthStore().parseJWT().sub
    const rackRow = 16
    const rackStart = 5
    const middle = 8
    const playedWords = ref({})
    const invalidWords = ref([])
    const playScore = ref(0)
    const gameOverMan = ref(false)
    const letterPoints = {
        'A': 1, 'B': 3, 'C': 3, 'D': 2, 'E': 1, 'F': 4, 'G': 2, 'H': 4, 'I': 1,
        'J': 8, 'K': 5, 'L': 1, 'M': 3, 'N': 1, 'O': 1, 'P': 3, 'Q': 10, 'R': 1,
        'S': 1, 'T': 1, 'U': 1, 'V': 4, 'W': 4, 'X': 8, 'Y': 4, 'Z': 10, '?': 0,
    }

    const blanksDialog = useTemplateRef('blanksDialog')
    const exhangeDialog = useTemplateRef('exhangeDialog')
    const movesDialog = useTemplateRef('movesDialog')
    const passDialog = useTemplateRef('passDialog')
    const gamesDialog = useTemplateRef('gamesDialog')

    const closeBlankLetterReplace = () => blanksDialog.value?.close()
    const closePassDialog = () => passDialog.value?.close()
    const closegamesDialog = () => gamesDialog.value.close()

    const exchangeTile = ref(null)

    const exchangeNo = ref([])
    const exchangeYes = ref([])
    const myTurn = ref(false)
    const whoseTurn = ref(null)
    const gameId = ref(route?.params?.id)
    const unseenLetters = ref({})
    const unseenConsonants = ref(null)
    const unseenVowels = ref(null)
    const curGame = ref(false)
    const turnCount = ref(0)

    watch(() => route.params.id, (newId, oldId) => {
        gameId.value = newId
        initializeBoard()
        refreshGame()
    })

    let interval
    onMounted(() => {
        initializeBoard()
        refreshGame()
        interval = setInterval(checkRefreshGame, 1000*60)
            window.addEventListener('keydown', function(e) {
                handleKeyPress(e);
            });
    })

    onUnmounted(() => {
        clearInterval(interval);
    });

    function compareTiles(a,b) {
        if (playDirection() == 'horizontal') {
            return a.col - b.col
        }
        else {
            return a.row - b.row
        }

    }

    function lastTile() {
        let sorted = tilesOnBoard().sort(compareTiles);
        return sorted[sorted.length - 1]
    }

    function removeTileAt(row, col) {
        let tile = tileAt(row, col)
        if (!tile) return false

        if (tile.row != rackRow) {
            delete board.value[tile.row-1][tile.col-1].letter
            delete board.value[tile.row-1][tile.col-1].value
            delete board.value[tile.row-1][tile.col-1].sub
        }
        let openCols = openTrayCols()
        tile.col = openCols.shift()
        tile.row = rackRow
        scorePlay()
        return true;
    }

    function showMarker() {
        marker.value.classList.remove("hidden")
        marker.value.style.gridRow = 8
        marker.value.style.gridColumn = 7
        bumpMarker('right')
    }

    function handleKeyPress(e) {
        const key = e.key.toUpperCase()
        const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('');
        let dirs = {
            ARROWLEFT:  'left',
            ARROWRIGHT: 'right',
            ARROWUP:    'up',
            ARROWDOWN:  'down',
        }
        if (key == 'BACKSPACE') {
            bumpMarker(textRight.value ? 'left' : 'up', true)
        }
        else if (key == ' ') {
            e.preventDefault()
            changeDirection()
        }
        else if (key == 'ESCAPE') {
            recallTiles()
        }
        else if (key == 'ENTER') {
            if (myTurn.value && validPlay.value) {
                play()
            }
        }
        else if (dirs[key]) {
            e.preventDefault()
            bumpMarker(dirs[key])
        }
        else if (alphabet.includes(key)) {
            let found = tilesOnRack().some(tile => {
                if (tile.letter === key) {
                    let row = Number(marker.value.style.gridRow)
                    let col = Number(marker.value.style.gridColumn)
                    placeTile(tile, row, col)
                    bumpMarker(textRight.value ? 'right' : 'down')
                    return true
                }
                return false
            })

            if (!found) {
                tilesOnRack().some(tile => {
                    if (tile.letter === '?') {
                        let row = Number(marker.value.style.gridRow)
                        let col = Number(marker.value.style.gridColumn)
                        blankTile.value = tile
                        pickBlankReplacement(key)
                        placeTile(tile, row, col)
                        bumpMarker(textRight.value ? 'right' : 'down')
                        return true
                    }
                    return false
                })
            }
        }
    }

    function nextSquare(row, col, dir) {
        switch (dir) {
        case 'right':
            col++
            if (col > 15) {
                col = 1
                row = row === 15 ? 1 : row + 1
            }
            break;
        case 'left':
            col--;
            if (col < 1) {
                col = 15
                row = row === 1 ? 15 : row - 1
            }
            break;
        case 'up':
            row--
            if (row < 1) {
                row = 15
                col = col === 1 ? 15 : col - 1
            }
            break;
        case 'down':
            row++
            if (row > 15) {
                row = 1
                col = col === 15 ? 1 : col + 1
            }
            break;
        }
        return [row, col]
    }

    function boardAt(row, col) {
        return board.value[row - 1][col - 1]
    }

    // bump marker past any existing tiles
    function bumpMarker(dir=textRight.value ? 'right' : 'down', clobber=false) {
        let [row, col] = nextSquare(Number(marker.value.style.gridRow), Number(marker.value.style.gridColumn), dir)
        let count = 0
        if (clobber) {
            let tile = lastTile()
            if (tile) {
                row = tile.row
                col = tile.col
                removeTileAt(row, col)
            }
        }
        let square = boardAt(row, col)
        while (square && (square.previous || square.letter)) {
            [row, col] = nextSquare(row, col, dir)
            count++
            if (count > 20) break
            square = boardAt(row, col)
        }

        marker.value.style.gridRow = row
        marker.value.style.gridColumn = col
    }

    function changeGame(id) {
        if (id != route?.params?.id) {
            router.push(`/game/${id}`)
            closegamesDialog()
        }
    }

    function changeDirection() {
        textRight.value = !textRight.value
        marker.value.innerHTML = textRight.value ? '&#9654;' : '&#x25BC'
    }

    function placeMarker(e) {
        marker.value.style.gridRow = Number(e.target.style.gridRow)
        marker.value.style.gridColumn = Number(e.target.style.gridColumn)
        marker.value.style.display = 'inline-flex'
    }

    function checkRefreshGame() {
        if (!myTurn) {
            refreshGame()
        }
    }

    function coordsKey(row, col) {
        return row + "|" + col
    }

    function existingLetter(row, col) {
        return playedCoords.value.get(coordsKey(row, col))
    }

    function refreshGameList() {
        http.get('/game?type=active').then(response => {
            games.value = response.data.filter(game => {
                return Number(game.id) !== Number(route.params.id)
            })
            turnCount.value = response.data.filter(game => {
                return game.whose_turn === authUsername
            }).length
            document.title = turnCount.value > 0 ? `(${turnCount}) - Games` : 'Games'
        })
        .catch(error => {
            const msg = (error.data && error.data.detail) || error.statusText;
            throw new Error(msg);
        });
    }

    function refreshGame() {
        refreshGameList()

        playedWords.value = {}
        existingTiles.value = []
        playScore.value = 0
        playerTiles.value = []
        exchangeNo.value = []
        playedCoords.value = new Map
        scores.value = []
        gameOverMan.value = false
        unseenLetters.value = []
        unseenConsonants.value = null
        unseenVowels.value = null
        curGame.value = false


        if (!route?.params.id) return;
        http.get('/game/' + route.params.id).then(response => {
            let rack_start = 5
            response.data.tray.forEach(letter => {
                playerTiles.value.push({
                    index:  letter + rack_start,
                    letter: letter,
                    row:    rackRow,
                    col:    rack_start++,
                })
                exchangeNo.value.push(letter)
            })
            response.data.played_tiles.forEach(move => {
                existingTiles.value.push(...move)
                move.forEach(tile => {
                    playedCoords.value.set(coordsKey(tile.row, tile.col), tile.letter);
                    board.value[tile.row - 1][tile.col - 1].previous = tile.letter
                    if (tile.sub) board.value[tile.row - 1][tile.col - 1].sub = tile.sub
                    board.value[tile.row-1][tile.col-1].value = letterPoints[tile.letter]
                    //playedCoords.value.push([tile.row, tile.col])
                })
            })
            curGame.value = response.data
            scores.value = response.data.scores
            gameOverMan.value = response.data.game_over
            whoseTurn.value = response.data.whose_turn
            myTurn.value = response.data.whose_turn == authUsername && !gameOverMan.value
            unseenLetters.value = response.data.unseen
            unseenVowels.value = response.data.vowels
            unseenConsonants.value = response.data.consonants
            showMarker()
        })
        .catch(error => {
            console.log(error)
            const msg = (error.data && error.data.detail) || error.statusText;
            throw new Error(msg);
        });

    }

    const showMovesDialog = () => movesDialog.value.show()
    const showGamesDialog = () => gamesDialog.value.show()

    function pass(force) {
        if (force) {
            submitPlay('pass')
        } else {
            passDialog.value.show()
        }
    }

    function exchange(data) {
        if (data) {
            submitPlay('exchange', data)
        } else {
            exhangeDialog.value.show()
        }
    }

    function play() {
        if (validPlay.value) {
            let data = tilesOnBoard().map(tile => {
                let letter = tile.sub ? tile.letter + tile.sub : tile.letter
                return [letter, tile.row - 1, tile.col - 1].join(':')
            }).join('::')
            submitPlay('play', data)
        }
    }

    function submitPlay(moveType="play", data=null) {
        let body = {
            game_id: route.params.id,
            type: moveType
        }
        if (data) body.data = data
        http.post('/move', body).then(response => {
            refreshGame()
        })
    }

    function takenCols(row) {
        let taken = new Set();
        return Array.from(taken)
    }

    function takenRows(col) {
        let taken = new Set();
        return Array.from(taken)
    }

    function playedRows() {
        let rows = new Set();
        tilesOnBoard().forEach(letter => rows.add(letter.row));
        return Array.from(rows);
    }

    function playedCols() {
        let cols = new Set();
        tilesOnBoard().forEach(letter => cols.add(letter.col));
        return Array.from(cols);
    }

    function validateWords(words) {
        if (!words.length) return;
        const query_string = words.map(word => `words=${word}`).join('&')
        http.get(`/word?${query_string}`).then(response => {
            invalidWords.value = response.data.invalid
            if (invalidWords.value.length) validPlay.value = false
        })
    }

    function validatePlay() {
        let played = tilesOnBoard()
        if (played.length === 0) {
            validPlay.value = false
            return
        }

        // middle square
        let hasMiddle = played.filter(tile => tile.row == middle && tile.col == middle).length > 0

        // all letters in same col or row
        let usedCols = playedCols()
        let usedRows = playedRows()
        let playDir = playDirection()
        let isStraight = (playDir !== "neither")

        if (!isStraight) {
            validPlay.value = false
            return
        }

        // all letters connected
        let connected = true
        if (playDir === "horizontal") {
            let row = usedRows[0]
            let col = Math.min(...usedCols)
            let end = Math.max(...usedCols)
            while (col <= end) {
                let existing = existingLetter(row, col)
                if (!usedCols.includes(col) && !existing) {
                    connected = false;
                    break
                }
                col++
            }
        }
        else {
            let col = usedCols[0]
            let row = Math.min(...usedRows)
            let end = Math.max(...usedRows)
            while (row <= end) {
                let existing = existingLetter(row, col)
                if (!usedRows.includes(row) && !existing) {
                    connected = false;
                    break
                }
                row++
            }
        }
        if (isStraight && hasMiddle && connected && played.length > 1) {
            validPlay.value = true;
            return
        }

        if (!connected) {
            validPlay.value = false;
            return;
        }

        // touches at least one played tile
        let isTouching = false
        let blankSet = true
        played.forEach(tile => {
            [[0,1],[1,0],[-1,0],[0,-1]].forEach(dir => {
                if (playedCoords.value.get(coordsKey(tile.row + dir[0], tile.col + dir[1]))) {
                    isTouching = true
                    return;
                }
            })

            // blank set
            if (tile.letter === '?' && !tile.sub) {
                blankSet = false
                return;
            }
        })

        if (!blankSet) {
            validPlay.value = false
            return
        }

        // fully valid
        if (isTouching && isStraight && !hasMiddle && played.length >= 1) {
            validPlay.value = true;
            return
        }
        validPlay.value = false;
    }

    function transposeArray(array){
        return array[0].map((_, colIndex) => array.map(row => row[colIndex]));
    }

    function scoreWordAt(row, col, direction) {
        row--
        col--

        let b = board.value
        if (direction == 'vertical') {
            b = transposeArray(b)
            row, col = col, row
            row = [col, col = row][0]; // swap row and col
        }

        // find start of word
        while (true) {
            let cell = b[row][col]
            if (col < 0 || cell.value == null) break;
            col--
        }
        col += 1

        // score to end of word
        let len = 0
        let score = 0
        let tws = 0
        let dws = 0
        let word = ''
        while (true) {
            let cell = b[row][col]
            if (col >= b.length || cell.value == null) break;
            score += cell.value
            word += cell.sub || cell.letter || cell.previous
            if (cell.letter && cell.type == 'triple-word') tws++
            if (cell.letter && cell.type == 'double-word') dws++
            if (cell.letter && cell.type == 'center') dws++
            col++
            len++
        }
        if (len < 2) return 0
        score *= 3**tws
        score *= 2**dws
        playedWords.value[word] = score
        return score
    }

    function scorePlay() {
        validatePlay()
        playedWords.value = {}
        playScore.value = 0

        if (!validPlay.value) return 0;

        let usedRows = playedRows()
        let usedCols = playedCols()
        let score = 0
        if (playDirection() === "horizontal") {
            let row = usedRows[0]
            score += scoreWordAt(row, usedCols[0], "horizontal")
            usedCols.forEach(col => {
                score += scoreWordAt(row, col, "vertical")
            })
        }
        else {
            let col = usedCols[0]
            score += scoreWordAt(usedRows[0], col, "vertical")
            usedRows.forEach(row => {
                score += scoreWordAt(row, col, "horizontal")
            })

        }
        validateWords(Object.keys(playedWords.value))
        if (tilesOnBoard().length === 7) {
            playedWords["BINGO!"] = 50
            score += 50
        }
        playScore.value = score
    }

    function modifiedLetterValue(val, row, col) {
        switch (board.value[row-1][col-1].type) {
            case "double-letter": val *= 2; break;
            case "triple-letter": val *= 3; break;
        }
        return val
    }

    function tileAt(row, col) {
        let out = null
        tilesOnBoard().forEach(tile => {
            if (tile.row === row && tile.col === col) {
                out = tile
                return;
            }
        })
        return out
    }

    function tilesOnBoard() {
        return playerTiles.value.filter(tile => tile.row !== rackRow)
    }

    function tilesOnRack() {
        return playerTiles.value.filter(tile => tile.row === rackRow)
    }

    function openTrayCols() {
        let taken = tilesOnRack().map(tile => tile.col);
        let trayCols = Array.from(new Array(7), (x, i) => i + rackStart);
        return trayCols.filter(index => !taken.includes(index))
    }

    function recallTiles() {
        let openCols = openTrayCols()
        playerTiles.value.forEach(tile => {
            if (tile.row !== rackRow) {
            tile.row = rackRow
            tile.col = openCols.shift()
            }
        })
        scorePlay()
    }

    function shuffleTray() {
        let rando = [...Array(tilesOnRack().length).keys()].sort(() => Math.random() - 0.5);
        playerTiles.value.forEach(tile => {
            if (tile.row === rackRow) tile.col = rando.pop() + rackStart
        })
    }

    function dragging(e) {
        let el = e.target;
        el.classList.add('dragging');

        e.dataTransfer.setData("index", el.getAttribute("index"));
        let row = Number(el.style.gridRow)
        let col = Number(el.style.gridColumn)
        if (row != rackRow) {
            delete board.value[row-1][col-1].letter
            delete board.value[row-1][col-1].value
            delete board.value[row-1][col-1].sub
        }
    }

    function allowDrop(e) {
        e.preventDefault();
    }

    function swapTiles(e) {
        // two tiles
        let a = playerTiles.value[e.target.getAttribute("index")];
        let b = playerTiles.value[e.dataTransfer.getData("index")]

        // swap tiles
        a.row = [b.row, b.row = a.row][0]; // swap row of tiles
        a.col = [b.col, b.col = a.col][0]; // swap col of tiles
    }

    function dropOnMarker(e) {
        drop(e)
        bumpMarker()
    }

    function drop(e) {
        e.preventDefault();

        // board cell
        let cell = e.target;
        let row = Number(cell.style.gridRow)
        let col = Number(cell.style.gridColumn)

        // tile
        let data = e.dataTransfer;
        let tile = playerTiles.value[data.getData("index")]
        placeTile(tile, row, col)
    }

    let placedTiles = []
    function placeTile(tile, row, col) {
        tile.col = col
        tile.row = row
        tile.onboard = row != rackRow
        if (row != rackRow) {
            board.value[row-1][col-1].letter = tile.letter
            if (tile.sub) board.value[row-1][col-1].sub = tile.sub
            board.value[row-1][col-1].value = modifiedLetterValue(letterPoints[tile.letter], row, col)
            placedTiles.push(tile)
        }

        scorePlay()
    }

    function exchangeDragging(e) {
        let el = e.target;
        el.classList.add('dragging');
        e.dataTransfer.setData("index", el.getAttribute("index"));
        exchangeTile.value = el
    }

    function exchangeDrop(e) {
        e.preventDefault();

        exchangeTile.value.style.gridRow = Number(e.target.style.gridRow)
        exchangeTile.value.style.gridColumn = Number(e.target.style.gridColumn)
        if (e.target.style.gridRow == 2) exchangeTile.value.classList.add("exchange-me-please")
    }

    function completeExchange() {
        const letters = Array.from(document.querySelectorAll(".exchange-me-please")).map(tile => {
            return tile.getAttribute("letter")
        }).join("")
        submitPlay("exchange", letters)
        exhangeDialog.value.close()
    }

    function nodrop(e) {
        e.target.classList.remove('dragging');
    }

    function generateItems(count, creator) {
        const result = [];
        for (let i = 0; i < count; i++) {
            result.push(creator(i));
        }
        return result;
    }

    function initializeBoard() {
        // board
        board.value = Array(15).fill().map(() => Array(15).fill().map(() => ({})))

        // tws
        const tripleWordSquares = [[0,0], [0,7], [0,14], [7,0], [7,14], [14,0], [14,7], [14,14]]
        tripleWordSquares.forEach(([row, col]) => {
            board.value[row][col].type = 'triple-word'
        })

        // dws
        const doubleWordSquares = [
            [1,1], [1,13], [2,2], [2,12], [3,3], [3,11], [4,4], [4,10],
            [10,4], [10,10], [11,3], [11,11], [12,2], [12,12], [13,1], [13,13]
        ]
        doubleWordSquares.forEach(([row, col]) => {
            board.value[row][col].type = 'double-word'
        })

        // tls
        const tripleLetterSquares = [
            [1,5], [1,9], [5,1], [5,5], [5,9], [5,13],
            [9,1], [9,5], [9,9], [9,13], [13,5], [13,9]
        ]
        tripleLetterSquares.forEach(([row, col]) => {
            board.value[row][col].type = 'triple-letter'
        })

        // dls
        const doubleLetterSquares = [
            [0,3], [0,11], [2,6], [2,8], [3,0], [3,7], [3,14],
            [6,2], [6,6], [6,8], [6,12], [7,3], [7,11],
            [8,2], [8,6], [8,8], [8,12], [11,0], [11,7], [11,14],
            [12,6], [12,8], [14,3], [14,11]
        ]
        doubleLetterSquares.forEach(([row, col]) => {
            board.value[row][col].type = 'double-letter'
        })

        board.value[7][7].type = 'center'
    }

    function validClass(tile) {
        if (tile.row == rackRow) return ''
        return validPlay.value ? 'valid' : 'invalid'
    }

    function getCellClass(cell) {
        return {
            'triple-word': cell.type === 'triple-word',
            'double-word': cell.type === 'double-word',
            'triple-letter': cell.type === 'triple-letter',
            'double-letter': cell.type === 'double-letter',
            'center': cell.type === 'center',
        }
    }

    function getBonusText(type) {
        const bonusText = {
            'triple-word': 'TW',
            'double-word': 'DW',
            'triple-letter': 'TL',
            'double-letter': 'DL',
            'center': '★'
        }
        return bonusText[type] || ''
    }

    const blankTile = ref()
    const lettersModal = ref()
    function showBlankDialog(tile) {
        if (tile.letter === '?') {
            blankTile.value = tile
            blanksDialog.value.show()
        }
    }

    function pickBlankReplacement(letter) {
        let tile = blankTile.value
        tile.sub = letter
        let row = tile.row
        if (tile.row != rackRow) {
            board.value[row - 1][tile.col - 1].letter = tile.letter
            board.value[row - 1][tile.col - 1].sub = tile.sub
        }
        scorePlay()
        blanksDialog.value.close()
    }

    function playDirection() {
        if (playedRows().length === 1) return "horizontal"
        if (playedCols().length === 1) return "vertical"
        return "neither"

    }
</script>
