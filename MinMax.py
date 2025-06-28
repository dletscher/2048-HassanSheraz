class Player:
    def __init__(self, time_limit):
        self.time_limit = time_limit

    def findMove(self, state):
        return state.actions()[0] if state.actions() else None
