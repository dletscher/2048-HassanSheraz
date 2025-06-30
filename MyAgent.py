from Game2048 import BasePlayer

class Player(BasePlayer):
    def __init__(self, timeLimit):
        super().__init__(timeLimit)
        self._count = 0
        self._depthCount = 0
        self._nodeCount = 0
        self._parentCount = 0
        self._childCount = 0

    def findMove(self, state):
        self._count += 1
        actions = self.moveOrder(state)
        depth = 1
        while self.timeRemaining():
            self._depthCount += 1
            self._parentCount += 1
            self._nodeCount += 1

            best = -float('inf')
            bestMove = None

            for a in actions:
                result = state.move(a)
                if not self.timeRemaining():
                    return
                v = self.minPlayer(result, depth - 1)
                if v is None:
                    return
                if v > best:
                    best = v
                    bestMove = a

            if bestMove is not None:
                self.setMove(bestMove)
            depth += 1

    def maxPlayer(self, state, depth):
        self._nodeCount += 1
        self._childCount += 1

        if state.gameOver():
            return state.getScore()

        if depth == 0:
            return self.heuristic(state)

        self._parentCount += 1
        best = -float('inf')
        for a in self.moveOrder(state):
            if not self.timeRemaining():
                return None
            result = state.move(a)
            v = self.minPlayer(result, depth - 1)
            if v is None:
                return None
            if v > best:
                best = v

        return best

    def minPlayer(self, state, depth):
        self._nodeCount += 1
        self._childCount += 1

        if state.gameOver():
            return state.getScore()

        if depth == 0:
            return self.heuristic(state)

        self._parentCount += 1
        best = float('inf')
        for t, v in state.possibleTiles():
            if not self.timeRemaining():
                return None
            result = state.addTile(t, v)
            val = self.maxPlayer(result, depth - 1)
            if val is None:
                return None
            if val < best:
                best = val

        return best

    def heuristic(self, state):
        score = state.getScore()
        empty = sum(1 for i in range(4) for j in range(4) if state.getTile(i, j) == 0)
        smoothness = self.calculateSmoothness(state)
        monotonicity = self.calculateMonotonicity(state)
        cornerBonus = self.calculateCornerBonus(state)
        mergePotential = self.calculateMergePotential(state)
        return score + empty * 250 + monotonicity * 2.5 + smoothness * 0.2 + cornerBonus + mergePotential * 60

    def calculateSmoothness(self, state):
        smooth = 0
        for r in range(4):
            for c in range(3):
                val1 = state.getTile(r, c)
                val2 = state.getTile(r, c + 1)
                if val1 and val2:
                    smooth -= abs(val1 - val2)
        for c in range(4):
            for r in range(3):
                val1 = state.getTile(r, c)
                val2 = state.getTile(r + 1, c)
                if val1 and val2:
                    smooth -= abs(val1 - val2)
        return smooth

    def calculateMonotonicity(self, state):
        totals = [0, 0, 0, 0]
        for r in range(4):
            prev = 0
            for c in range(4):
                val = state.getTile(r, c)
                if val:
                    if prev and val > prev:
                        totals[0] += val - prev
                    elif prev:
                        totals[1] += prev - val
                    prev = val
        for c in range(4):
            prev = 0
            for r in range(4):
                val = state.getTile(r, c)
                if val:
                    if prev and val > prev:
                        totals[2] += val - prev
                    elif prev:
                        totals[3] += prev - val
                    prev = val
        return max(totals[0], totals[1]) + max(totals[2], totals[3])

    def calculateCornerBonus(self, state):
        corners = [state.getTile(0, 0), state.getTile(0, 3), state.getTile(3, 0), state.getTile(3, 3)]
        maxTile = max(state.getTile(r, c) for r in range(4) for c in range(4))
        return maxTile * 2 if maxTile in corners else 0

    def calculateMergePotential(self, state):
        merges = 0
        for r in range(4):
            for c in range(3):
                if state.getTile(r, c) == state.getTile(r, c + 1) and state.getTile(r, c) != 0:
                    merges += 1
        for c in range(4):
            for r in range(3):
                if state.getTile(r, c) == state.getTile(r + 1, c) and state.getTile(r, c) != 0:
                    merges += 1
        return merges

    def moveOrder(self, state):
        return state.actions()

    def stats(self):
        print(f'Average depth: {self._depthCount / self._count:.2f}')
        print(f'Branching factor: {self._childCount / self._parentCount:.2f}')





'''
Latest best one with 14,477.44	31,884	15,004 score
from Game2048 import BasePlayer

class Player(BasePlayer):
    def __init__(self, timeLimit):
        BasePlayer.__init__(self, timeLimit)
        self._count = 0
        self._depthCount = 0
        self._nodeCount = 0
        self._parentCount = 0
        self._childCount = 0

    def findMove(self, state):
        self._count += 1
        actions = self.moveOrder(state)
        depth = 1
        while self.timeRemaining():
            self._depthCount += 1
            self._parentCount += 1
            self._nodeCount += 1

            best = -float('inf')
            for a in actions:
                result = state.move(a)
                if not self.timeRemaining():
                    return
                v = self.minPlayer(result, depth - 1)
                if v is None:
                    return
                if v > best:
                    best = v
                    bestMove = a

            self.setMove(bestMove)
            depth += 1

    def maxPlayer(self, state, depth):
        self._nodeCount += 1
        self._childCount += 1

        if state.gameOver():
            return state.getScore()

        if depth == 0:
            return self.heuristic(state)

        self._parentCount += 1
        best = -float('inf')
        for a in self.moveOrder(state):
            if not self.timeRemaining():
                return None
            result = state.move(a)
            v = self.minPlayer(result, depth - 1)
            if v is None:
                return None
            if v > best:
                best = v

        return best

    def minPlayer(self, state, depth):
        self._nodeCount += 1
        self._childCount += 1

        if state.gameOver():
            return state.getScore()

        if depth == 0:
            return self.heuristic(state)

        self._parentCount += 1
        best = float('inf')
        for t, v in state.possibleTiles():
            if not self.timeRemaining():
                return None
            result = state.addTile(t, v)
            val = self.maxPlayer(result, depth - 1)
            if val is None:
                return None
            if val < best:
                best = val

        return best

    def heuristic(self, state):
        score = state.getScore()
        empty = sum(1 for i in range(4) for j in range(4) if state.getTile(i, j) == 0)
        smoothness = self.calculateSmoothness(state)
        monotonicity = self.calculateMonotonicity(state)
        cornerBonus = self.calculateCornerBonus(state)
        mergePotential = self.calculateMergePotential(state)
        return score + empty * 200 + monotonicity * 2.0 + smoothness * 0.1 + cornerBonus + mergePotential * 50

    def calculateSmoothness(self, state):
        smooth = 0
        for r in range(4):
            for c in range(3):
                val1 = state.getTile(r, c)
                val2 = state.getTile(r, c + 1)
                if val1 and val2:
                    smooth -= abs(val1 - val2)
        for c in range(4):
            for r in range(3):
                val1 = state.getTile(r, c)
                val2 = state.getTile(r + 1, c)
                if val1 and val2:
                    smooth -= abs(val1 - val2)
        return smooth

    def calculateMonotonicity(self, state):
        totals = [0, 0, 0, 0]
        for r in range(4):
            prev = 0
            for c in range(4):
                val = state.getTile(r, c)
                if val:
                    if prev and val > prev:
                        totals[0] += val - prev
                    elif prev:
                        totals[1] += prev - val
                    prev = val
        for c in range(4):
            prev = 0
            for r in range(4):
                val = state.getTile(r, c)
                if val:
                    if prev and val > prev:
                        totals[2] += val - prev
                    elif prev:
                        totals[3] += prev - val
                    prev = val
        return max(totals[0], totals[1]) + max(totals[2], totals[3])

    def calculateCornerBonus(self, state):
        corners = [state.getTile(0,0), state.getTile(0,3), state.getTile(3,0), state.getTile(3,3)]
        maxTile = max(state.getTile(r, c) for r in range(4) for c in range(4))
        if maxTile in corners:
            return maxTile * 2
        return 0

    def calculateMergePotential(self, state):
        merges = 0
        for r in range(4):
            for c in range(3):
                if state.getTile(r, c) == state.getTile(r, c+1) and state.getTile(r, c) != 0:
                    merges += 1
        for c in range(4):
            for r in range(3):
                if state.getTile(r, c) == state.getTile(r+1, c) and state.getTile(r, c) != 0:
                    merges += 1
        return merges

    def moveOrder(self, state):
        return state.actions()

    def stats(self):
        print(f'Average depth: {self._depthCount/self._count:.2f}')
        print(f'Branching factor: {self._childCount / self._parentCount:.2f}')




FINE TUNING WITH SCORE UPTO 25,000 + STABLE 

from Game2048 import BasePlayer

class Player(BasePlayer):
    def __init__(self, timeLimit):
        BasePlayer.__init__(self, timeLimit)
        self._count = 0
        self._depthCount = 0
        self._nodeCount = 0
        self._parentCount = 0
        self._childCount = 0

    def findMove(self, state):
        self._count += 1
        actions = self.moveOrder(state)
        depth = 1
        while self.timeRemaining():
            self._depthCount += 1
            self._parentCount += 1
            self._nodeCount += 1

            best = -float('inf')
            for a in actions:
                result = state.move(a)
                if not self.timeRemaining():
                    return
                v = self.minPlayer(result, depth - 1)
                if v is None:
                    return
                if v > best:
                    best = v
                    bestMove = a

            self.setMove(bestMove)
            depth += 1

    def maxPlayer(self, state, depth):
        self._nodeCount += 1
        self._childCount += 1

        if state.gameOver():
            return state.getScore()

        if depth == 0:
            return self.heuristic(state)

        self._parentCount += 1
        best = -float('inf')
        for a in self.moveOrder(state):
            if not self.timeRemaining():
                return None
            result = state.move(a)
            v = self.minPlayer(result, depth - 1)
            if v is None:
                return None
            if v > best:
                best = v

        return best

    def minPlayer(self, state, depth):
        self._nodeCount += 1
        self._childCount += 1

        if state.gameOver():
            return state.getScore()

        if depth == 0:
            return self.heuristic(state)

        self._parentCount += 1
        best = float('inf')
        for t, v in state.possibleTiles():
            if not self.timeRemaining():
                return None
            result = state.addTile(t, v)
            val = self.maxPlayer(result, depth - 1)
            if val is None:
                return None
            if val < best:
                best = val

        return best

    def heuristic(self, state):
        score = state.getScore()
        empty = sum(1 for i in range(4) for j in range(4) if state.getTile(i, j) == 0)
        smoothness = self.calculateSmoothness(state)
        monotonicity = self.calculateMonotonicity(state)
        return score + empty * 350 + monotonicity * 1.0 + smoothness * 0.1

    def calculateSmoothness(self, state):
        smooth = 0
        for r in range(4):
            for c in range(3):
                val1 = state.getTile(r, c)
                val2 = state.getTile(r, c+1)
                if val1 and val2:
                    smooth -= abs((2**val1) - (2**val2))
        for c in range(4):
            for r in range(3):
                val1 = state.getTile(r, c)
                val2 = state.getTile(r+1, c)
                if val1 and val2:
                    smooth -= abs((2**val1) - (2**val2))
        return smooth

    def calculateMonotonicity(self, state):
        totals = [0, 0, 0, 0]

        for r in range(4):
            prev = 0
            for c in range(4):
                val = state.getTile(r, c)
                if val:
                    if prev and val > prev:
                        totals[0] += 2**val - 2**prev
                    elif prev:
                        totals[1] += 2**prev - 2**val
                    prev = val

        for c in range(4):
            prev = 0
            for r in range(4):
                val = state.getTile(r, c)
                if val:
                    if prev and val > prev:
                        totals[2] += 2**val - 2**prev
                    elif prev:
                        totals[3] += 2**prev - 2**val
                    prev = val

        return max(totals[0], totals[1]) + max(totals[2], totals[3])

    def moveOrder(self, state):
        return state.actions()

    def stats(self):
        print(f'Average depth: {self._depthCount/self._count:.2f}')
        print(f'Branching factor: {self._childCount / self._parentCount:.2f}')





INITIAL WORKING
from Game2048 import *

class Player(BasePlayer):
	def __init__(self, timeLimit):
		BasePlayer.__init__(self, timeLimit)

		self._nodeCount = 0
		self._parentCount = 0
		self._childCount = 0
		self._depthCount = 0
		self._count = 0

	def findMove(self, state):
		self._count += 1
		actions = self.moveOrder(state)
		depth = 2
		while self.timeRemaining():
			self._depthCount += 1
			self._parentCount += 1
			self._nodeCount += 1
			print('Search depth', depth)
			best = -10000
			for a in actions:
				result = state.move(a)
				if not self.timeRemaining(): return
				v = self.minPlayer(result, depth-1)
				if v is None: return
				if v > best:
					best = v
					bestMove = a
						
			self.setMove(bestMove)
			print('\tBest value', best, bestMove)

			depth += 1

	def maxPlayer(self, state, depth):
		# The max player gets to choose the move
		self._nodeCount += 1
		self._childCount += 1

		if state.gameOver():
			return state.getScore()
			
		actions = self.moveOrder(state)

		if depth == 0:
			return self.heuristic(state)

		self._parentCount += 1
		best = -10000
		for a in actions:
			if not self.timeRemaining(): return None
			result = state.move(a)
			v = self.minPlayer(result, depth-1)
			if v is None: return None
			if v > best:
				best = v
				
		return best

	def minPlayer(self, state, depth):
		# The min player chooses where to add the extra tile and whether it is a 2 or a 4
		self._nodeCount += 1
		self._childCount += 1

		if state.gameOver():
			return state.getScore()
			
		actions = self.moveOrder(state)

		if depth == 0:
			return self.heuristic(state)

		self._parentCount += 1
		best = 1e6
		for (t,v) in state.possibleTiles():
			if not self.timeRemaining(): return None
			result = state.addTile(t,v)
			v = self.maxPlayer(result, depth-1)
			if v is None: return None
			if v < best:
				best = v

		return best

	def heuristic(self, state):
		return state.getScore()
		
	def moveOrder(self, state):
		return state.actions()

	def stats(self):
		print(f'Average depth: {self._depthCount/self._count:.2f}')
		print(f'Branching factor: {self._childCount / self._parentCount:.2f}')
		'''
