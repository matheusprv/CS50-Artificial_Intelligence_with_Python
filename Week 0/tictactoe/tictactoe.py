"""
Tic Tac Toe Player
"""

import math
from copy import deepcopy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    number_of_Xs = 0
    number_of_Os = 0

    for row in board:
        for column in row:
            if column == X:
                number_of_Xs += 1
            elif column == O:
                number_of_Os += 1

    if number_of_Xs == number_of_Os:
        return X
    else:
        return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    actions = set()
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                actions.add((i, j))
    return actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    i, j = action
    if not (0 <= i < 3 and 0 <= j < 3):
        raise ValueError("Action is out of bounds.")
    if board[i][j] is not EMPTY:
        raise ValueError("Cell is already occupied.")
        
    copy_board = deepcopy(board)
    copy_board[i][j] = player(board)
    return copy_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    main_diagonal = {X: 0, O: 0, None: 0}
    opposite_diagonal = {X: 0, O: 0, None: 0}
    for i in range(3):
        row = {X: 0, O: 0, None: 0}
        column = {X: 0, O: 0, None: 0}

        # Iterate through each row and column
        for j in range(3):
            row[board[i][j]] += 1
            column[board[j][i]] += 1

        if row[X] == 3 or column[X] == 3:
            return X
        elif row[O] == 3 or column[O] == 3:
            return O        
        
        main_diagonal[board[i][i]] += 1 
        opposite_diagonal[board[i][-1-i]] += 1
    
    if main_diagonal[X] == 3 or opposite_diagonal[X] == 3:
        return X 
    elif main_diagonal[O] == 3 or opposite_diagonal[O] == 3:
        return O
    else: 
        return None


def board_completed(board):
    # Check if tehre is any EMPTY cell
    for row in board:
        for cell in row:
            if cell is EMPTY:
                return False
    return True 


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    return winner(board) is not None or board_completed(board)


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    winner_player = winner(board)
    if winner_player == X:
        return 1
    elif winner_player == O:
        return -1
    else: 
        return 0


def min_value(board):
    optimal_action = None
    if terminal(board):
        return utility(board), optimal_action
    v = math.inf
    for action in actions(board):
        max_v, _ = max_value(result(board, action))
        if max_v < v:
            v = max_v
            optimal_action = action 

    return v, optimal_action


def max_value(board):
    optimal_action = None
    if terminal(board):
        return utility(board), optimal_action
    v = -math.inf
    for action in actions(board):
        min_v, _ = min_value(result(board, action))
        if min_v > v:
            v = min_v
            optimal_action = action
        
    return v, optimal_action


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None
    if player(board) == X:
        return max_value(board)[1]
    else:
        return min_value(board)[1]
