import pickle
import random
import time
import copy
from Game2048 import *

class Player(BasePlayer):
    def __init__(self, timeLimit):
        BasePlayer.__init__(self, timeLimit)
        
        self._max_tile_value = 15 
        self._base_for_index = self._max_tile_value + 1

        self._patterns = {
            'straight_4_horizontal': [(0, 1, 2, 3)],
            'straight_4_vertical': [(0, 4, 8, 12)],
            'square_2x2': [(0, 1, 4, 5)],
            'rectangle_2x3_h': [(0, 1, 2, 4, 5, 6)], 
            'rectangle_2x3_v': [(0, 4, 8, 1, 5, 9)] 
        }
        
        self._n_tuple_tables = {}
        self._precomputed_symmetric_patterns = {}

        self._initialize_n_tuple_network()
        
        self._learningRate = 0.0025 
        self._discountFactor = 0.99

    def _initialize_n_tuple_network(self):
        for pattern_name, base_patterns in self._patterns.items():
            for base_pattern_tuple in base_patterns:
                symmetric_patterns_for_base = self._generate_symmetries(base_pattern_tuple)
                self._precomputed_symmetric_patterns[base_pattern_tuple] = symmetric_patterns_for_base
                
                tuple_length = len(base_pattern_tuple)
                table_size = (self._base_for_index) ** tuple_length
                self._n_tuple_tables[base_pattern_tuple] = {}
                for i in range(table_size):
                    self._n_tuple_tables[base_pattern_tuple][i] = random.uniform(0, 1)

    def _generate_symmetries(self, pattern_indices_tuple):
        symmetries = set()
        
        def to_rc(idx):
            return idx // 4, idx % 4
        
        def to_idx(r, c):
            return r * 4 + c

        def get_rotated_pattern_coords(coords, k):
            rotated_coords = []
            for r, c in coords:
                if k == 0: rotated_r, rotated_c = r, c
                elif k == 1: rotated_r, rotated_c = c, 3 - r
                elif k == 2: rotated_r, rotated_c = 3 - r, 3 - c
                elif k == 3: rotated_r, rotated_c = 3 - c, r
                rotated_coords.append((rotated_r, rotated_c))
            return tuple(sorted(rotated_coords))

        def get_flipped_pattern_coords(coords):
            flipped_coords = []
            for r, c in coords:
                flipped_coords.append((r, 3 - c))
            return tuple(sorted(flipped_coords))

        current_coords = tuple(to_rc(idx) for idx in pattern_indices_tuple)
        
        for k in range(4):
            rotated_coords = get_rotated_pattern_coords(current_coords, k)
            symmetries.add(tuple(to_idx(r, c) for r, c in rotated_coords))
        
        flipped_coords = get_flipped_pattern_coords(current_coords)
        for k in range(4):
            rotated_flipped_coords = get_rotated_pattern_coords(flipped_coords, k)
            symmetries.add(tuple(to_idx(r, c) for r, c in rotated_flipped_coords))

        return list(symmetries)

    def _get_tuple_index(self, board_segment_values):
        index = 0
        for i, tile_value in enumerate(board_segment_values):
            tile_value_capped = min(tile_value, self._max_tile_value)
            index += tile_value_capped * (self._base_for_index ** i)
        return index

    def value(self, board):
        total_value = 0.0
        for base_pattern_tuple, symmetric_patterns in self._precomputed_symmetric_patterns.items():
            current_lookup_table = self._n_tuple_tables[base_pattern_tuple]
            
            for sym_pattern_indices in symmetric_patterns:
                board_segment_values = tuple(board._board[idx] for idx in sym_pattern_indices)
                index = self._get_tuple_index(board_segment_values)
                total_value += current_lookup_table.get(index, 0)
                
        return total_value

    def findMove(self, board):
        bestValue = float('-inf')
        bestMove = ''
        
        actions = board.actions()
        if not actions:
            self.setMove(None)
            return

        for a in actions:
            afterstate_s_prime = board.move(a)
            r_immediate = afterstate_s_prime.getScore() - board.getScore()
            v = r_immediate + self.value(afterstate_s_prime)
                
            if v > bestValue:
                bestValue = v
                bestMove = a
                
        self.setMove(bestMove)

    def train(self, repetitions):
        save_interval = 10000 
        for trial in range(repetitions):
            if trial % 1000 == 0:
                print(f'Simulating game number {trial} of {repetitions}')
            
            state = Game2048()
            state.randomize()

            while not state.gameOver():
                self._startTime = time.time()
                
                actions = state.actions()
                if not actions:
                    break

                best_move_for_training = ''
                max_eval_for_training = float('-inf')

                for current_action in actions:
                    afterstate_s_prime_current = state.move(current_action)
                    r_current = afterstate_s_prime_current.getScore() - state.getScore()
                    current_eval = r_current + self.value(afterstate_s_prime_current)

                    if current_eval > max_eval_for_training:
                        max_eval_for_training = current_eval
                        best_move_for_training = current_action
                
                if not best_move_for_training:
                    break
                
                move = best_move_for_training
                oldState = state
                
                s_prime = oldState.move(move)
                r = s_prime.getScore() - oldState.getScore()

                state_s_double_prime, _ = oldState.result(move)
                
                actions_s_double_prime = state_s_double_prime.actions()
                if not actions_s_double_prime:
                    target_value = state_s_double_prime.getScore()
                else:
                    max_eval_a_next = float('-inf')
                    best_a_next = ''
                    for next_action in actions_s_double_prime:
                        afterstate_s_prime_next = state_s_double_prime.move(next_action)
                        r_s_prime_next = afterstate_s_prime_next.getScore() - state_s_double_prime.getScore()
                        eval_a_next = r_s_prime_next + self.value(afterstate_s_prime_next)
                        if eval_a_next > max_eval_a_next:
                            max_eval_a_next = eval_a_next
                            best_a_next = next_action
                    
                    if not best_a_next:
                        target_value = state_s_double_prime.getScore()
                    else:
                        s_next_prime = state_s_double_prime.move(best_a_next)
                        r_next = s_next_prime.getScore() - state_s_double_prime.getScore()
                        target_value = r_next + self.value(s_next_prime)
                
                current_afterstate_value = self.value(s_prime)
                update_amount = self._learningRate * (target_value - current_afterstate_value)
                
                for base_pattern_tuple, symmetric_patterns in self._precomputed_symmetric_patterns.items():
                    current_lookup_table = self._n_tuple_tables[base_pattern_tuple]
                    for sym_pattern_indices in symmetric_patterns:
                        board_segment_values = tuple(s_prime._board[idx] for idx in sym_pattern_indices)
                        index = self._get_tuple_index(board_segment_values)
                        current_lookup_table[index] = current_lookup_table.get(index, 0) + update_amount
                    
                state = state_s_double_prime

            if (trial + 1) % save_interval == 0:
                self.saveData('MyData.pkl')
                print(f'Saved data after {trial + 1} games.')

    def loadData(self, filename):
        try:
            with open(filename, 'rb') as dataFile:
                loaded_data = pickle.load(dataFile)
                if isinstance(loaded_data, dict):
                    self._n_tuple_tables = loaded_data
                else:
                    self._initialize_n_tuple_network()
        except FileNotFoundError:
            self._initialize_n_tuple_network()
        except Exception:
            self._initialize_n_tuple_network()

    def saveData(self, filename):
        with open(filename, 'wb') as dataFile:
            pickle.dump(self._n_tuple_tables, dataFile)

    def findMove(self, board):
        bestValue = float('-inf')
        bestMove = ''
        
        actions = board.actions()
        if not actions:
            self.setMove(None)
            return

        for a in actions:
            afterstate_s_prime = board.move(a)
            r_immediate = afterstate_s_prime.getScore() - board.getScore()
            v = r_immediate + self.value(afterstate_s_prime)
                
            if v > bestValue:
                bestValue = v
                bestMove = a
                
        self.setMove(bestMove)

if __name__ == '__main__':
    agent = Player(timeLimit=0.001)
    data_file = 'MyData.pkl' 
    agent.loadData(data_file)
    training_games = 10000 
    agent.train(training_games)
    agent.saveData(data_file)
