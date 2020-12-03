var board = null;
var $board = $('#myBoard')
var squareClass = 'square-55d63'
var pos = 'start';
var game = new Chess();
var $status = $('#status');
var $fen = $('#fen');
var $pgn = $('#pgn');
var whitePlayer = 'player';
var blackPlayer = 'stockfish';
var variation = '';
var constantVariation = '';
var curIndex = 0;
var tempIndex = 0;
var curTactic = '';

function getTactic() {
    var message = document.getElementById('message');
    if(message != null) {
        document.getElementById('message').remove();
    }
    document.getElementById('start').innerHTML = "Next tactic"
    document.getElementById('start').setAttribute('disabled', 'true');
    message = { "getTactic": true };
    $.ajax({
        type: 'POST',
        url: "/get_tactic",
        data: message,
        success: function (response) {
            displayTactic(response.tactic);
        }
    })
}

function displayTactic(tactic) {
    console.log(tactic);
    game = new Chess(tactic.fen)
    if(tactic.turn) {
        //white to move
        board.orientation('white');
    } else {
        board.orientation('black');
    }
    board.position(game.fen())
    variation = tactic.variation;
    constantVariation = JSON.parse(JSON.stringify(tactic.variation));
    curIndex = -1; // no moves made yet in the variation
    tempIndex = -1; // no moves made yet in the variation
    curTactic = tactic;

    updateStatus();
}

function removeHighlights(color) {
    $board.find('.' + squareClass).removeClass('highlight-' + color)
}


function changeRating(value) {
    message = { "changeRating": value };
    $.ajax({
        type: 'POST',
        url: "/update",
        data: message,
        success: function (response) {
            console.log("Updated rating by " + value);
        }
    })
}

function updateTacticRecords(value) {
    message = { "changeTacticsCorrect": value };
    $.ajax({
        type: 'POST',
        url: "/update",
        data: message,
        success: function (response) {
            console.log("Updated tactic record by " + value);
        }
    })
}

function onDragStart(source, piece, position, orientation) {
    // do not pick up pieces if the game is over
    if (game.game_over()) return false;

    if (curIndex != tempIndex) return false;


    // // only pick up pieces for the side to move
    if ((game.turn() === 'w' && piece.search(/^b/) !== -1) ||
        (game.turn() === 'b' && piece.search(/^w/) !== -1)) {
            return false;
        }
    
    if (game.turn() === 'w' && curTactic.turn) return true;
    if (game.turn() === 'b' && !curTactic.turn) return true;
    
    return false;
}

function begin() {
    removeHighlights('black')
    removeHighlights('white')
    tempIndex = -1;
    while(game.undo()) {
        game.undo()
    }
    updateStatus();
    board.position(game.fen());
    document.getElementById('nextmove').removeAttribute('disabled');
    document.getElementById('end').removeAttribute('disabled');
    $("#lastmove").attr('disabled', 'disabled');
    $("#begin").attr('disabled', 'disabled');
}


function lastmove() {
    console.log("-----------------LAST MOVE--------------------")
    console.log("Start Temp Index " + tempIndex);
    console.log("Start Current Index " + curIndex);

    if(tempIndex > -1) {
        tempIndex--;
        var result = game.undo();
        
        if(result == null) {
            console.log("NO MOVE MADE. --ERROR")
        }

        board.position(game.fen());
        updateStatus();
        document.getElementById('nextmove').removeAttribute('disabled');
        document.getElementById('end').removeAttribute('disabled');
        removeHighlights('black')
        removeHighlights('white')
    }

    if(tempIndex == -1) {
        $("#lastmove").attr('disabled', 'disabled');
        $("#begin").attr('disabled', 'disabled');
    }

    console.log("End Temp Index " + tempIndex);
    console.log("End Current Index " + curIndex);
}

function nextmove() {
    console.log("-----------------NEXT MOVE--------------------")
    console.log("Temp Index " + tempIndex);
    console.log("Current Index " + curIndex);

    if(tempIndex < curIndex) {

        tempIndex++;
        
        var move = game.move({
            from: constantVariation[tempIndex].substr(0, 2),
            to: constantVariation[tempIndex].substr(2, 4),
            promotion: constantVariation[tempIndex].substr(4)
        })

        if(move == null) {
            console.log("NO MOVE MADE. --ERROR")
        }

        board.position(game.fen());
        
        if(game.turn() == 'w') {
            //black just moved
            removeHighlights('black')
            removeHighlights('white')
            $board.find('.square-' + constantVariation[tempIndex].substr(0, 2)).addClass('highlight-black')
            $board.find('.square-' + constantVariation[tempIndex].substr(2, 4)).addClass('highlight-black')
        } else {
            removeHighlights('black')
            removeHighlights('white')
            $board.find('.square-' + constantVariation[tempIndex].substr(0, 2)).addClass('highlight-white')
            $board.find('.square-' + constantVariation[tempIndex].substr(2, 4)).addClass('highlight-white')
        }

        updateStatus();
        document.getElementById('lastmove').removeAttribute('disabled');
        document.getElementById('begin').removeAttribute('disabled');
    }

    if(tempIndex >= curIndex) {
        $("#nextmove").attr('disabled', 'disabled');
        $("#end").attr('disabled', 'disabled');
        tempIndex = curIndex;
    }

    console.log("End Temp Index " + tempIndex);
    console.log("End Current Index " + curIndex);
}

function respond() {
    var move = game.move({
        from: variation[0].substr(0, 2),
        to: variation[0].substr(2, 4),
        promotion: variation[0].substr(4)
    })

    curIndex++;
    tempIndex++;
    
    board.position(game.fen());
    if(game.turn() == 'w') {
        //black just moved
        removeHighlights('black')
        removeHighlights('white')
        $board.find('.square-' + variation[0].substr(0, 2)).addClass('highlight-black')
        $board.find('.square-' + variation[0].substr(2, 4)).addClass('highlight-black')
    }
    else {
        removeHighlights('black')
        removeHighlights('white')
        $board.find('.square-' + variation[0].substr(0, 2)).addClass('highlight-white')
        $board.find('.square-' + variation[0].substr(2, 4)).addClass('highlight-white')
    }
    variation = variation.slice(1, variation.length)
    updateStatus();
}

function onDrop(source, target) {
    // see if the move is legal
    var move = game.move({
        from: source,
        to: target,
        promotion: 'q' // NOTE: always promote to a queen for example simplicity
    })
                
    
    // $board.find('.' + squareClass).removeClass('highlight-white')
    // $board.find('.square-' + move.from).addClass('highlight-white')
    // squareToHighlight = target
    // colorToHighlight = 'white'
    // illegal move
    if (move === null) return 'snapback';

    if(game.turn() == 'w') {
        //black just moved
        removeHighlights('black')
        removeHighlights('white')
        $board.find('.square-' + source).addClass('highlight-black')
        $board.find('.square-' + target).addClass('highlight-black')
    }
    else {
        removeHighlights('black')
        removeHighlights('white')
        $board.find('.square-' + source).addClass('highlight-white')
        $board.find('.square-' + target).addClass('highlight-white')
    }
    
    var message = document.getElementById('message');
    if(message != null) {
        document.getElementById('message').remove();
    }

    curIndex++;
    tempIndex++;

    document.getElementById('begin').removeAttribute('disabled');
    document.getElementById('lastmove').removeAttribute('disabled');

    if( source+target == variation[0] ) {
        //correc
        variation = variation.slice(1, variation.length)
        if(variation.length > 0) {
            var div = document.createElement('div');
            div.setAttribute('role', 'alert');
            div.id = "message";
            div.className = "alert alert-success"
            div.innerHTML = 'Correct move! Keep going...'
            document.getElementById('info').appendChild(div)
            window.setTimeout(respond, 250)
        } else {
            var div = document.createElement('div');
            div.id = "message";
            div.setAttribute('role', 'alert');
            div.className = "alert alert-success"
            div.innerHTML = 'Puzzle Solved!'
            document.getElementById('info').appendChild(div)
            document.getElementById('start').removeAttribute('disabled');
        }
    } else {
        var div = document.createElement('div');
        div.setAttribute('role', 'alert');
        div.id = "message";
        div.className = "alert alert-danger";
        div.innerHTML = 'Incorrect move.';
        document.getElementById('info').appendChild(div);
        document.getElementById('start').removeAttribute('disabled');
        curIndex = constantVariation.length - 1;
    }
    updateStatus();
}

// update the board position after the piece snap
// for castling, en passant, pawn promotion
function onSnapEnd() {
    board.position(game.fen());
}

function updateStatus() {
    var status = '';

    var moveColor = 'White';
    if (game.turn() === 'b') {
        moveColor = 'Black';
    }

    // checkmate?
    if (game.in_checkmate()) {
        status = 'Game over, ' + moveColor + ' is in checkmate.';
        var $switchColors = $('#switch');
        $switchColors.prop("disabled", true);
    }

    // draw?
    else if (game.in_draw()) {
        status = 'Game over, drawn position';
    }

    // game still on
    else {
        
        var $switchColors = $('#switch');
        $switchColors.prop("disabled", false);

        status = moveColor + ' to move';

        // check?
        if (game.in_check()) {
            status += ', ' + moveColor + ' is in check';
        }
    }

    $status.html("<strong>Status: </strong>" + status);
    $fen.html("<strong>FEN: </strong>" + game.fen());
    $pgn.html("<strong>Moves: </strong>" + game.pgn());
}

var config = {
    pieceTheme: 'static/img/chesspieces/' + document.getElementById('piecetype').className,
    draggable: true,
    position: pos,
    onDragStart: onDragStart,
    onDrop: onDrop,
    onSnapEnd: onSnapEnd,
    orientation: 'white'
}
board = Chessboard('myBoard', config);
$(window).resize(board.resize);
updateStatus();