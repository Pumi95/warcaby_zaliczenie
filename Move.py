import Rules

def checkPosition(board, position):
    if board[position[1]][position[0]] == 'x' or board[position[1]][position[0]] == 'o':
        return True
    else:
        return False

def returnCheck(board, position):
    if board[position[1]][position[0]] == 'x' or board[position[1]][position[0]] == 'o':
        return board[position[1]][position[0]]
    else:
        return False

def checkTargetPosition(board, position):
    if board[position[1]][position[0]] == '-':
        return True
    else:
        return False

def move(board, start_position, target_position):
    if checkPosition(board, start_position) == False:
        return 'To nie jest pionek'
    elif checkTargetPosition(board, target_position) == False:
        return 'Nie mozesz przeniesc tutaj pionka'
    elif Rules.isCorrectMove(board, start_position, target_position) == '0':
        return 'Nie mozesz przeniesc tutaj pionka!'
    elif Rules.isCorrectMove(board, start_position, target_position) == '1':
        board[target_position[1]][target_position[0]] = board[start_position[1]][start_position[0]]
        board[start_position[1]][start_position[0]] = '-'
        return 'Ruch wykonany!'
    #elif Rules.isCorrectMove(board, start_position, target_position) == '2':
    else:
        board[target_position[1]][target_position[0]] = board[start_position[1]][start_position[0]]
        board[(start_position[1] + target_position[1]) / 2][(start_position[0] + target_position[0]) / 2] = '-'
        board[start_position[1]][start_position[0]] = '-'
        return 'Ruch wykonany!'

