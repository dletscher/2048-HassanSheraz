import random

class Game2048:
    def __init__(self):
        self._board = [0] * 16
        self._score = 0
        self.randomize()

    def randomize(self):
        for _ in range(2):
            self.addRandomTile()

    def actions(self):
        return ['U', 'D', 'L', 'R']

    def result(self, move):
        child = self.clone()
        score = child.move(move)
        return child, score

    def clone(self):
        new = Game2048()
        new._board = self._board[:]
        new._score = self._score
        return new

    def move(self, direction):
        board = [2 ** x if x > 0 else 0 for x in self._board]
        score = 0

        for i in range(4):
            line = []
            for j in range(4):
                idx = i * 4 + j if direction in 'LR' else j * 4 + i
                val = board[idx]
                if val != 0:
                    line.append(val)

            if direction in 'RD':
                line.reverse()

            merged = []
            skip = False
            for k in range(len(line)):
                if skip:
                    skip = False
                    continue
                if k + 1 < len(line) and line[k] == line[k + 1]:
                    merged.append(line[k] * 2)
                    score += line[k] * 2
                    skip = True
                else:
                    merged.append(line[k])

            while len(merged) < 4:
                merged.append(0)

            if direction in 'RD':
                merged.reverse()

            for j in range(4):
                idx = i * 4 + j if direction in 'LR' else j * 4 + i
                board[idx] = merged[j]

        changed = False
        for i in range(16):
            val = board[i]
            exp = int(val).bit_length() - 1 if val > 0 else 0
            if exp != self._board[i]:
                self._board[i] = exp
                changed = True

        if changed:
            self._score += score
            self.addRandomTile()

        return score

    def getTile(self, r, c):
        return self._board[r * 4 + c]

    def addRandomTile(self):
        empties = [i for i, x in enumerate(self._board) if x == 0]
        if not empties:
            return
        idx = random.choice(empties)
        self._board[idx] = 1 if random.random() < 0.9 else 2

    def gameOver(self):
        if any(x == 0 for x in self._board):
            return False
        for move in self.actions():
            child, _ = self.result(move)
            if child._board != self._board:
                return False
        return True

    def __str__(self):
        rows = []
        for r in range(4):
            row = []
            for c in range(4):
                val = self.getTile(r, c)
                row.append(f'{2 ** val if val > 0 else "."}')
            rows.append('\t'.join(row))
        return '\n'.join(rows) + f'\nScore: {self._score}\n'

'''
OLDER WORKING VERSION WITH GOOD IMPROVEMENTS
import time
import random
import copy

class Game2048:
	def __init__(self, b=None, s=None):
		if b:
			self._board = b
		else:
			self._board = [0] * 16
		
		if s:
			self._score = s
		else:
			self._score = 0
		
	def randomize(self):
		self._board = []
		for i in range(16):
			self._board.append(random.choice([0]*16 + [1]*4 + [2]*2 + [3]))

	def actions(self):
		return ''.join([ a for a in 'UDLR' if self.move(a)._board != self._board ])

	def result(self, a):
		s = self._score
		g = self.move(a)
		zeros = [ i for i in range(16) if g._board[i] == 0 ]
		i = random.choice(zeros)
		if random.randint(0,3) == 3:
			g._board[i] = 2
		else:
			g._board[i] = 1
		return g, g._score - s
		
	def getScore(self):
		return self._score
		
	def getTile(self, r, c):
		return self._board[4*r+c]

	def possibleResults(self, a):
		s = self._score
		possible = []
		g = self.move(a)
		zeros = [ i for i in range(16) if g._board[i] == 0 ]
		for i in zeros:
			g = self.move(a)
			for t in [1,2]:
				g._board[i] = t
				if t == 1:
					possible.append((g,.75/len(zeros)))
				else:
					possible.append((g,.25/len(zeros)))
			
		return possible

	def move(self, action):
		board = []
		s = self._score
		if action == 'R':
			for i in range(0,16,4):
				compressed = [t for t in self._board[i:i+4] if t != 0]
				j = len(compressed) - 1
				r = []
				while j >= 0:
					if j > 0 and compressed[j] == compressed[j-1]:
						s += 2*(2**compressed[j])
						r.insert(0,compressed[j]+1)
						j -= 2
					else:
						r.insert(0,compressed[j])
						j -= 1
				r = [0] * (4-len(r)) + r					
				board.extend(r)
			return Game2048(board, s)
		elif action == 'L':
			for i in range(0,16,4):
				compressed = [t for t in self._board[i:i+4] if t != 0]
				j = 0
				r = []
				while j < len(compressed):
					if j < len(compressed)-1 and compressed[j] == compressed[j+1]:
						s += 2*(2**compressed[j])
						r.append(compressed[j]+1)
						j += 2
					else:
						r.append(compressed[j])
						j += 1
				r = r + [0] * (4-len(r))					
				board.extend(r)
			return Game2048(board, s)
		elif action == 'D':
			return self._flip().move('R')._flip()
		elif action == 'U':
			f = self._flip()
			return self._flip().move('L')._flip()
		else:
			print('ERROR move =', action)
				
	def _flip(self):
		r = []
		for i in range(4):
			r.extend( self._board[i:16:4] )
		return Game2048(r, self._score)
		
	def rotate(self, numRotations):
		numRotations = numRotations % 4
		if numRotations == 0:
			return Game2048(copy.copy(self._board), self._score)
			
		if numRotations == 1:
			b = [0]*16
			for r in range(4):
				for c in range(4):
					b[4*c + 3-r] = self._board[4*r+c]
			return Game2048(b, self._score)
			
		if numRotations == 2:
			b = [0]*16
			for r in range(4):
				for c in range(4):
					b[4*(3-r) + 3-c] = self._board[4*r+c]
			return Game2048(b, self._score)
			
		if numRotations == 3:
			b = [0]*16
			for r in range(4):
				for c in range(4):
					b[4*(3-c) + r] = self._board[4*r+c]
			return Game2048(b, self._score)
			
	def gameOver(self):
		return self.actions() == '' or 16 in self._board

	def __str__(self):
		s = ''
		for r in range(0,16,4):
			s += ' '.join(f'{2**x} '.rjust(5) for x in self._board[r:r+4]).replace(' 1 ','   ') + '\n'
		s += f'Score = {self._score}'
		return s
		
class BasePlayer:
	def __init__(self, timeLimit):
		self._timeLimit = timeLimit
		self._startTime = 0
		self._move = None

	def timeRemaining(self):
		if time.time() < self._startTime + self._timeLimit:
			return True
		return False

	def setMove(self, move):
		if self.timeRemaining():
			self._move = move

	def getMove(self):
		return self._move

	def stats(self):
		pass
		
	def saveData(self, filename):
		pass
		
	def loadData(self, filename):
		pass






Latest complicated work that works offline but crash online
import random
import copy

class Game2048:
    def __init__(self):
        self._board = [0] * 16
        self._score = 0
        self.spawnTile()
        self.spawnTile()

    def getTile(self, row, col):
        return self._board[4 * row + col]

    def spawnTile(self):
        empty = [i for i, x in enumerate(self._board) if x == 0]
        if not empty:
            return False
        index = random.choice(empty)
        self._board[index] = 1 if random.random() < 0.9 else 2  # 1 = 2, 2 = 4
        return True

    def actions(self):
        return ['U', 'D', 'L', 'R']

    def result(self, move):
        newGame = self.clone()
        moved, points = newGame.move(move)
        if moved:
            newGame.spawnTile()
        return newGame, points

    def move(self, direction):
        moved = False
        points = 0
        grid = [[self.getTile(r, c) for c in range(4)] for r in range(4)]

        if direction == 'L':
            for r in range(4):
                row, p = self._merge(grid[r])
                points += p
                row += [0] * (4 - len(row))
                grid[r] = row
        elif direction == 'R':
            for r in range(4):
                row = grid[r][::-1]
                row, p = self._merge(row)
                points += p
                row += [0] * (4 - len(row))
                grid[r] = row[::-1]
        elif direction == 'U':
            for c in range(4):
                col = [grid[r][c] for r in range(4)]
                col, p = self._merge(col)
                points += p
                col += [0] * (4 - len(col))
                for r in range(4):
                    grid[r][c] = col[r]
        elif direction == 'D':
            for c in range(4):
                col = [grid[r][c] for r in range(4)][::-1]
                col, p = self._merge(col)
                points += p
                col += [0] * (4 - len(col))
                for r in range(4):
                    grid[r][c] = col[::-1][r]

        for r in range(4):
            for c in range(4):
                if self.getTile(r, c) != grid[r][c]:
                    moved = True
                self._board[4 * r + c] = grid[r][c]

        self._score += points
        return moved, points

    def _merge(self, tiles):
        newTiles = []
        score = 0
        skip = False
        for i in range(len(tiles)):
            if tiles[i] == 0:
                continue
            if skip:
                skip = False
                continue
            if i + 1 < len(tiles) and tiles[i] == tiles[i + 1]:
                newTiles.append(tiles[i] + 1)
                score += 2 ** (tiles[i] + 1)
                skip = True
            else:
                newTiles.append(tiles[i])
        return newTiles, score

    def gameOver(self):
        if any(x == 0 for x in self._board):
            return False
        for r in range(4):
            for c in range(4):
                t = self.getTile(r, c)
                for dr, dc in [(1, 0), (0, 1)]:
                    nr, nc = r + dr, c + dc
                    if nr < 4 and nc < 4 and t == self.getTile(nr, nc):
                        return False
        return True

    def clone(self):
        return copy.deepcopy(self)

    def insertTile(self, pos, value):
        self._board[4 * pos[0] + pos[1]] = value

    def randomize(self):
        self._board = [0] * 16
        self._score = 0
        self.spawnTile()
        self.spawnTile()

    def __str__(self):
        lines = []
        for r in range(4):
            row = []
            for c in range(4):
                val = self.getTile(r, c)
                if val == 0:
                    row.append('.')
                else:
                    row.append(str(2 ** val))
            lines.append('\t'.join(row))
        lines.append(f'Score: {self._score}')
        return '\n'.join(lines)

'''
