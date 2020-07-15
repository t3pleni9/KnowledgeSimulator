from .behavior import Behavior

class State:
    WAIT = None
    NILL = None
    
    def __init__(self, behavior, agent, args=None, timeout=1):
        self.behavior = behavior
        self.agent = agent
        self.args = args
        self.timeout = timeout if timeout is not None else 1
    
    def __call__(self, simulator):
        def perform_task(next_state, simulator):
            yield simulator.env.process(next_state(simulator))
            
        agent = yield simulator.agents.get(lambda t: t == self.agent)
        next_state = Behavior.perform(self.behavior, agent, self.args)
        waiting = ""

        now = simulator.env.now    
        if next_state == State.NILL:
            simulator.agents.put(agent)
            return None
        
        if next_state == State.WAIT:
            simulator.agents.put(agent)
            yield simulator.env.timeout(self.timeout)
            next_state = [self]
            print(f"{now} Waiting {self.agent.name} {self.behavior.name} {self.args}" )

        else:
            yield simulator.env.timeout(self.timeout)
            simulator.agents.put(agent)
            print(f"{now} Simulating  {self.agent.name} {self.behavior.name} {self.args} {self.timeout} secs" )
            with open("log.csv", "a+") as f:
                f.write(f"{now},{self.agent.name},{self.behavior.name},{self.args},{self.timeout}\n")
        
        for state in next_state:
            simulator.env.process(perform_task(state, simulator))


State.WAIT = State(None, None)
