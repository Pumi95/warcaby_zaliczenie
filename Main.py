# Main file #
#############

# Imports
import Board
import Move
import WinCondition
import os


# Defs
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


# Main
board = Board.createBoard()
Board.printBoard(board)

while WinCondition.isGameEnded(board):
    print 'Podaj startowe x:'
    start_x = int(raw_input())
    print 'Podaj startowe y:'
    start_y = int(raw_input())
    print 'Podaj docelowe x:'
    target_x = int(raw_input())
    print 'Podaj docelowe y:'
    target_y = int(raw_input())
    startPos = [start_x, start_y]
    targetPos = [target_x, target_y]
    Move.move(board, startPos, targetPos)
    print '\n'
    print board[startPos[1]][startPos[0]]
    Board.printBoard(board)

if WinCondition.checkWhoWin(board):
    print ' Gracz 1 wygral - gratulacje!'
else:
    print ' Gracz 2 wygral - gratulacje!'

    #ds Strusio chuj dsd
