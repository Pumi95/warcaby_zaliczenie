def isGameEnded(board):
    tmp = [False, False]
    reversedRange = [8, 7, 6, 5, 4, 3, 2, 1]
    for i in range(1, 9):
        for j in range(1, 9):
            if board[i][j] == 'o':
                tmp[0] = True

    for i in reversedRange:
        for j in reversedRange:
            if board[i][j] == 'x':
                tmp[1] = True

    if tmp[0] == False or tmp[1] == False:
        return True
    else:
        return False


def checkWhoWin(board):
    for i in range(1, 9):
        for j in range(1, 9):
            if board[i][j] == 'o':
                return True
            elif board[i][j] == 'x':
                return False
