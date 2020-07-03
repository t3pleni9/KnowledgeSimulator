from .behavior import Behavior
class State:
    def __init__(self, behavior, agent, args=None, timeout=1):
        self.behavior = behavior
        self.agent = agent
        self.args = args
        self.timeout = timeout
    
    def __call__(self, simulator):
        print(f"{simulator.env.now} Performable {self.behavior} {self.agent} {self.args} in progress for {self.timeout} secs" )

        agent = yield simulator.agents.get(lambda t: t == self.agent)

        return_value = Behavior.perform(self.behavior, self.agent, self.args)

        if return_value is not None:
            simulator.push([State(*args) for args in return_value])

        yield simulator.env.timeout(self.timeout)
        simulator.agents.put(agent)
    
    
