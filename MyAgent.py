import random
import time
import sys
from Game2048 import *

class Player(BasePlayer):
    def __init__(self, timeLimit):
        BasePlayer.__init__(self, timeLimit)

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
        depth = 1
        
        while self.timeRemaining():
            try:
                best_value_for_depth = float('-inf')
                best_move_for_depth = None

                for action in actions:
                    if not self.timeRemaining():
                        raise TimeoutError
                        
                    expected_value = 0
                    possible_results = board.possibleResults(action)
                    
                    if not possible_results:
                        continue
                        
                    for next_state, probability in possible_results:
                        v = self.expectimax_value(next_state, depth - 1)
                        if v is None: raise TimeoutError
                        expected_value += probability * v
                    
                    if expected_value > best_value_for_depth:
                        best_value_for_depth = expected_value
                        best_move_for_depth = action
                
                # If a full depth level was completed, update the best move.
                if best_move_for_depth is not None:
                    best_move_so_far = best_move_for_depth
                
            except TimeoutError:
                break
            
            depth += 1
            
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

        best_value = float('-inf')
        for action in state.actions():
            afterstate = state.move(action)
            
            chance_value = self.chance_value(afterstate, depth)
            if chance_value is None: return None
            
            best_value = max(best_value, chance_value)
            
        return best_value

    def chance_value(self, state, depth):
        if not self.timeRemaining():
            return None
        
        if state.gameOver():
            return self.heuristic(state)

        expected_value = 0
        possible_tiles = state.possibleTiles()
        
        if not possible_tiles:
            return self.heuristic(state)

        for position, value in possible_tiles:
            next_state_board = list(state._board)
            next_state_board[position] = value
            next_state = Game2048(next_state_board, state.getScore())
            
            probability = 0.9 if value == 1 else 0.1
            
            v = self.max_value(next_state, depth)
            if v is None: return None
            expected_value += probability * v
            
        return expected_value

    def loadData(self, filename):
        pass

    def saveData(self, filename):
        pass
