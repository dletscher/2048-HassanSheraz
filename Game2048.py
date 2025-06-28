import random

class Game2048:
    def __init__(self, board=None):
        if board:
            self._board = [row[:] for row in board]
        else:
            self._board = [[0]*4 for _ in range(4)]
            self.add_random_tile()
            self.add_random_tile()
        self._score = 0

    def clone(self):
        new = Game2048(self._board)
        new._score = self._score
        return new

    def randomize(self):
        pass

    def actions(self):
        return [a for a in 'UDLR' if self.clone().move(a) != self._board]

    def add_random_tile(self):
        empty = [(r, c) for r in range(4) for c in range(4) if self._board[r][c] == 0]
        if empty:
            r, c = random.choice(empty)
            self._board[r][c] = 2 if random.random() < 0.9 else 4

    def move(self, direction):
        def slide(row):
            new = [i for i in row if i]
            for i in range(len(new) - 1):
                if new[i] == new[i+1]:
                    new[i] *= 2
                    self._score += new[i]
                    new[i+1] = 0
            new = [i for i in new if i]
            return new + [0]*(4 - len(new))

        board = [row[:] for row in self._board]
        if direction == 'L':
            self._board = [slide(row) for row in board]
        elif direction == 'R':
            self._board = [slide(row[::-1])[::-1] for row in board]
        elif direction == 'U':
            self._board = [list(x) for x in zip(*[slide(col) for col in zip(*board)])]
        elif direction == 'D':
            self._board = [list(x) for x in zip(*[slide(col[::-1])[::-1] for col in zip(*board)])]
        return self._board

    def result(self, move):
        new_state = self.clone()
        new_state.move(move)
        new_state.add_random_tile()
        return new_state, new_state._score

    def gameOver(self):
        return len(self.actions()) == 0

    def getScore(self):
        return self._score
