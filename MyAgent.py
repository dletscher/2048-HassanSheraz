import pickle
import random
import time
import copy
from Game2048 import *

class Player(BasePlayer):
    def __init__(self, timeLimit):
        BasePlayer.__init__(self, timeLimit)
        
        self._max_tile_value = 15 
        self._tuple_length = 4 
        self._base_for_index = self._max_tile_value + 1
        self._table_size = (self._base_for_index) ** self._tuple_length
        self._valueTable = {}
        
        for i in range(self._table_size):
            self._valueTable[i] = random.uniform(0, 1)
                        
        self._learningRate = 0.0025 
        self._discountFactor = 0.99
        
    def _get_tuple_index(self, board_segment):
        index = 0
        for i, tile_value in enumerate(board_segment):
            index += tile_value * (self._base_for_index ** i)
        return index

    def value(self, board):
        total_value = 0.0
        for turns in range(4):
            rotated_board = board.rotate(turns)._board
            board_segment = tuple(rotated_board[:self._tuple_length])
            index = self._get_tuple_index(board_segment)
            total_value += self._valueTable.get(index, 0)
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
                
                for turns in range(4):
                    rotated_s_prime = s_prime.rotate(turns)
                    board_segment = tuple(rotated_s_prime._board[:self._tuple_length])
                    index = self._get_tuple_index(board_segment)
                    self._valueTable[index] = self._valueTable.get(index, 0) + update_amount
                    
                state = state_s_double_prime

            if (trial + 1) % save_interval == 0:
                self.saveData('MyData.pkl')
                print(f'Saved data after {trial + 1} games.')

    def loadData(self, filename):
        try:
            with open(filename, 'rb') as dataFile:
                loaded_data = pickle.load(dataFile)
                if isinstance(loaded_data, dict):
                    self._valueTable = loaded_data
                else:
                    self._valueTable = {}
                    for i in range(self._table_size):
                        self._valueTable[i] = random.uniform(0, 1)
        except FileNotFoundError:
            self._valueTable = {}
            for i in range(self._table_size):
                self._valueTable[i] = random.uniform(0, 1)
        except Exception:
            self._valueTable = {}
            for i in range(self._table_size):
                self._valueTable[i] = random.uniform(0, 1)

    def saveData(self, filename):
        with open(filename, 'wb') as dataFile:
            pickle.dump(self._valueTable, dataFile)

if __name__ == '__main__':
    agent = Player(timeLimit=1.0) 
    data_file = 'MyData.pkl' 
    agent.loadData(data_file)
    training_games = 500000 
    agent.train(training_games)
    agent.saveData(data_file)