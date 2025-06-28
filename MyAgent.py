import random
import time
import sys
from Game2048 import *

class Player(BasePlayer):
    def __init__(self, timeLimit):
        BasePlayer.__init__(self, timeLimit)
        self._cache = {}
        self.max_search_depth = 4

    def heuristic(self, board):
        empty_cells = sum(1 for tile in board._board if tile == 0)
        max_tile_power = max(board._board)

        smoothness = 0
        for r in range(4):
            for c in range(4):
                if board.getTile(r, c) != 0:
                    current_tile = board.getTile(r, c)
                    if c < 3 and board.getTile(r, c + 1) != 0:
                        smoothness -= abs(current_tile - board.getTile(r, c + 1))
                    if r < 3 and board.getTile(r + 1, c) != 0:
                        smoothness -= abs(current_tile - board.getTile(r + 1, c))

        monotonicity = 0
        for i in range(16):
            r, c = i // 4, i % 4
            if r < 3:
                monotonicity += board.getTile(r, c) - board.getTile(r + 1, c)
            if c < 3:
                monotonicity += board.getTile(r, c) - board.getTile(r, c + 1)
        
        return empty_cells * 2 + monotonicity + smoothness + max_tile_power * 10

    def findMove(self, board):
        actions = board.actions()
        if not actions:
            self.setMove(None)
            return
            
        best_move_to_set = random.choice(actions)
        best_value_found = float('-inf')
        
        self._cache = {} 
        depth = 1
        
        while self.timeRemaining() and depth <= self.max_search_depth:
            try:
                current_depth_best_value = float('-inf')
                current_depth_best_move = None
                alpha = float('-inf')
                beta = float('inf')

                for action in actions:
                    if not self.timeRemaining():
                        raise TimeoutError
                        
                    afterstate = board.move(action)
                    if afterstate is None:
                        continue
                        
                    v = self.chance_value(afterstate, depth - 1, alpha, beta)
                    if v is None: raise TimeoutError
                    
                    if v > current_depth_best_value:
                        current_depth_best_value = v
                        current_depth_best_move = action
                    
                    alpha = max(alpha, v)
                    if alpha >= beta:
                        break
                
                if current_depth_best_move is not None:
                    if current_depth_best_value > best_value_found:
                        best_value_found = current_depth_best_value
                        best_move_to_set = current_depth_best_move
            
            except TimeoutError:
                break
            
            depth += 1
            
        self.setMove(best_move_to_set)

    def expectimax_value(self, state, depth, alpha, beta):
        state_tuple = tuple(state._board)
        cache_key = (state_tuple, depth, alpha, beta)
        if cache_key in self._cache:
            return self._cache[cache_key]

        if not self.timeRemaining():
            return None
            
        if state.gameOver() or depth == 0:
            return self.heuristic(state)

        value = self.max_value(state, depth, alpha, beta)
        self._cache[cache_key] = value
        return value

    def max_value(self, state, depth, alpha, beta):
        if not self.timeRemaining():
            return None

        if state.gameOver():
            return self.heuristic(state)
        
        if depth == 0:
            return self.heuristic(state)

        best_value = float('-inf')
        for action in state.actions():
            afterstate = state.move(action)
            if afterstate is None:
                continue
            
            chance_value = self.chance_value(afterstate, depth - 1, alpha, beta)
            if chance_value is None: return None
            
            best_value = max(best_value, chance_value)
            
            alpha = max(alpha, best_value)
            if alpha >= beta:
                break
                
        return best_value

    def chance_value(self, state, depth, alpha, beta):
        if not self.timeRemaining():
            return None
        
        if state.gameOver():
            return self.heuristic(state)

        expected_value = 0
        empty_indices = [i for i, tile in enumerate(state._board) if tile == 0]
        
        if not empty_indices:
            return self.heuristic(state)

        for position in empty_indices:
            
            next_state_board_2 = list(state._board)
            next_state_board_2[position] = 1
            next_state_2 = Game2048(next_state_board_2, state.getScore())
            prob_2_tile = 0.75 / len(empty_indices) 
            
            v_2 = self.max_value(next_state_2, depth, alpha, beta)
            if v_2 is None: return None
            expected_value += prob_2_tile * v_2
            
            next_state_board_4 = list(state._board)
            next_state_board_4[position] = 2
            next_state_4 = Game2048(next_state_board_4, state.getScore())
            prob_4_tile = 0.25 / len(empty_indices)
            
            v_4 = self.max_value(next_state_4, depth, alpha, beta)
            if v_4 is None: return None
            expected_value += prob_4_tile * v_4
            
        return expected_value

    def loadData(self, filename):
        pass

    def saveData(self, filename):
        pass
