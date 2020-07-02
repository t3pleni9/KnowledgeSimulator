class State:
    def __init__(self, behavior, agent, reasoner):
        self.behavior = behavior
        self.agent = agent
        self.reasoner = reasoner
        self.time_to_finish = 1

    def process(self, environment):
        pass

    
