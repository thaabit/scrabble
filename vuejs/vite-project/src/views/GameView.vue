<template>
<div id="top">
    <template v-if="isAuthenticated">
    <a @click="showGamesDialog">Games  <span v-if="turnCount">({{turnCount}})</span> | </a>
    <RouterLink to="/games">Archive | </RouterLink>
    <RouterLink to="/friends">Friends | </RouterLink>
    <a @click="authStore.logout">Logout</a>
    </template>

    <template v-else>
    <RouterLink to="/signup">Signup | </RouterLink>
    <RouterLink to="/login">Login</RouterLink>
    </template>
</div>
<div class="two-columns">
    <div> <!-- left col -->
        <div v-if="curGame?.finished" class="error">GAME OVER MAN</div>

        <div v-if="curGame" class="cur-game">
            <div :class="['you', myTurn ? 'current' : '']" >
                <div class="title">You ({{authUsername}})</div>
                <div class="score">{{curGame.scores[authUsername]}}
                <span v-if="playScore">+{{ playScore }}</span></div>
            </div>
            <div :class="['play']">
                <div v-if="lastMove">
                    <div class="box">{{ lastMove.username }} - {{ lastMove.main_word || lastMove.exchange || lastMove.type.toUpperCase() }} {{lastMove.score > 0 ? '+' : ''}}{{lastMove.score}}
                    <a @click="showMovesDialog" style="padding-left:10px; color:#aaa;">&#x25BC;</a>
                    </div>
                </div>

                <div v-if="playScore" class="word-scores">
                <template
                v-for="play in playedWords"
                >
                <div :class="{ 'invalid-word': invalidWords.includes(play[0]) }">{{play[0]}}</div><div>{{play[1]}}</div>
                </template>
                </div>
            </div>
            <div :class="['other', (!myTurn) ? 'current' : '']" >
                <div class="title">{{curGame.opponent}}</div>
                <div class="score">{{curGame.scores[curGame.opponent]}}</div>
            </div>
        </div>

        <div class="unseen" v-if="curGame">
            <div class="box">
                <div class="title">Unseen Tiles</div>
                <span v-for="(count, letter) in unseen.tiles">
                {{ letter.repeat(count) }}
                &nbsp;
                </span>
                <hr>
                <div>{{ unseen.vowels + unseen.consonants }} tiles ({{ unseen.bag }} in bag) || {{ unseen.vowels }} vowels | {{ unseen.consonants }} consonants</div>
            </div>
            </div>
        <div>
        </div>

    </div> <!-- end lef col -->

    <div class="centerize"> <!-- main col begin -->
    <Dialog ref="newGameDialog">
        <div v-for="(user) in allUsers">{{user}} <button @click="newGame(user)">New Game</button></div>
    </Dialog>
    <Dialog ref="movesDialog">
        <!-- moves -->
        <div v-if="curGame.moves" class="moves">
        <div v-for="(move) in curGame.moves" :class="['move', move.username===authUsername ? 'you' : '']">
            <div>{{ move.username }}</div>
            <div class="{{move.type}}">{{ move.main_word || move.exchange || move.type.toUpperCase() }}</div>
            <div>{{ move.tally }} {{move.score > 0 ? '+' : ''}} {{ move.score }}</div>
            <div></div>
            <div>{{move.rack}}</div>
            <div>{{ move.tally + move.score }}</div>
        </div>
        </div>
        <div v-else>No moves yet</div>
    </Dialog>
    <Dialog ref="gamesDialog">

        <!-- active games -->
        <div class="title">Active Games
            <button @click="showNewGameDialog">New Game</button>
        </div>
        <div class="other-games">
            <div v-for="(game) in active_games"
                @click="changeGame(game.id)"
                class="game clickable"
            >
            <div :class="(game.my_turn) ? 'current' : ''">
                <div class="user">You {{ game.scores[authUsername] }}</div>
            </div>
            <div :class="(!game.my_turn) ? 'current' : ''">
                <div class="user">{{ game.opponent }} {{ game.scores[game.opponent] }}</div>
            </div>
            <div>
            <button @click="changeGame(game.id)">Go</button>
            </div>
        </div>
        </div>

        <!--unacknowledged finished games-->
        <div class="title" v-if="finished_games.length > 0">Finished Games</div>
        <div class="other-games">
        <div v-for="(game) in finished_games"
            @click="changeGame(game.id)"
            class="game clickable"
        >
            <div>
                <div class="user">You {{ game.scores[authUsername] }}</div>
            </div>
            <div>
                <div class="user">{{ game.opponent }} {{ game.scores[game.opponent] }}</div>
            </div>
            <div>
            <button @click.prevent="acknowledge_game(game.id)">Dismiss</button>
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
            >
            </div>
            <div
                v-for="col in 7"
                class="board-cell"
                :style="{gridColumn: col, gridRow: 2}"
            ></div>
            <div
                v-for="(tile) in exchangeTiles"
                :key="`exchange-letter-${tile.col}`"
                class="tile"
                :letter="tile.letter"
                :style="{gridColumn: tile.col, gridRow: tile.row}"
                @click="toggleExchange"
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
                        :style="{gridColumn: colIndex + 1, gridRow: rowIndex + 1}"
                        @drop="drop"
                        @dragover="allowDrop"
                        @click="placeMarker"
                        >
                        {{ getBonusText(cell.type) }}
                </div>
            </template>
        </template>


        <!-- Rack -->
        <div class="rack-bumper" :style="{gridColumn: 1, gridRow: rackRow, gridColumnEnd: 'span 4'}">
            <img @click="showKeyboard" src="/keyboard.svg" class="button-image hide-non-mobile"/>
            <img @click="shuffleTray"  src="/shuffle.svg"  class="button-image"/>
            <img @click="recallAllTiles"  src="/recall.svg"   class="button-image"/>
        </div>
        <div
            v-for="(col) in [...Array(7).keys()]"
            :class="['board-cell','rack-cell']"
            :style="{gridColumn: col + 5, gridRow: 16}"
            @drop="drop"
            @dragover="allowDrop"
        />
        <div class="rack-bumper" :style="{gridColumn: 12, gridRow: rackRow, gridColumnEnd: 'span 4'}">
            <img @click="play" src="/play.svg" :class="['button-image', (!myTurn || !validPlay) ? 'disabled' : '']" />
            <img @click="pass(false)" src="/pass.svg" :class="['button-image', !myTurn ? 'disabled' : '']" />
            <img @click="exchange(null)" src="/exchange.svg" :class="['button-image', !canExchange ? 'disabled' : '']" />
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
                @dragstart="dragging"
                @dragend="nodrop"
                @dragover="allowDrop"
                @drop="swapTiles"
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
            :class="['tile', 'played', tile.sub ? 'blank' : '', tile.most_recent_play ? 'last-play' : '']"
            :style="{gridColumn: tile.col, gridRow: tile.row}"
            @dragstart="dragging"
            @dragend="nodrop"
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
        @drop="dropOnMarker"
    >&#9654;</div>
    </div> <!-- board end -->
    <input ref="hiddenInput" class="hidden-input">
    </div> <!-- main col end -->

    <div class="hide-mobile"> <!-- column 3 -->

    </div> <!-- column 3 -->
    </div> <!-- three column grid -->
</template>
<script setup>
    import { http } from '@/helpers/api.js';
    import { ref, computed, onMounted, onUnmounted, useTemplateRef, watch } from 'vue'
    import { router } from '@/helpers/router.js'
    import { useRoute } from 'vue-router';
    import { useAuthStore } from '@/stores/auth.store.js'
    import Dialog from '@/components/Dialog.vue'

    import { storeToRefs } from 'pinia'

    const route = useRoute()
    const currentRouteName = computed(() => router.currentRoute.value.name);
    const playerTiles = ref([])
    const exchangeTiles = ref([])
    const board = ref([])
    const existingTiles = ref([])
    const scores = ref([])
    const active_games = ref([])
    const finished_games = ref([])
    const marker = ref(null)
    const textRight = ref(true)

    const authUsername = useAuthStore().parseJWT().sub
    const rackRow = 16
    const rackStart = 5
    const middle = 8
    const playedWords = ref([])
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

    const hiddenInput = useTemplateRef('hiddenInput')

    const closeBlankLetterReplace = () => blanksDialog.value?.close()
    const closePassDialog  = () => passDialog.value.close()
    const closeGamesDialog = () => gamesDialog.value.close()

    const exchangeTile = ref(null)

    const exchangeNo = ref([])
    const exchangeYes = ref([])
    const whoseTurn = ref(null)
    const gameId = ref(route?.params?.id)
    const unseen = ref(null)
    const bagCount = 0
    const curGame = ref(false)
    const lastMove = ref(null)
    const turnCount = ref(0)
    let otherKeydown = false
    let validPlay = false;
    let myTurn = false
    let canExchange = false

    const authStore = useAuthStore();
    const { isAuthenticated, loggedInUser } = storeToRefs(authStore)

    const newGameDialog = useTemplateRef('newGameDialog')
    const showNewGameDialog = () => newGameDialog.value.show()
    const allUsers = ref([])

    watch(() => route.params.id, (newId, oldId) => {
        gameId.value = newId
        initializeGame()
    })

    let interval
    onMounted(() => {
        refreshGameList()
        initializeGame()

        interval = setInterval(checkRefreshGame, 1000*60)
        window.addEventListener('keydown', handleKeyPress)
        window.addEventListener('keyup', handleKeyUp)

        http.get('/user').then(response => {
            allUsers.value = response.data
        })
        .catch(error => {
            warn(error)
            const msg = (error.data && error.data.detail) || error.statusText;
            throw new Error(msg);
        })
        if (!route?.params.id) return showGamesDialog();
    })


    onUnmounted(() => {
        window.removeEventListener('keydown', handleKeyPress)
        window.removeEventListener('keyup', handleKeyUp)
        clearInterval(interval);
    });

    function newGame(other_user) {
        http.post('/game', { opponent: other_user }).then(response => {
            newGameDialog.value.close()
            router.push(`/game/${response.data.id}`)
        })
        .catch(error => {
            warn(error)
            const msg = (error.data && error.data.detail) || error.statusText;
            throw new Error(msg);
        });
    }

    function warn(msg) {
        console.log(msg)
    }

    function compareTiles(a,b) {
        if (playDirection() == 'horizontal') {
            return a.col - b.col
        }
        else {
            return a.row - b.row
        }

    }

    function lastPlayedTile() {
        let sorted = tilesInPlay().sort(compareTiles);
        return sorted[sorted.length - 1]
    }

    // mobile only
    function showKeyboard() {
        hiddenInput.value.style.visibility = 'visible'
        hiddenInput.value.focus()
        hiddenInput.value.select()
        window.scrollTo(0, document.body.scrollHeight);
    }

    function recallTile(tile) {
        if (!tile) return false

        if (tile.row != rackRow) {
            tile.col = openTrayCols().shift()
            tile.row = rackRow
            scorePlay()
        }
        return true;
    }

    function showMarker() {
        marker.value.classList.remove("hidden")
        marker.value.style.gridRow = 8
        marker.value.style.gridColumn = 7
        bumpMarker('right')
    }

    function handleKeyUp(e) {
        otherKeydown = false
    }

    function handleKeyPress(e) {
        const key = e.key.toUpperCase()
        const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('');
        if (otherKeydown || !curGame.value) return
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
            shuffleTray()
        }
        else if (key == 'ESCAPE') {
            recallAllTiles()
        }
        else if (key == 'TAB') {
            e.preventDefault()
            changeDirection()
        }
        else if (key == 'ENTER') {
            e.preventDefault()
            if (!myTurn) alert("not your turn")
            if (myTurn && validPlay) {
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
        else {
            otherKeydown = true
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

    function existingTileAt(row, col) {
        return existingTiles.value.find(tile => { return (tile.row === Number(row) && tile.col === Number(col)) })
    }
    function tileAt(row, col) {
        return playerTiles.value.find(tile => { return (tile.row === Number(row) && tile.col === Number(col)) })
    }
    function anyTileAt(row, col) {
        return existingTileAt(row, col) || tileAt(row, col)
    }

    function tilesInPlay() {
        return playerTiles.value.filter(tile => { return tile.row !== rackRow })
    }

    function tilesOnRack() {
        return playerTiles.value.filter(tile => tile.row === rackRow)
    }


    // bump marker past any existing tiles
    function bumpMarker(dir=textRight.value ? 'right' : 'down', clobber=false) {
        let [row, col] = nextSquare(Number(marker.value.style.gridRow), Number(marker.value.style.gridColumn), dir)
        if (clobber) recallTile(lastPlayedTile())

        let count = 0
        while (anyTileAt(row, col)) {
            [row, col] = nextSquare(row, col, dir)
            count++
            if (count > 20) break
        }

        marker.value.style.gridRow = row
        marker.value.style.gridColumn = col
    }

    function changeGame(id) {
        router.push(`/game/${id}`)
        closeGamesDialog()
        initializeGame()
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
        if (!myTurn) refreshGame()
        refreshGameList()
    }

    function refreshGameList() {
        http.get('/game?type=active').then(response => {
            active_games.value = response.data
            turnCount.value = response.data.filter(game => {
                return game.whose_turn === authUsername
            }).length
            document.title = turnCount.value > 0 ? `(${turnCount.value}) - Games` : 'Games'
        })
        .catch(error => {
            const msg = (error.data && error.data.detail) || error.statusText;
            throw new Error(msg);
        });
        http.get('/game?type=unacknowledged').then(response => {
            finished_games.value = response.data
        })
        .catch(error => {
            const msg = (error.data && error.data.detail) || error.statusText;
            throw new Error(msg);
        });
    }

    const toExchangeTiles = computed(() => {
        return exchangeTiles.value.filter(tile => tile.row === 2)
    })

    function initializeGame() {
        playedWords.value = []
        existingTiles.value = []
        playScore.value = 0
        exchangeTiles.value = []
        exchangeNo.value = []
        scores.value = []
        gameOverMan.value = false
        unseen.value = null
        curGame.value = false
        lastMove.value = null

        initializeBoard()
        refreshGame()
    }

    function refreshGame() {
        if (!route?.params.id) return;

        http.get('/game/' + route.params.id).then(response => {

            let rack_start = 5
            let exchange_start = 1

            playerTiles.value = []
            exchangeTiles.value = []
            response.data.tray.forEach(letter => {
                playerTiles.value.push({
                    index:  rack_start,
                    letter: letter,
                    row:    rackRow,
                    col:    rack_start++,
                })

                exchangeTiles.value.push({
                    index:  exchange_start,
                    letter: letter,
                    row:    1,
                    col:    exchange_start++,
                })
                exchangeNo.value.push(letter)
            })

            existingTiles.value = []
            response.data.played_tiles.toReversed().forEach((move, index) => {
                let most_recent_play = (index == 0)
                existingTiles.value.push(...move)
                move.forEach(tile => {
                    tile.most_recent_play = (index == 0)
                    tile.existing = true
                })
            })
            curGame.value = response.data
            lastMove.value = curGame.value.moves[0]
            scores.value = response.data.scores
            gameOverMan.value = response.data.game_over
            whoseTurn.value = response.data.whose_turn
            myTurn = response.data.whose_turn == authUsername && !gameOverMan.value
            unseen.value = response.data.unseen
            canExchange = myTurn && Number(unseen.value.bag) >= 7
            showMarker()
        })
        .catch(error => {
            warn(error)
            const msg = (error.data && error.data.detail) || error.statusText;
            throw new Error(msg);
        });

    }

    const showMovesDialog = () => movesDialog.value.show()
    const showGamesDialog = () => gamesDialog.value.show()

    function pass(force) {
        if (!myTurn) return
        if (force) {
            submitPlay('pass')
            closePassDialog()
        } else {
            passDialog.value.show()
        }
    }

    function exchange(data) {
        if (!canExchange) return
        if (data) {
            submitPlay('exchange', data)
        } else {
            exhangeDialog.value.show()
        }
    }

    function play() {
        if (myTurn && validPlay) {
            let data = tilesInPlay().map(tile => {
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
            refreshGameList()
            initializeGame()
            showGamesDialog()
        })
    }

    function acknowledge_game(game_id) {
        http.patch('/game/acknowledge/' + game_id).then(response => {
            refreshGameList()
            showGamesDialog()
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
        tilesInPlay().forEach(letter => rows.add(letter.row));
        return Array.from(rows);
    }

    function playedCols() {
        let cols = new Set();
        tilesInPlay().forEach(letter => cols.add(letter.col));
        return Array.from(cols);
    }

    let controller = null
    function allWordsValid() {
        if (!playedWords.value.length) return false;
        const query_string = playedWords.value.map(word => `words=${word[0]}`).join('&')
        if (controller) {
            controller.abort()
        }
        controller = new AbortController();
        const signal = controller.signal
        http.get(`/word?${query_string}`, { signal }).then(response => {
            invalidWords.value = response.data.invalid
            controller = null
            validPlay = !invalidWords.value.length
        })
    }

    function isValidPlacement() {
        let played = tilesInPlay()
        if (played.length === 0) return false

        // middle square
        let hasMiddle = played.filter(tile => tile.row == middle && tile.col == middle).length > 0

        // all letters in same col or row
        let usedCols = playedCols()
        let usedRows = playedRows()
        let playDir = playDirection()
        let isStraight = (playDir !== "neither")

        if (!isStraight) return false

        // all letters connected
        let connected = true
        if (playDir === "horizontal") {
            let row = usedRows[0]
            let col = Math.min(...usedCols)
            let end = Math.max(...usedCols)
            while (col <= end) {
                let existing = existingTileAt(row, col)
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
                let existing = existingTileAt(row, col)
                if (!usedRows.includes(row) && !existing) {
                    connected = false;
                    break
                }
                row++
            }
        }
        if (isStraight && hasMiddle && connected && played.length > 1) return true
        if (!connected) return false

        // touches at least one played tile
        let isTouching = false
        let blankSet = true
        played.forEach(tile => {
            [[0,1],[1,0],[-1,0],[0,-1]].forEach(dir => {

                if (existingTileAt(tile.row + dir[0], tile.col + dir[1])) {
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

        if (!blankSet) return false

        // fully valid
        if (isTouching && isStraight && !hasMiddle && played.length >= 1) return true

        // unknown
        return false

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
            let tile = direction == 'vertical' ? anyTileAt(col+1, row+1) : anyTileAt(row+1, col+1)
            if (col < 0 || tile == undefined) break;
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
            let tile = direction == 'vertical' ? anyTileAt(col+1,row+1) : anyTileAt(row+1, col+1)
            if (col >= b.length || tile == undefined) break;
            let points = letterPoints[tile.letter]
            points = tile.existing ? points : modifiedLetterValue(points, row+1, col+1)
            score += points
            word += tile.sub || tile.letter

            if (!tile.existing) {
                let cell = b[row][col]
                if (cell.type == 'triple-word') tws++
                if (cell.type == 'double-word') dws++
                if (cell.type == 'center') dws++
            }
            col++
            len++
        }
        if (len < 2) return 0
        score *= 3**tws
        score *= 2**dws
        playedWords.value.push([word, score])
        return score
    }

    function scorePlay() {
        playedWords.value = []
        playScore.value = 0

        if (!isValidPlacement()) {
            validPlay = false
            return 0;
        }

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
        allWordsValid()
        if (tilesInPlay().length === 7) score += 50
        playScore.value = score
    }

    function modifiedLetterValue(val, row, col) {
        switch (board.value[row-1][col-1].type) {
            case "double-letter": val *= 2; break;
            case "triple-letter": val *= 3; break;
        }
        return val
    }

    function openTrayCols() {
        let taken = tilesOnRack().map(tile => tile.col);
        let trayCols = Array.from(new Array(7), (x, i) => i + rackStart);
        return trayCols.filter(index => !taken.includes(index))
    }

    function recallAllTiles() {
        let openCols = openTrayCols()
        playerTiles.value.forEach(tile => recallTile(tile))
        scorePlay()
    }

    function shuffleTray() {
        let rando = [...Array(tilesOnRack().length).keys()].sort(() => Math.random() - 0.5);
        playerTiles.value.forEach(tile => {
            if (tile.row === rackRow) tile.col = rando.pop() + rackStart
        })
    }

    let draggedEl = null
    function dragging(e) {
        let el = e.currentTarget;
        draggedEl = el
        el.classList.add('dragging');

        let row = Number(el.style.gridRow)
        let col = Number(el.style.gridColumn)
    }

    function allowDrop(e) {
        e.preventDefault();
    }

    function swapTiles(e) {
        // two tiles
        let a = playerTiles.value[e.currentTarget.getAttribute("index")];
        let b = playerTiles.value[draggedEl.getAttribute("index")]

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

        let cell = e.target;
        let row = Number(cell.style.gridRow)
        let col = Number(cell.style.gridColumn)
        let tile = tileAt(draggedEl.style.gridRow, draggedEl.style.gridColumn)
        if (tile) placeTile(tile, row, col)
    }

    function placeTile(tile, row, col) {
        tile.col = col
        tile.row = row
        scorePlay()
    }

    function toggleExchange(e) {
        let el = e.currentTarget;
        const row = Number(el.style.gridRow)
        const col = Number(el.style.gridColumn)
        exchangeTiles.value.forEach(tile => {
            if (tile.row === row && tile.col === col) {
                tile.row = tile.row === 1 ? 2 : 1
            }
        })
    }

    function completeExchange() {
        let letters = toExchangeTiles.value.map(tile => tile.letter).join("")
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
        return validPlay ? 'valid' : 'invalid'
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
        scorePlay()
        blanksDialog.value.close()
    }

    function playDirection() {
        if (playedRows().length === 1) return "horizontal"
        if (playedCols().length === 1) return "vertical"
        return "neither"

    }
</script>
