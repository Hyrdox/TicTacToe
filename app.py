from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'supersecretkey'
db = SQLAlchemy(app)


# Model bazy danych
class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(50), unique=True, nullable=False)
    wins = db.Column(db.Integer, default=0)


# Inicjalizacja bazy danych
with app.app_context():
    db.create_all()


# Funkcja sprawdzająca, czy ktoś wygrał
def check_winner(board):
    winning_combinations = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # wiersze
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # kolumny
        [0, 4, 8], [2, 4, 6]  # przekątne
    ]
    for combo in winning_combinations:
        if board[combo[0]] == board[combo[1]] == board[combo[2]] != '':
            return board[combo[0]]
    return None


# # Ruch komputera (losowy)
# def computer_move(board):
#     empty_spots = [i for i, x in enumerate(board) if x == '']
#     if empty_spots:
#         return random.choice(empty_spots)
#     return None


# KOD KOMPUTERA MISTRZA
def minimax(board, depth, is_maximizing):
    # Sprawdzenie wyniku bieżącego stanu gry
    winner = check_winner(board)
    if winner == 'O':  # Komputer wygrywa
        return 10 - depth
    elif winner == 'X':  # Gracz wygrywa
        return depth - 10
    elif '' not in board:  # Remis
        return 0

    if is_maximizing:
        best_score = float('-inf')
        for i in range(9):
            if board[i] == '':
                board[i] = 'O'
                score = minimax(board, depth + 1, False)
                board[i] = ''
                best_score = max(score, best_score)
        return best_score
    else:
        best_score = float('inf')
        for i in range(9):
            if board[i] == '':
                board[i] = 'X'
                score = minimax(board, depth + 1, True)
                board[i] = ''
                best_score = min(score, best_score)
        return best_score


def computer_move(board):
    best_score = float('-inf')
    best_move = None
    for i in range(9):
        if board[i] == '':
            board[i] = 'O'
            score = minimax(board, 0, False)
            board[i] = ''
            if score > best_score:
                best_score = score
                best_move = i
    return best_move
# # # # # #


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        nickname = request.form['nickname']
        session['nickname'] = nickname
        player = Player.query.filter_by(nickname=nickname).first()
        if not player:
            player = Player(nickname=nickname)
            db.session.add(player)
            db.session.commit()
        return redirect(url_for('game'))

    players = Player.query.order_by(Player.wins.desc()).all()
    return render_template('index.html', players=players)


@app.route('/game', methods=['GET', 'POST'])
def game():
    if 'nickname' not in session:
        return redirect(url_for('index'))

    board = [''] * 9
    winner = None
    draw = False  # Zmienna do obsługi remisu

    if request.method == 'POST':
        board = request.form.getlist('board')
        move = int(request.form['move'])
        if board[move] == '':
            board[move] = 'X'  # ruch gracza
            winner = check_winner(board)
            if not winner:
                comp_move = computer_move(board)
                if comp_move is not None:
                    board[comp_move] = 'O'
                    winner = check_winner(board)

            # Sprawdzenie, czy nastąpił remis (brak pustych miejsc i brak zwycięzcy)
            if not winner and '' not in board:
                draw = True

        if winner == 'X':
            player = Player.query.filter_by(nickname=session['nickname']).first()
            player.wins += 1
            db.session.commit()

    return render_template('game.html', board=board, winner=winner, draw=draw)


@app.route('/logout')
def logout():
    session.pop('nickname', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
