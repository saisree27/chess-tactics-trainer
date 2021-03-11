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
var classifications = '';
var timerVar;
var totalSeconds = 0;
var originalFEN = '';
var promoting = false;
var promotion_piece = null;
var move = '';

$('#update-class-form').submit(function(event) {
    event.preventDefault();
    var $form = $(this)
    var url = $form.attr('action');

    var posting = $.post(url, {
        fen: $('#update-class-fen').val(),
        addclass: $('#addclass').val()
    })

    posting.done(function(response) {
        document.getElementById('update-class-result').innerHTML = response.message;
        if(response.message == "Classifications updated!") {
            classifications = response.new_classifications;
            var classificationString = "";
            classifications.map((x) => {
                classificationString = classificationString.concat("<span class='badge badge-primary'>" + x + "</span> <span> </span>")
                console.log(classificationString)
            })
            console.log(classificationString)
            document.getElementById('classifications').innerHTML = "<strong>Classifications: </strong>" + classificationString + "<span> </span>" + "<span id='addclassification' class='badge badge-primary' style='cursor: pointer;'>+</span>";
            document.getElementById("classifications").style.visibility = "visible"
            var btn = document.getElementById("addclassification");
            btn.onclick = function() {
                modal.style.display = "block";
            }
        }
    });

    posting.fail(function(data) {
        document.getElementById('update-class-result').innerHTML = "Request failed.";
    });

});

$('#remove-class-form').submit(function(event) {
    event.preventDefault();
    var $form = $(this)
    var url = $form.attr('action');

    var posting = $.post(url, {
        fen: $('#remove-class-fen').val(),
        removeclass: $('#removeclass').val()
    })

    posting.done(function(response) {
        document.getElementById('remove-class-result').innerHTML = response.message;
        if(response.message == "Classification removed!") {
            classifications = response.new_classifications;
            var classificationString = "";
            classifications.map((x) => {
                classificationString = classificationString.concat("<span class='badge badge-primary'>" + x + "</span> <span> </span>")
                console.log(classificationString)
            })
            console.log(classificationString)
            document.getElementById('classifications').innerHTML = "<strong>Classifications: </strong>" + classificationString + "<span> </span>" + "<span id='addclassification' class='badge badge-primary' style='cursor: pointer;'>+</span>";
            document.getElementById("classifications").style.visibility = "visible"
            var btn = document.getElementById("addclassification");
            btn.onclick = function() {
                modal.style.display = "block";
            }
        }
    });

    posting.fail(function(data) {
        document.getElementById('update-class-result').innerHTML = "Request failed.";
    });

});

var modal = document.getElementById("myModal");
var promotionModal = document.getElementById("promotion-dialog");

// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close")[0];
var spanPromotion = document.getElementsByClassName("closePromotion")[0];

var promotionQueen = document.getElementById("promoteQueen");
var promotionRook = document.getElementById("promoteRook");
var promotionBishop = document.getElementById("promoteBishop");
var promotionKnight = document.getElementById("promoteKnight");

promotionQueen.onclick = function() {
    promotionModal.style.display = "none";
    promotion_piece = "q";
    move.promotion = promotion_piece;
    moveAndUpdateTactic(move);
}

promotionRook.onclick = function() {
    promotionModal.style.display = "none";
    promotion_piece = "r";
    move.promotion = promotion_piece;
    moveAndUpdateTactic(move);
}

promotionBishop.onclick = function() {
    promotionModal.style.display = "none";
    promotion_piece = "b";
    move.promotion = promotion_piece;
    moveAndUpdateTactic(move);
}

promotionKnight.onclick = function() {
    promotionModal.style.display = "none";
    promotion_piece = "n";
    move.promotion = promotion_piece;
    moveAndUpdateTactic(move);
}
// When the user clicks on <span> (x), close the modal
span.onclick = function() {
modal.style.display = "none";
}

spanPromotion.onclick = function() {
    promotionModal.style.display = "none";
    promoting = false;
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
} 

function getTactic() {
    var message = document.getElementById('message');
    if(message != null) {
        document.getElementById('message').remove();
    }

    document.getElementById("start").classList.remove('btn-outline-success');
    document.getElementById("start").classList.remove('btn-outline-danger');
    document.getElementById("start").classList.add('btn-outline-primary');

    document.getElementById('start').innerHTML = "Find the best move"
    document.getElementById('start').setAttribute('disabled', 'true');

    $("#begin").attr('disabled', 'disabled');
    $("#lastmove").attr('disabled', 'disabled');
    $("#nextmove").attr('disabled', 'disabled');
    $("#end").attr('disabled', 'disabled');
    
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
    // game = new Chess('1nbqkbnr/Ppppp1pp/8/8/8/8/1PPPPPPP/RNBQKBNR w KQk - 0 1')
    if(tactic.turn) {
        //white to move
        board.orientation('white');
    } else {
        board.orientation('black');
    }
    $("#analysis_board").attr('src', '');
    board.position(game.fen());
    originalFEN = game.fen();
    variation = tactic.variation;
    constantVariation = JSON.parse(JSON.stringify(tactic.variation));
    classifications = tactic.classifications;
    document.getElementById("classifications").style.visibility = "hidden"
    document.getElementById("update-class-fen").value = game.fen();
    document.getElementById("remove-class-fen").value = game.fen();
    curIndex = -1; // no moves made yet in the variation
    tempIndex = -1; // no moves made yet in the variation
    curTactic = tactic;

    updateStatus();
    totalSeconds = 0;
    timerVar = setInterval(countTimer, 1000);
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

function countTimer() {
    ++totalSeconds;
    var hour = Math.floor(totalSeconds /3600);
    var minute = Math.floor((totalSeconds - hour*3600)/60);
    var seconds = totalSeconds - (hour*3600 + minute*60);
    if(hour < 10)
      hour = "0"+hour;
    if(minute < 10)
      minute = "0"+minute;
    if(seconds < 10)
      seconds = "0"+seconds;
    document.getElementById("timer").innerHTML = "<strong>Time Spent: </strong>" + hour + ":" + minute + ":" + seconds;
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

function end() {
    removeHighlights('black');
    removeHighlights('white');

    while(tempIndex != curIndex) {
        nextmove();
    }

    updateStatus();
    board.position(game.fen());
    document.getElementById('nextmove').removeAttribute('disabled');
    document.getElementById('end').removeAttribute('disabled');
    $("#nextmove").attr('disabled', 'disabled');
    $("#end").attr('disabled', 'disabled');
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

function getImgSrc(piece) {
    var piecetype = 'static/img/chesspieces' + document.getElementById('piecetype').className;
    return piecetype.replace('{piece}', game.turn() + piece.toLocaleUpperCase());
}


var onDialogClose = function() {
    // console.log(promote_to);
    move.promotion = promote_to;
    console.log(move);
    moveAndUpdateTactic(move);
}

function moveAndUpdateTactic(move) {
    console.log(move);
    var result = game.move(move);
    var source = move.from;
    var target = move.to;

    console.log(source + target);
    // $board.find('.' + squareClass).removeClass('highlight-white')
    // $board.find('.square-' + move.from).addClass('highlight-white')
    // squareToHighlight = target
    // colorToHighlight = 'white'
    // illegal move
    if (result === null) return 'snapback';

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
    
    if(promoting) board.position(game.fen());

    var message = document.getElementById('message');
    if(message != null) {
        document.getElementById('message').remove();
    }

    updateStatus();

    curIndex++;
    tempIndex++;

    document.getElementById('begin').removeAttribute('disabled');
    document.getElementById('lastmove').removeAttribute('disabled');

    if( source+target == variation[0] ) {
        //correc
        variation = variation.slice(1, variation.length)
        if(variation.length > 0) {
            document.getElementById('start').innerHTML = "Correct! Keep going!";
            document.getElementById("start").classList.remove('btn-outline-primary');
            document.getElementById("start").classList.add('btn-outline-success');
            window.setTimeout(respond, 250)
        } else {
            document.getElementById('start').innerHTML = "Puzzle Solved! <strong>|</strong> Continue Solving";
            document.getElementById("start").classList.remove('btn-outline-primary');
            document.getElementById("start").classList.add('btn-outline-success');
            document.getElementById('start').removeAttribute('disabled');
            $("#analysis_board").attr('src', 'https://lichess.org/analysis/standard/' + originalFEN);
            console.log("Classifications");
            console.log(classifications);
            var classificationString = "";
            classifications.map((x) => {
                classificationString = classificationString.concat("<span class='badge badge-primary'>" + x + "</span> <span> </span>")
                console.log(classificationString)
            })
            console.log(classificationString)
            document.getElementById('classifications').innerHTML = "<strong>Classifications: </strong>" + classificationString + "<span> </span>" + "<span id='addclassification' class='badge badge-primary' style='cursor: pointer;'>+</span>";
            document.getElementById("classifications").style.visibility = "visible"
            var btn = document.getElementById("addclassification");
            btn.onclick = function() {
                modal.style.display = "block";
            }
            clearInterval(timerVar);
        }
    } else {
        document.getElementById("start").classList.remove('btn-outline-primary');
        document.getElementById("start").classList.add('btn-outline-success');
        document.getElementById("start").classList.add('btn-outline-danger');
        document.getElementById('start').innerHTML = "Incorrect move. <strong>|</strong> Continue Solving"
        document.getElementById('start').removeAttribute('disabled');
        $("#analysis_board").attr('src', 'https://lichess.org/analysis/standard/' + originalFEN);
        curIndex = constantVariation.length - 1;
        var classificationString = "";
        classifications.map((x) => {
            classificationString = classificationString.concat("<span class='badge badge-primary'>" + x + "</span> <span> </span>")
            console.log(classificationString)
        })
        console.log(classificationString)
        document.getElementById('classifications').innerHTML = "<strong>Classifications: </strong>" + classificationString + "<span> </span>" + "<span id='addclassification' class='badge badge-primary button'  style='cursor: pointer;'>+</span>";
        document.getElementById("classifications").style.visibility = "visible"
        var btn = document.getElementById("addclassification");
        btn.onclick = function() {
            modal.style.display = "block";
        }
        clearInterval(timerVar);
    }
    
}


function onDrop(source, target) {
    // see if the move is legal
    move = {
        from: source,
        to: target,
        promotion: 'q'
    }

    var result = game.move(move);

    if(result === null) return 'snapback';
    else game.undo();
                
    var source_rank = source.substring(2,1);
    var target_rank = target.substring(2,1);
    var piece = game.get(source).type;

    if (piece === 'p' && ((source_rank === '7' && target_rank === '8') || (source_rank === '2' && target_rank === '1'))) {
         promoting = true;

        // // get piece images
        $('.promotion-piece-q').attr('src', getImgSrc('q'));
        $('.promotion-piece-r').attr('src', getImgSrc('r'));
        $('.promotion-piece-n').attr('src', getImgSrc('n'));
        $('.promotion-piece-b').attr('src', getImgSrc('b'));

        promotionModal.style.display = "block";
        //the actual move is made after the piece to promote to
        //has been selected, in the stop event of the promotion piece selectable
        return;
    }
    moveAndUpdateTactic(move);
}

// update the board position after the piece snap
// for castling, en passant, pawn promotion
function onSnapEnd() {
    board.position(game.fen());
}

function updateStatus() {
    promoting = false;
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
    $pgn.html("<strong>Moves: </strong>" + game.pgn().substr(game.pgn().lastIndexOf(']') + 1));
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
