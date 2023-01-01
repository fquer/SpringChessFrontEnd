from flask import Flask, render_template, request, Response, redirect
from time import sleep
import requests
import json

app = Flask(__name__, template_folder = 'templates')

def stream_template(template_name, **context):
    app.update_template_context(context)
    t = app.jinja_env.get_template(template_name)
    rv = t.stream(context)
    rv.disable_buffering()
    return rv

def generate(url, options):
    temp = ""
    while True:
        x = requests.post(url, json = options)
        if type(temp) == str:
            temp = x
            yield x.text
            req = json.loads(x.text)
            if (req['board']['winner'] != 'Empty'):
                break
        else:
            if temp.text != x.text:
                temp = x
                yield x.text
                req = json.loads(x.text)
                if (req['board']['winner'] != 'Empty'):
                    break
        sleep(1)

@app.route('/lobby')
def home():
    req = requests.post('http://localhost:8080/game/checkLogin', json = {})
    jreq = json.loads(req.text)

    if (jreq['player1'] == None and jreq['player2'] == None):
        gameStat = '0'
    elif jreq['player1'] != None and jreq['player2'] != None:
        gameStat = '2'
        return render_template('lobby.html', gameStatus = gameStat, player1 = jreq['player1']['login'], player2 = jreq['player2']['login'])
    else:
        gameStat = '1'

    return render_template('lobby.html', gameStatus = gameStat)

@app.route('/startGame')
def startGame():
    player = request.args.get('player')
    color = request.args.get('color')

    print(color)
    print(player)

    options = {
        'login' : player,
        'color' : color
    }

    req = requests.post('http://localhost:8080/game/start', json = options)
    if 'Error' in req.text:
        return redirect('/')
    else:
        return redirect('/stream?player={}&color={}'.format(player, color))

@app.route('/connectToGame')
def connectToGame():
    player = request.args.get('player')
    color = request.args.get('color')

    print(color)
    print(player)

    options = {
        "player" : {
            'login' : player,
            'color' : color
        }
        
    }
    url = 'http://localhost:8080/game/connect'

    req = requests.post(url, json = options)
    if 'Error' in req.text:
        return redirect('/')
    else:
        return redirect('/stream?player={}&color={}'.format(player, color))

storedWhite = ""
storedBlack = ""

@app.route('/stream')
def stream_view():
    global storedWhite
    global storedBlack
    print(storedWhite)
    print(storedBlack)
    player = request.args.get('player')
    color = request.args.get('color')
    options= {
        "player" : {
            "login": player
        }
    }
    url = 'http://localhost:8080/game/gamestatus'
    if color == 'White':
        print('byz')
        storedWhite = generate(url, options)
        return Response(stream_template('game.html', rows = storedWhite, player = player, color = color))
    elif color == 'Black':
        print('syh')
        storedBlack = generate(url, options)
        return Response(stream_template('game.html', rows = storedBlack, player = player, color = color))


@app.route('/gameplay')
def gameplay():
    player = request.args.get('player')
    color = request.args.get('color')
    moveToCoordinate = request.args.get('moveToCoordinate')

    options = {
        "player": {
            "login": player,
            "color": color
        },
        "moveToCoordinate": moveToCoordinate
    }
    url = 'http://localhost:8080/game/gameplay'

    requests.post(url, json = options)
    return redirect('/stream?player={}&color={}'.format(player, color))

@app.route('/checkMoveableArea')
def checkMoveableArea():
    player = request.args.get('player')
    color = request.args.get('color')
    selectedCoordinate = request.args.get('selectedCoordinate')

    options = {
        "player": {
            "login": player,
            "color": color
        },
        "selectedCoordinate": selectedCoordinate,
    }

    url = 'http://localhost:8080/game/checkMoveableArea'

    requests.post(url, json = options)
    return redirect('/stream?player={}&color={}'.format(player, color))

@app.route('/cancelSelectedCoordinate')
def cancelSelectedCoordinate():
    player = request.args.get('player')
    color = request.args.get('color')
    selectedCoordinate = request.args.get('selectedCoordinate')

    options = {
        "player": {
            "login": player
        },
        "selectedCoordinate": selectedCoordinate,
    }

    url = 'http://localhost:8080/game/cancelSelectedCoordinate'
    
    requests.post(url, json = options)
    return redirect('/stream?player={}&color={}'.format(player, color))

@app.route('/history')
def history():
    req = requests.get('http://localhost:8080/gameHistory/getMatches')
    jreq = json.loads(req.text)

    print(jreq)
    return render_template('history.html', games = jreq)

@app.route('/viewGame')
def viewGame():
    gameStatus = ''
    winner = ''
    gameId = request.args.get('gameId')
    moveOrder = request.args.get('moveOrder')
    options = {
        "gameId": gameId,
        "moveOrder": moveOrder
    }
    req = requests.post('http://localhost:8080/gameHistory/getMatchPlayHistory', json = options)
    jreq = json.loads(req.text)

    if 'error' in req.text:
        moveOrder = str(int(moveOrder) - 1)
        options = {
            "gameId": gameId,
            "moveOrder": moveOrder
        }
        req = requests.post('http://localhost:8080/gameHistory/getMatchPlayHistory', json = options)
        jreq = json.loads(req.text)
        gameStatus = 'Game ended.'

    return render_template('gameViewer.html', moveOrder = moveOrder, board = jreq['board']['map'], player1 = jreq['player1']['login'], player2 = jreq['player2']['login'], gameId = gameId, gameStatus = gameStatus, winner = winner)

@app.route('/mainpage')
def mainpage():
    return render_template('mainpage.html')

if __name__ == '__main__':
    app.debug = True
    app.run()