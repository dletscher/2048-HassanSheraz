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
