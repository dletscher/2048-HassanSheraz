import argparse
from Game2048 import Game2048
from MyAgent import Player

def play():
    parser = argparse.ArgumentParser()
    parser.add_argument('agent')
    parser.add_argument('time_limit', type=float)
    args = parser.parse_args()

    state = Game2048()
    agent = Player(args.time_limit)

    while not state.gameOver():
        move = agent.findMove(state)
        if move is None:
            break
        state, _ = state.result(move)

    print("Game Over! Score:", state.getScore())

if __name__ == '__main__':
    play()
