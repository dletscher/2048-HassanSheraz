import random
import time

class Player:
    def __init__(self, timeLimit):
        self.maxDepth = 4
        self.timeLimit = timeLimit
        self._move = None

    def findMove(self, state):
        legalMoves = list(state.actions())
        if not legalMoves:
            self._move = None
            return

        bestMove = None
        bestScore = -float('inf')

        moveScores = []
        for move in legalMoves:
            child, _ = state.result(move)
            score = self.evaluate(child)
            moveScores.append((score, move))

        moveScores.sort(reverse=True)

        for score, move in moveScores:
            child, _ = state.result(move)
            score = self.minValue(child, self.maxDepth - 1, -float('inf'), float('inf'))
            if score > bestScore:
                bestScore = score
                bestMove = move

        if bestMove not in legalMoves:
            bestMove = legalMoves[0]

        self._move = bestMove

    def getMove(self):
        return self._move

    def maxValue(self, state, depth, alpha, beta):
        if depth == 0 or state.gameOver():
            return self.evaluate(state)

        value = -float('inf')
        legalMoves = list(state.actions())
        if not legalMoves:
            return self.evaluate(state)

        moveScores = []
        for move in legalMoves:
            child, _ = state.result(move)
            score = self.evaluate(child)
            moveScores.append((score, move))
        moveScores.sort(reverse=True)

        for score, move in moveScores:
            child, _ = state.result(move)
            value = max(value, self.minValue(child, depth - 1, alpha, beta))
            if value >= beta:
                return value
            alpha = max(alpha, value)

        return value

    def minValue(self, state, depth, alpha, beta):
        if depth == 0 or state.gameOver():
            return self.evaluate(state)

        value = float('inf')
        legalMoves = list(state.actions())
        if not legalMoves:
            return self.evaluate(state)

        for move in legalMoves:
            child, _ = state.result(move)
            value = min(value, self.maxValue(child, depth - 1, alpha, beta))
            if value <= alpha:
                return value
            beta = min(beta, value)

        return value

    def evaluate(self, state):
        grid = []
        for r in range(4):
            grid.append([state.getTile(r, c) for c in range(4)])

        empty = sum([row.count(0) for row in grid])
        maxTile = max([max(row) for row in grid])

        smoothness = 0
        for row in grid:
            for i in range(len(row) - 1):
                smoothness -= abs(row[i] - row[i + 1])
        for c in range(4):
            for r in range(3):
                smoothness -= abs(grid[r][c] - grid[r + 1][c])

        monoRows = 0
        for row in grid:
            for i in range(len(row) - 1):
                if row[i] >= row[i + 1]:
                    monoRows += 1

        corners = [grid[0][0], grid[0][3], grid[3][0], grid[3][3]]
        cornerBonus = maxTile if maxTile in corners else 0

        score = (
            maxTile * 1.0 +
            empty * 300 +
            smoothness +
            monoRows * 50 +
            cornerBonus * 3
        )

        return score
