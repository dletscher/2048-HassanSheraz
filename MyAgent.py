from Game2048 import *

class Player:
    def __init__(self, timeLimit):
        self.timeLimit = timeLimit

    def findMove(self, state):
        moves = state.actions()
        best = None
        bestScore = float('-inf')
        for move in moves:
            nextState, _ = state.result(move)
            score = self.evaluate(nextState)
            if score > bestScore:
                bestScore = score
                best = move
        return best

    def evaluate(self, state):
        board = state._board
        empty = sum(1 for r in range(4) for c in range(4) if board[r][c] == 0)
        smooth = self.smoothness(board)
        monotonic = self.monotonicity(board)
        maxTile = max(max(row) for row in board)
        return empty * 200 + smooth + monotonic + maxTile * 2

    def smoothness(self, board):
        score = 0
        for r in range(4):
            for c in range(3):
                if board[r][c] and board[r][c+1]:
                    score -= abs(board[r][c] - board[r][c+1])
        for r in range(3):
            for c in range(4):
                if board[r][c] and board[r+1][c]:
                    score -= abs(board[r][c] - board[r+1][c])
        return score

    def monotonicity(self, board):
        totals = [0, 0, 0, 0]

        # rows
        for r in range(4):
            for c in range(3):
                if board[r][c] > board[r][c+1]:
                    totals[0] += board[r][c] - board[r][c+1]
                else:
                    totals[1] += board[r][c+1] - board[r][c]

        # cols
        for c in range(4):
            for r in range(3):
                if board[r][c] > board[r+1][c]:
                    totals[2] += board[r][c] - board[r+1][c]
                else:
                    totals[3] += board[r+1][c] - board[r][c]

        return -min(totals[0], totals[1]) - min(totals[2], totals[3])
