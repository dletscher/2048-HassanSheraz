import random
import math

class Player:
    def __init__(self, timeLimit):
        self.timeLimit = timeLimit
        self.maxDepth = 3
        self._move = None

        self.weights = [
            [4, 3, 2, 1],
            [3, 2, 1, 0],
            [2, 1, 0, -1],
            [1, 0, -1, -2],
        ]

    def findMove(self, state):
        legalMoves = []
        for move in state.actions():
            child, _ = state.result(move)
            if child._board != state._board:
                legalMoves.append(move)

        if not legalMoves:
            self._move = None
            return

        bestMove = None
        bestScore = -math.inf

        for move in legalMoves:
            child, _ = state.result(move)
            score = self.minimax(child, self.maxDepth - 1, -math.inf, math.inf, False)
            if score > bestScore:
                bestScore = score
                bestMove = move

        self._move = bestMove

    def minimax(self, state, depth, alpha, beta, isMax):
        if depth == 0 or state.gameOver():
            return self.evaluate(state)

        if isMax:
            maxEval = -math.inf
            for move in state.actions():
                child, _ = state.result(move)
                if child._board != state._board:
                    eval = self.minimax(child, depth - 1, alpha, beta, False)
                    maxEval = max(maxEval, eval)
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break
            return maxEval
        else:
            minEval = math.inf
            empty = [i for i, x in enumerate(state._board) if x == 0]
            if not empty:
                return self.evaluate(state)
            for pos in empty:
                for val, prob in [(1, 0.9), (2, 0.1)]:
                    newState = state.clone()
                    r, c = divmod(pos, 4)
                    newState.insertTile((r, c), val)
                    eval = self.minimax(newState, depth - 1, alpha, beta, True)
                    minEval = min(minEval, eval)
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break
            return minEval

    def evaluate(self, state):
        empty = sum(1 for x in state._board if x == 0)
        grid = [[state.getTile(r, c) for c in range(4)] for r in range(4)]

        positional = 0
        for r in range(4):
            for c in range(4):
                val = state.getTile(r, c)
                if val > 0:
                    positional += (2 ** val) * self.weights[r][c]

        return state._score + positional + empty * 50

    def getMove(self):
        return self._move


'''
OLDER VERSION SOME BETTER IMPROVEMENTS
import random

class Player:
    def __init__(self, timeLimit):
        self.timeLimit = timeLimit
        self._move = None
        self.maxBaseDepth = 4
        self.cache = {}

    def findMove(self, state):
        empty = sum(1 for r in range(4) for c in range(4) if state.getTile(r, c) == 0)
        if empty >= 6:
            self.maxDepth = self.maxBaseDepth
        elif empty >= 3:
            self.maxDepth = self.maxBaseDepth - 1
        else:
            self.maxDepth = self.maxBaseDepth - 2

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

        for _, move in moveScores:
            child, _ = state.result(move)
            score = self.minValue(child, self.maxDepth - 1, -float('inf'), float('inf'))
            if score > bestScore:
                bestScore = score
                bestMove = move

        self._move = bestMove if bestMove else legalMoves[0]

    def getMove(self):
        return self._move

    def maxValue(self, state, depth, alpha, beta):
        key = self.hash(state)
        if key in self.cache and self.cache[key][1] >= depth:
            return self.cache[key][0]

        if depth == 0 or state.gameOver():
            v = self.evaluate(state)
            self.cache[key] = (v, depth)
            return v

        value = -float('inf')
        legalMoves = list(state.actions())
        if not legalMoves:
            v = self.evaluate(state)
            self.cache[key] = (v, depth)
            return v

        moveScores = []
        for move in legalMoves:
            child, _ = state.result(move)
            score = self.evaluate(child)
            moveScores.append((score, move))
        moveScores.sort(reverse=True)

        for _, move in moveScores:
            child, _ = state.result(move)
            value = max(value, self.minValue(child, depth - 1, alpha, beta))
            if value >= beta:
                self.cache[key] = (value, depth)
                return value
            alpha = max(alpha, value)

        self.cache[key] = (value, depth)
        return value

    def minValue(self, state, depth, alpha, beta):
        key = self.hash(state)
        if key in self.cache and self.cache[key][1] >= depth:
            return self.cache[key][0]

        if depth == 0 or state.gameOver():
            v = self.evaluate(state)
            self.cache[key] = (v, depth)
            return v

        value = float('inf')
        legalMoves = list(state.actions())
        if not legalMoves:
            v = self.evaluate(state)
            self.cache[key] = (v, depth)
            return v

        for move in legalMoves:
            child, _ = state.result(move)
            value = min(value, self.maxValue(child, depth - 1, alpha, beta))
            if value <= alpha:
                self.cache[key] = (value, depth)
                return value
            beta = min(beta, value)

        self.cache[key] = (value, depth)
        return value

    def evaluate(self, state):
        grid = []
        for r in range(4):
            grid.append([state.getTile(r, c) for c in range(4)])

        empty = sum(row.count(0) for row in grid)
        maxTile = max(max(row) for row in grid)

        smoothness = 0
        for row in grid:
            for i in range(3):
                smoothness -= abs(row[i] - row[i + 1])
        for c in range(4):
            for r in range(3):
                smoothness -= abs(grid[r][c] - grid[r + 1][c])

        mono = 0
        for row in grid:
            for i in range(3):
                if row[i] >= row[i + 1]:
                    mono += 1

        snakeMask = [
            [15, 14, 13, 12],
            [8, 9, 10, 11],
            [7, 6, 5, 4],
            [0, 1, 2, 3]
        ]
        gradient = sum(grid[r][c] * snakeMask[r][c] for r in range(4) for c in range(4))

        return (
            maxTile * 1.0 +
            empty * 600 +
            smoothness +
            mono * 120 +
            gradient * 10
        )

    def hash(self, state):
        return tuple(state.getTile(r, c) for r in range(4) for c in range(4))




Lates and best version but it crashing online while best score 50,000 offline

import random
import math

class Player:
    def __init__(self, timeLimit):
        self.timeLimit = timeLimit
        self.maxDepth = 3
        self._move = None

        self.weights = [
            [4, 3, 2, 1],
            [3, 2, 1, 0],
            [2, 1, 0, -1],
            [1, 0, -1, -2],
        ]

    def findMove(self, state):
        legalMoves = []
        for move in state.actions():
            child, _ = state.result(move)
            if child._board != state._board:
                legalMoves.append(move)

        if not legalMoves:
            self._move = None
            return

        bestMove = None
        bestScore = -math.inf

        for move in legalMoves:
            child, _ = state.result(move)
            score = self.expectimax(child, self.maxDepth - 1, False)
            if score > bestScore:
                bestScore = score
                bestMove = move

        self._move = bestMove

    def expectimax(self, state, depth, isMax):
        if depth == 0 or state.gameOver():
            return self.evaluate(state)

        if isMax:
            best = -math.inf
            for move in state.actions():
                child, _ = state.result(move)
                if child._board != state._board:
                    score = self.expectimax(child, depth - 1, False)
                    best = max(best, score)
            return best
        else:
            empty = [i for i, x in enumerate(state._board) if x == 0]
            if not empty:
                return self.evaluate(state)
            total = 0
            for pos in empty:
                for val, prob in [(1, 0.9), (2, 0.1)]:
                    newState = state.clone()
                    r, c = divmod(pos, 4)
                    newState.insertTile((r, c), val)
                    total += prob * self.expectimax(newState, depth - 1, True)
            return total / len(empty)

    def evaluate(self, state):
        empty = sum(1 for x in state._board if x == 0)
        score = state._score + empty * 10

        positional = 0
        for r in range(4):
            for c in range(4):
                val = state.getTile(r, c)
                if val > 0:
                    positional += (2 ** val) * self.weights[r][c]

        return score + positional

    def getMove(self):
        return self._move



OLDER ONE/START



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

        empty = sum(row.count(0) for row in grid)
        maxTile = max(max(row) for row in grid)

        smoothness = 0
        for row in grid:
            for i in range(3):
                smoothness -= abs(row[i] - row[i + 1])
        for c in range(4):
            for r in range(3):
                smoothness -= abs(grid[r][c] - grid[r + 1][c])

        mono = 0
        for row in grid:
            for i in range(3):
                if row[i] >= row[i + 1]:
                    mono += 1

        cornerBonus = 0
        if grid[0][0] == maxTile:
            cornerBonus = maxTile * 1.5
        elif grid[0][3] == maxTile or grid[3][0] == maxTile or grid[3][3] == maxTile:
            cornerBonus = maxTile * 0.5

        gradientMask = [
            [20, 10, 5, 1],
            [10, 5, 2, 1],
            [5, 2, 1, 0],
            [1, 1, 0, 0]
        ]
        gradient = sum(grid[r][c] * gradientMask[r][c] for r in range(4) for c in range(4))

        isolatedPenalty = 0
        for r in range(4):
            for c in range(4):
                if grid[r][c] == 0:
                    continue
                neighbors = 0
                if r > 0 and grid[r - 1][c] > 0:
                    neighbors += 1
                if r < 3 and grid[r + 1][c] > 0:
                    neighbors += 1
                if c > 0 and grid[r][c - 1] > 0:
                    neighbors += 1
                if c < 3 and grid[r][c + 1] > 0:
                    neighbors += 1
                if neighbors == 0:
                    isolatedPenalty -= grid[r][c] * 2

        return (
            maxTile * 1.0 +
            empty * 500 +
            smoothness +
            mono * 100 +
            cornerBonus +
            gradient * 8 +
            isolatedPenalty
        )
'''
