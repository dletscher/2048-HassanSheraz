import random
import time
import sys
from Game2048 import *

class Player(BasePlayer):
    def __init__(self, timeLimit):
        BasePlayer.__init__(self, timeLimit)
        self.max_search_depth = 5 
        self.max_empty_tiles_to_check = 4 

    def heuristic(self, board):
        empty_cells_weight = 2.7
        monotonicity_weight = 1.0
        smoothness_weight = 0.1
        max_tile_weight = 10.0
        corner_weight = 1000.0

        empty_cells = sum(1 for tile in board._board if tile == 0)
        max_tile_power = max(board._board)

        smoothness = 0
        for r in range(4):
            for c in range(4):
                current_tile = board.getTile(r, c)
                if current_tile == 0:
                    continue
                if c < 3 and board.getTile(r, c + 1) != 0:
                    smoothness -= abs(current_tile - board.getTile(r, c + 1))
                if r < 3 and board.getTile(r + 1, c) != 0:
                    smoothness -= abs(current_tile - board.getTile(r + 1, c))

        monotonicity = 0
        for r in range(4):
            increasing_row = 0
            decreasing_row = 0
            for c in range(3):
                if board.getTile(r,c) > board.getTile(r,c+1):
                    decreasing_row += board.getTile(r, c)
                else:
                    increasing_row += board.getTile(r, c + 1)
            monotonicity += min(increasing_row, decreasing_row)

        for c in range(4):
            increasing_col = 0
            decreasing_col = 0
            for r in range(3):
                if board.getTile(r,c) > board.getTile(r+1,c):
                    decreasing_col += board.getTile(r, c)
                else:
                    increasing_col += board.getTile(r + 1, c)
            monotonicity += min(increasing_col, decreasing_col)

        corner_score = 0
        if board.getTile(0, 0) == max_tile_power:
            corner_score = corner_weight * max_tile_power
        
        return (empty_cells * empty_cells_weight + 
                monotonicity * monotonicity_weight + 
                smoothness * smoothness_weight + 
                max_tile_power * max_tile_weight + 
                corner_score)

    def findMove(self, board):
        actions = board.actions()
        if not actions:
            self.setMove(None)
            return
            
        best_move_to_set = random.choice(actions)
        best_value_found = float('-inf')
        
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
                        
                    v = self.min_value(afterstate, depth - 1, alpha, beta)
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

    def max_value(self, state, depth, alpha, beta):
        if not self.timeRemaining():
            return None

        if state.gameOver() or depth == 0:
            return self.heuristic(state)

        best_value = float('-inf')
        for action in state.actions():
            afterstate = state.move(action)
            if afterstate is None:
                continue
            
            min_score = self.min_value(afterstate, depth - 1, alpha, beta)
            if min_score is None: return None
            
            best_value = max(best_value, min_score)
            
            alpha = max(alpha, best_value)
            if alpha >= beta:
                break
                
        return best_value

    def min_value(self, state, depth, alpha, beta):
        if not self.timeRemaining():
            return None
        
        if state.gameOver() or depth == 0:
            return self.heuristic(state)

        worst_value = float('inf')
        empty_indices = [i for i, tile in enumerate(state._board) if tile == 0]
        
        if not empty_indices:
            return self.heuristic(state)

        positions_to_check = empty_indices[:self.max_empty_tiles_to_check]
        
        for position in positions_to_check:
            next_state_board_2 = list(state._board)
            next_state_board_2[position] = 1
            next_state_2 = Game2048(next_state_board_2, state.getScore())
            
            v_2 = self.max_value(next_state_2, depth - 1, alpha, beta)
            if v_2 is None: return None
            worst_value = min(worst_value, v_2)
            
            beta = min(beta, worst_value)
            if alpha >= beta:
                return worst_value
            
            next_state_board_4 = list(state._board)
            next_state_board_4[position] = 2
            next_state_4 = Game2048(next_state_board_4, state.getScore())
            
            v_4 = self.max_value(next_state_4, depth - 1, alpha, beta)
            if v_4 is None: return None
            worst_value = min(worst_value, v_4)
            
            beta = min(beta, worst_value)
            if alpha >= beta:
                break
            
        return worst_value

    def loadData(self, filename):
        pass

    def saveData(self, filename):
        pass
