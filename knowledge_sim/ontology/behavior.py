class Behavior:
    __behaviors = {}

    @classmethod
    def add(cls, uri, function):
        cls.__behaviors[uri] = Behavior(function)
    
    @classmethod
    def sync(cls, simulator):
        reasoner = simulator.reasoner
        reasoner.sync_reasoner()
        uri_property = simulator.uri_property
        behavior_class = simulator.behavior_class
        for behavior in behavior_class.instances():
            uri = getattr(behavior, uri_property)
            api_behavior = cls.__behaviors.get(uri, None)

            if api_behavior is not None:
                api_behavior.simulator = simulator
                cls.__behaviors[behavior] = api_behavior

    @classmethod
    def perform(cls, behavior, agent, task):
        api_behavior = cls.__behaviors.get(behavior)
        if api_behavior is None:
            return None

        return api_behavior(agent, task, behavior=behavior)

    def __init__(self, function):
        self.function = function
        self.simulator = None

    def __call__(self, *args, **kwargs):
        return self.function(
            simulator=self.simulator,
            *args, **kwargs
        )

