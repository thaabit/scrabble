<script setup>
    import { http } from '@/helpers/api.js';
    import { ref, onMounted, onUnmounted, useTemplateRef } from 'vue'
    import { useRoute } from 'vue-router'
    import { useAuthStore } from '@/stores/auth.store.js'
    import Dialog from '@/components/Dialog.vue'

    const route = useRoute()

    const rackLetters = ref([])
    const validPlay = ref(false);
    const board = ref([])
    const playedTiles = ref([])
    const playedCoords = ref(new Map)
    const scores = ref([])
    const whose_turn = ref('')

    const auth_username = useAuthStore().parseJWT().sub
    const rackRow = 16
    const rackStart = 5
    const middle = 8
    const validWords = ref([])
    const playScore = ref(0)
    const gameOverMan = ref(false)
    const letterPoints = {
        'A': 1, 'B': 3, 'C': 3, 'D': 2, 'E': 1, 'F': 4, 'G': 2, 'H': 4, 'I': 1,
        'J': 8, 'K': 5, 'L': 1, 'M': 3, 'N': 1, 'O': 1, 'P': 3, 'Q': 10, 'R': 1,
        'S': 1, 'T': 1, 'U': 1, 'V': 4, 'W': 4, 'X': 8, 'Y': 4, 'Z': 10, '?': 0,
    }
    const dialogBlanks = useTemplateRef('dialogBlanks')
    const dialogExchange = useTemplateRef('dialogExchange')
    const closeBlankLetterReplace = () => dialogBlanks.value?.close()
    const exchangeTile = ref(null)
    const exchangeNo = ref([])
    const exchangeYes = ref([])

    onMounted(() => {
        initializeBoard()
        refreshGame()
        const interval = setInterval(checkRefreshGame, 1000*10)
    })

    onUnmounted(() => {
        console.log('cleared interval', interval);
        clearInterval(interval);
    });

    function checkRefreshGame() {
        if (whose_turn.value !== auth_username) {
            //console.log("refreshing")
            //refreshGame()
        }
    }

    function coordsKey(row, col) {
        return row + "|" + col
    }

    function existingLetter(row, col) {
        return playedCoords.value.get(coordsKey(row, col))
    }

    function refreshGame() {
        validWords.value = []
        playScore.value = 0
        http.get('/game/' + route.params.id).then(response => {
            console.log(response.data)
            let rack_start = 5
            rackLetters.value = []
            response.data.tray.forEach(letter => {
                rackLetters.value.push({
                    letter: letter,
                    row:    rackRow,
                    col:    rack_start++,
                })
                exchangeNo.value.push(letter)
            })
            console.log(exchangeNo.value)
            response.data.moves.forEach(move => {
                playedTiles.value.push(...move)
                move.forEach(tile => {
                    playedCoords.value.set(coordsKey(tile.row, tile.col), tile.letter);
                    board.value[tile.row - 1][tile.col - 1].previous = tile.letter
                    if (tile.sub) board.value[tile.row - 1][tile.col - 1].sub = tile.sub
                    board.value[tile.row-1][tile.col-1].value = letterPoints[tile.letter]
                    //playedCoords.value.push([tile.row, tile.col])
                })
            })
            scores.value = response.data.scores
            gameOverMan.value = response.data.game_over
            whose_turn.value = response.data.whose_turn
        })
        .catch(error => {
            console.log(error)
            const msg = (error.data && error.data.detail) || error.statusText;
            throw new Error(msg);
        });

    }

    function submitPlay(moveType="play", move) {
        console.log(moveType)
        let body = {
            game_id: route.params.id,
            type: moveType
        }
        if (moveType == "exchange") {
            body.data = move
        }
        else if (moveType ==="pass" && !confirm("Do you really want to pass?")) {
            return
        }
        else if (moveType === "play" && validPlay.value) {
            body.data = tilesOnBoard().map(tile => {
                let letter = tile.sub ? tile.letter + tile.sub : tile.letter
                return [letter, tile.row - 1, tile.col - 1].join(':')
            }).join('::')
        }
        http.post('/move', body).then(response => {
            console.log(response)
            refreshGame()
        })
    }

    function exchangeLetters() {
        dialogExchange.value.show()
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

    function validatePlay() {
        if (whose_turn.value !== auth_username) {
            validPlay.value = false;
            return;
        }
        let played = tilesOnBoard()
        if (played.length === 0) {
            console.log("no tiles on board")
            validPlay.value = false
            return
        }

        // middle square
        let hasMiddle = played.filter(tile => tile.row == middle && tile.col == middle).length > 0

        // all letters in same col or row
        let usedCols = playedCols()
        let usedRows = playedRows()
        let playDir = playDirection()
        let isStraight = (playDir != "neither")

        if (!isStraight) {
            validPlay.value = false
            return
        }
        if (isStraight && hasMiddle && played.length > 1) {
            validPlay.value = true;
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
            console.log(cell)
            word += cell.sub || cell.letter || cell.previous
            if (cell.letter && cell.type == 'triple-word') tws++
            if (cell.letter && cell.type == 'double-word') dws++
            col++
            len++
        }
        if (len < 2) return 0
        score *= 3**tws
        score *= 2**dws
        validWords.value.push({ word: word, score: score })
        return score
    }

    function scorePlay() {
        validatePlay()
        validWords.value = []
        playScore.value = 0

        if (!validPlay.value) return 0;
        console.log("valid", validPlay)

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
        if (tilesOnBoard().length === 7) {
            validWords.value.push({ word: "BINGO!", score: 50 })
            score += 50
        }
        console.log(validWords)
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
        return rackLetters.value.filter(tile => tile.row !== rackRow)
    }

    function rackedLetters() {
        return rackLetters.value.filter(tile => tile.row === rackRow)
    }

    function openTrayCols() {
        let taken = rackedLetters().map(tile => tile.col);
        let trayCols = Array.from(new Array(7), (x, i) => i + rackStart);
        return trayCols.filter(index => !taken.includes(index))
    }

    function recallTiles() {
        let openCols = openTrayCols()
        rackLetters.value.forEach(tile => {
            if (tile.row !== rackRow) {
            tile.row = rackRow
            tile.col = openCols.shift()
            }
        })
        scorePlay()
    }

    function shuffleTray() {
        let rando = [...Array(rackedLetters().length).keys()].sort(() => Math.random() - 0.5);
        rackLetters.value.forEach(tile => {
            if (tile.row === rackRow) tile.col = rando.pop() + rackStart
        })
    }

    function dragging(e) {
        let el = e.target;
        el.classList.add('hide');
        e.dataTransfer.setData("index", el.getAttribute("index"));
        let row = Number(el.style.gridRow)
        let col = Number(el.style.gridColumn)
        if (row != rackRow) {
            delete board.value[row-1][col-1].letter
            delete board.value[row-1][col-1].value
        }
    }

    function allowDrop(e) {
        e.preventDefault();
    }

    function swapTiles(e) {
        // two tiles
        let a = rackLetters.value[e.target.getAttribute("index")];
        let b = rackLetters.value[e.dataTransfer.getData("index")]

        // swap tiles
        console.log(a, b)
        a.row = [b.row, b.row = a.row][0]; // swap row of tiles
        a.col = [b.col, b.col = a.col][0]; // swap col of tiles
    }

    function drop(e) {
        e.preventDefault();

        // board cell
        let cell = e.target;
        let row = Number(cell.style.gridRow)
        let col = Number(cell.style.gridColumn)

        // tile
        let data = e.dataTransfer;
        let tile = rackLetters.value[data.getData("index")]
        tile.col = col
        tile.row = row
        tile.onboard = row != rackRow
        if (row != rackRow) {
            board.value[row-1][col-1].letter = tile.letter
            if (tile.sub) board.value[row-1][col-1].sub = tile.sub
            board.value[row-1][col-1].value = modifiedLetterValue(letterPoints[tile.letter], row, col)
            console.log(board.value)
        }

        scorePlay()
        console.log("valid?", validPlay.value)
    }

    function exchangeDragging(e) {
        let el = e.target;
        el.classList.add('hide');
        e.dataTransfer.setData("index", el.getAttribute("index"));
        exchangeTile.value = el
        console.log(exchangeTile.value)
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
        console.log(letters)
        submitPlay("exchange", letters)
        dialogExchange.value.close()
    }

    function nodrop(e) {
        e.target.classList.remove('hide');
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
            dialogBlanks.value.show()
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
        console.log(dialogBlanks)
        dialogBlanks.value.close()
    }

    function playDirection() {
        if (playedRows().length === 1) return "horizontal"
        if (playedCols().length === 1) return "vertical"
        return "neither"

    }
</script>
<template>
    <div v-if="gameOverMan" class="error">GAME OVER MAN</div>
    <Dialog ref="dialogExchange">
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
                v-for="(tile, col) in rackLetters"
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
    <Dialog ref="dialogBlanks">
        <div class="letter-choice">
        <div v-for="(value, letter) in letterPoints" class="tile" @click="pickBlankReplacement(letter)">{{letter}}</div>
        </div>
    </Dialog>

    <div class="scrabble-board" id="board">

        <!-- underlying board -->
        <template v-for="(row, rowIndex) in board">
            <template v-for="(cell, colIndex) in row">
                <div
                        :class="['bonus-text','board-cell', getCellClass(cell)]"
                        v-on:drop="drop"
                        v-on:dragover="allowDrop"
                        :style="{gridColumn: colIndex + 1, gridRow: rowIndex + 1}"
                        >
                        {{ getBonusText(cell.type) }}
                </div>
            </template>
        </template>


        <!-- Rack -->
        <div class="rack-bumper" :style="{gridColumn: 1, gridRow: rackRow, gridColumnEnd: 'span 4'}">
            <div style="padding:5px; background:#555;font-size:larger;margin:0">
            <div v-for="(player) in scores">
                <span v-for="(score, username) in player">
                    <span :class = "(username === whose_turn) ? 'current_turn' : ''">
                        <b>{{ username === auth_username ? "You" : username }} </b>: {{score}}
                    </span>
                </span>
            </div>
            </div>

        </div>
        <div
            v-for="(col) in [...Array(7).keys()]"
            :class="['rack-cell']"
            :style="{gridColumn: col + 5, gridRow: 16}"
            v-on:drop="drop"
            v-on:dragover="allowDrop"
        />
        <div class="rack-bumper" :style="{gridColumn: 12, gridRow: rackRow, gridColumnEnd: 'span 4'}">
            <button @click="shuffleTray">Shuffle</button>
            <button @click="recallTiles">Recall</button>
            <button @click="refreshGame">Refresh</button>
            <button @click="submitPlay('play')" :disabled="(validPlay) ? false : true">Submit</button>
            <button @click="submitPlay('pass')">Pass</button>
            <button @click="exchangeLetters">Exchange</button>
        </div>

        <!-- User Tiles -->
        <div
                v-for="(tile, index) in rackLetters"
                :key="`tile-${index}`"
                :class="['bonus-text','board-cell','tile', validClass(tile), tile.sub ? 'blank' : '']"
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
                {{ tile.sub || tile.letter }}
                <small class="points">{{ letterPoints[tile.letter] || '' }}</small>
        </div>

        <!-- played tiles superimposed on board -->
        <div
            v-for="(tile, index) in playedTiles"
            :key="`played-${index}`"
            :class="['bonus-text','board-cell', 'tile', 'played', tile.sub ? 'blank' : '']"
            :style="{gridColumn: tile.col, gridRow: tile.row}"
            v-on:dragstart="dragging"
            v-on:dragend="nodrop"
            draggable="true"
        >
        {{tile.sub || tile.letter}}
        <small class="points">{{ letterPoints[tile.letter] || '' }}</small>
        </div>
    </div>
    <div
        v-for="(word, index) in validWords"
        :key="`valid-words-${index}`"
    >
    {{word.word}}: {{word.score}}
    </div>
    <div v-if="playScore">{{ playScore }}</div>
</template>

<style scoped>
.rack-bumper {
    border-radius:5px;
}
.scrabble-board {
  display: grid;
  grid-template-columns: repeat(15, 1fr);
  border: 2px solid #333;
  padding: 16px;
  background: #aaa;
  border-radius:15px;
}

.board-row {
  display: flex;
}

.rack-cell {
  aspect-ratio: 1 / 1;
  border: 1px solid #aaa;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: bold;
  position: relative;
  background: #ddd;
  margin:2px;
  border-radius:5px;
}
.board-cell {
  aspect-ratio: 1 / 1;
  border: 1px solid #aaa;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: bold;
  position: relative;
  background: #F8F8F8;
  margin:2px;
  border-radius:5px;
}

.triple-word {
  background: red;
}

.double-word {
  background: darkorange;
  color:white;
}

.triple-letter {
  background: royalblue;
  color:white;
}

.double-letter {
  background: lightblue;
}

.center {
  background: #ffd93d;
}

.letter {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  background: #f8f9fa;
  border: 1px solid #343a40;
}

.points {
  font-size: .3em;
  bottom: 4px;
  right: 4px;
  color:black;
}

.bonus-text {
  font-size: 12px;
  color: white;
}

.has-letter {
  background: #f8f9fa;
}
dialog {
    width:50%;
    border-radius:15px;
}
.letter-choice {
    display:grid;
    grid-template-columns: repeat(7, 1fr);
}
.rack {
  display:grid;
  grid-template-columns: repeat(15, 1fr);
}
.tile {
    font-weight:bold;
    display:block;
    margin:2px;
    font-size:3em;
    border:2px solid black;
    aspect-ratio: 1 / 1;
    background:tan;
    color:black;
    border-radius:5px;
    float:left;
    box-sizing: border-box;
}
.logo {
  height: 6em;
  padding: 1.5em;
  will-change: filter;
  transition: filter 300ms;
}
.logo:hover {
  filter: drop-shadow(0 0 2em #646cffaa);
}
.logo.vue:hover {
  filter: drop-shadow(0 0 2em #42b883aa);
}
[draggable=true] {
  cursor: move;
}
.clearfix:after {
    content: ".";
    display: block;
    clear: both;
    visibility: hidden;
    line-height: 0;
    height: 0;
}
.clearfix {
    display: block;
}
.hide {
  transition: 0.01s;
  transform: translateX(-9999px);
}
.played {
    color: #555;
    border: 1px solid #555;
}
.valid {
    border: 3px solid #0FFF50;
}
.invalid {
    border: 3px solid red !important;
}
.current_turn {
    background: yellow;
    color: orange;
    padding:5px;
}
.blank {
    color:steelblue;
}
</style>
