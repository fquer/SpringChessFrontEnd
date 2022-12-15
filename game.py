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
        else:
            if temp.text != x.text:
                temp = x
                yield x.text
        sleep(1)

@app.route('/')
def home():
    req = requests.post('http://localhost:8080/game/checkLogin', json = {})
    jreq = json.loads(req.text)

    if (jreq['player1'] == None and jreq['player2'] == None):
        gameStat = '0'
    elif jreq['player1'] != None and jreq['player2'] != None:
        gameStat = '2'
        return render_template('home.html', gameStatus = gameStat, player1 = jreq['player1']['login'], player2 = jreq['player2']['login'])
    else:
        gameStat = '1'

    return render_template('home.html', gameStatus = gameStat)

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

@app.route('/stream')
def stream_view():
    player = request.args.get('player')
    color = request.args.get('color')
    options= {
        "player" : {
            "login": player
        }
    }
    url = 'http://localhost:8080/game/gamestatus'
    rows = generate(url, options)
    return Response(stream_template('game.html', rows = rows, player = player, color = color))


@app.route('/gameplay')
def gameplay():
    player = request.args.get('player')
    color = request.args.get('color')
    moveToCoordinate = request.args.get('moveToCoordinate')

    options = {
        "player": {
            "login": player
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
            "login": player
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

if __name__ == '__main__':
    app.debug = True
    app.run()