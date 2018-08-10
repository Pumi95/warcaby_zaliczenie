#   Tworzenie dwuwymiarowej listy sluzacej za plansze do gry
def createBoard():
    #   Tworzenie pustej listy dwuwymiarowej
    board = [None] * 9
    for i in range(9):
        board[i] = [None] * 9

    #   Tworzenie listy literek oznaczajacych pola na planszy
    letters = [' ', '1', '2', '3', '4', '5', '6', '7', '8']#os pozioma x

    #   Wypelnianie planszy pionkami
    for i in range(9):
        for j in range(9):
            if (i == 1 or i == 3) and j % 2 == 1:
                board[i][j] = 'o'
            elif i == 2 and j % 2 == 0:
                board[i][j] = 'o'
            elif (i == 6 or i == 8) and j % 2 == 0:
                board[i][j] = 'x'
            elif i == 7 and j % 2 == 1:
                board[i][j] = 'x'
            else:
                board[i][j] = '-'

    #   Wypelnianie bokow planszy cyframi i literami identyfikujacymi pole
    for i in range(9):
        board[i][0] = i
    for i in range(9):
        board[0][i] = letters[i]

    #   Zwracanie listy dwuwymiarowej
    return board

#   Wyswietlanie planszy do gry
def printBoard(board):
    msg = ''
    for i in range(9):
        for j in range(9):
            msg += str(board[i][j])
            msg += ' '
        else:
            msg += '\n'

    return msg
