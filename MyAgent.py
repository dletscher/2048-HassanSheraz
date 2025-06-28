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
            # Expectimax lookahead for tile spawn
            score = 0
            empty = [(r, c) for r in range(4) for c in range(4) if nextState._board[r][c] == 0]
            for (r, c) in empty:
                nextState._board[r][c] = 2
                score += 0.9 * self.evaluate(nextState)
                nextState._board[r][c] = 4
                score += 0.1 * self.evaluate(nextState)
                nextState._board[r][c] = 0
            if empty:
                score /= len(empty)
            else:
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
        return empty * 300 + smooth + monotonic + maxTile * 2

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
        for r in range(4):
            for c in range(3):
                if board[r][c] > board[r][c+1]:
                    totals[0] += board[r][c] - board[r][c+1]
                else:
                    totals[1] += board[r][c+1] - board[r][c]
        for c in range(4):
            for r in range(3):
                if board[r][c] > board[r+1][c]:
                    totals[2] += board[r][c] - board[r+1][c]
                else:
                    totals[3] += board[r+1][c] - board[r][c]
        return -min(totals[0], totals[1]) - min(totals[2], totals[3])
