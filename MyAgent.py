import random
import time
import sys
from Game2048 import *

class Player(BasePlayer):
    def __init__(self, timeLimit):
        BasePlayer.__init__(self, timeLimit)
        self.max_search_depth = 2

    def heuristic(self, board):
        empty_cells_weight = 2.0
        monotonicity_weight = 1.0
        smoothness_weight = 0.5
        max_tile_weight = 0.5

        empty_cells = sum(1 for tile in board._board if tile == 0)
        max_tile_power = max(board._board)

        smoothness = 0
        for i in range(16):
            r, c = i // 4, i % 4
            current_tile = board._board[i]
            if current_tile == 0:
                continue
            if c > 0 and board.getTile(r, c - 1) != 0:
                smoothness -= abs(current_tile - board.getTile(r, c - 1))
            if r > 0 and board.getTile(r - 1, c) != 0:
                smoothness -= abs(current_tile - board.getTile(r - 1, c))

        monotonicity = 0
        for r in range(4):
            row = [board.getTile(r, c) for c in range(4) if board.getTile(r, c) != 0]
            if len(row) > 1:
                is_increasing_left_to_right = all(row[i] <= row[i + 1] for i in range(len(row) - 1))
                is_decreasing_left_to_right = all(row[i] >= row[i + 1] for i in range(len(row) - 1))
                if is_increasing_left_to_right or is_decreasing_left_to_right:
                    monotonicity += sum(row)
        
        for c in range(4):
            col = [board.getTile(r, c) for r in range(4) if board.getTile(r, c) != 0]
            if len(col) > 1:
                is_increasing_top_to_bottom = all(col[i] <= col[i + 1] for i in range(len(col) - 1))
                is_decreasing_top_to_bottom = all(col[i] >= col[i + 1] for i in range(len(col) - 1))
                if is_increasing_top_to_bottom or is_decreasing_top_to_bottom:
                    monotonicity += sum(col)
        
        return (empty_cells * empty_cells_weight + 
                monotonicity * monotonicity_weight + 
                smoothness * smoothness_weight + 
                max_tile_power * max_tile_weight)

    def findMove(self, board):
        actions = board.actions()
        if not actions:
            self.setMove(None)
            return
            
        best_move_so_far = random.choice(actions)
        best_value_for_depth = float('-inf')
        
        try:
            for action in actions:
                afterstate = board.move(action)
                if afterstate is None:
                    continue
                    
                v = self.expectimax_value(afterstate, self.max_search_depth - 1)
                if v is None: raise TimeoutError
                
                if v > best_value_for_depth:
                    best_value_for_depth = v
                    best_move_so_far = action
        
        except TimeoutError:
            pass
            
        self.setMove(best_move_so_far)

    def expectimax_value(self, state, depth):
        if not self.timeRemaining():
            return None
            
        if state.gameOver() or depth == 0:
            return self.heuristic(state)

        return self.max_value(state, depth)

    def max_value(self, state, depth):
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
            
            chance_value = self.chance_value(afterstate, depth - 1)
            if chance_value is None: return None
            
            best_value = max(best_value, chance_value)
            
        return best_value

    def chance_value(self, state, depth):
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
            
            v_2 = self.max_value(next_state_2, depth)
            if v_2 is None: return None
            expected_value += prob_2_tile * v_2
            
            next_state_board_4 = list(state._board)
            next_state_board_4[position] = 2
            next_state_4 = Game2048(next_state_board_4, state.getScore())
            prob_4_tile = 0.25 / len(empty_indices)
            
            v_4 = self.max_value(next_state_4, depth)
            if v_4 is None: return None
            expected_value += prob_4_tile * v_4
            
        return expected_value

    def loadData(self, filename):
        pass

    def saveData(self, filename):
        pass
