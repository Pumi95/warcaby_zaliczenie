def checkPiece(board, pos):
    if board[pos[1]][pos[0]] == 'x':
        return 'x'
    elif board[pos[1]][pos[0]] == 'o':
        return 'o'
    else:
        return '-'


#Sprawdza czy na te pole mozna wejsc
def checkCrossMove(target_pos):
    if (target_pos[1] % 2 == 0 and target_pos[0] % 2 == 1) or (target_pos[1] % 2 == 1 and target_pos[0] % 2 == 0):
        return True
    else:
        return False


#Sprawdza rodzaj ruchu
def checkMoveType(board, start_pos, target_pos):
    if (start_pos[1] - 1 == target_pos[1]) or (start_pos[1] + 1 == target_pos[1]):
        if (start_pos[0] - 1 == target_pos[0]) or (start_pos[0] + 1 == target_pos[0]):
            if checkPiece(board, start_pos) == 'x':
                return 'move'
            elif checkPiece(board, start_pos) == 'o':
                return 'move'
    elif (start_pos[1] - 2 == target_pos[1]) or (start_pos[1] + 2 == target_pos[1]):
        if (start_pos[0] - 2 == target_pos[0]) or (start_pos[0] + 2 == target_pos[0]):
            if (checkPiece(board, start_pos) == 'x') and (board[(start_pos[1] + target_pos[1]) / 2][(start_pos[0] + target_pos[0]) / 2] == 'o'):
                return 'attack'
            elif (checkPiece(board, start_pos) == 'o') and (board[(start_pos[1] + target_pos[1]) / 2][(start_pos[0] + target_pos[0]) / 2] == 'x'):
                return 'attack'
    else:
        return '0'


def isCorrectMove(board, start_pos, target_pos):
    if checkCrossMove(target_pos):
        return '0'
    if checkMoveType(board, start_pos, target_pos) == 'move':
        return '1'
    elif checkMoveType(board, start_pos, target_pos) == 'attack':
        return '2'
    else:
        return '0'

#       board[y][x]
#       field[x][y]