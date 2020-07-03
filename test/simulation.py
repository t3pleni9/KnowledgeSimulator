from knowledge_sim import Simulator

def get_next_tasks(task):
    return [(next_task.definedBy, next_task.assignedTo, next_task, next_task.timeToComplete) for next_task in list(task.hasTask)]

@Simulator.behavior(api='definition.addToContainable')
def add_to_containable(manager, task, simulator=None, *args, **kwargs):
    ontology = simulator.ontology
    entity = task.entity
    setattr(entity, task.__params__, manager.manages[0])

    simulator.sync_reasoner()
    task.done = True

    return get_next_tasks(task)

@Simulator.behavior(api='definition.createAssembly')
def create_assembly(factory_manager, task, simulator=None, *args, **kwargs):
    ontology = simulator.ontology
    
    assembly_type = ontology[task.__params__]
    parts = task.parts

    assembly = assembly_type()
    for part in parts:
        part.partOf = assembly

    simulator.sync_reasoner()
    for next_tasks in task.hasTask:
        next_tasks.entity = assembly
    task.done = True
    return get_next_tasks(task)

@Simulator.behavior(api='definition.createBot')
def create_bot(factory_manager, task, simulator=None, *args, **kwargs):
    ontology = simulator.ontology
    
    bot_type = ontology[task.__params__]
    assemblies = task.assemblies

    bot = bot_type()
    for assembly in assemblies:
        assembly.assemblyOf = bot

    simulator.sync_reasoner()
    
    for next_tasks in task.hasTask:
        next_tasks.entity = bot
    task.done = True
    return get_next_tasks(task)


@Simulator.behavior(api='definition.fetchAssemblies')    
def fetchAssemblies(inventoryManager, task, simulator=None, *args, **kwargs):
    if task.done:
        return None
    queries = task.__query__
    namespace = task.__name_space__
    query_result = [simulator.reasoner.run_query(query, namespace) for query in queries]
    assemblies = [result[0] for results in query_result for result in results]
    
    for next_tasks in task.hasTask:
        next_tasks.assemblies = assemblies
    task.done = True
    return get_next_tasks(task)


@Simulator.behavior(api='definition.fetchParts')    
def fetchParts(inventoryManager, task, simulator=None, *args, **kwargs):
    queries = task.__query__
    namespace = task.__name_space__
    query_result = [simulator.reasoner.run_query(query, namespace) for query in queries]
    parts = [result[0] for results in query_result for result in results]
    
    for next_tasks in task.hasTask:
        next_tasks.parts = parts
    task.done = True
    return get_next_tasks(task)


def factory_manager_perform(actor, task, *args, **kwargs):
    return [(task.definedBy, task.assignedTo, task)]

def inventory_manager_perform(actor, task, *args, **kwargs):
    return [(task.definedBy, task.assignedTo, task)]

@Simulator.behavior(api='definition.perform')    
def perform(actor, executable, *args, **kwargs):
    agent_type = actor.is_a[0].name
    agent_perform = {
        'FactoryManager': factory_manager_perform,
        'InventoryManager': inventory_manager_perform
    }

    return agent_perform[agent_type](actor, executable)

def mother_ship_execute(agent, mission):
    return get_next_tasks(mission)

@Simulator.behavior(api='definition.execute')
def execute(actor, executable, *args, **kwargs):
    agent_type = actor.is_a[0].name
    agent_perform = {
        'Orchestrator': mother_ship_execute
    }
    
    return agent_perform[agent_type](actor, executable)

@Simulator.behavior(api='definition.assignExecutable')    
def assignExecutable(simulator_agent, simulation, *args, **kwargs):
    return [(mission.definedBy, mission.assignedTo, mission, mission.timeToComplete) for mission in list(simulation.hasMissions)]
    
@Simulator.behavior(api='definition.simulate')    
def simulate(simulator_agent,  *args, **kwargs):
    behavior = kwargs['behavior']
    return [(behavior.triggers[0], simulator_agent, simulation) for simulation in list(simulator_agent.simulates)]



def main():
    simulator = Simulator.get_instance(ontology_uri="./kb_owl.owl")
    simulator.run(until = 100)
    oo = simulator.ontology
    oo.save('/Users/in-justin.jose/temp2.owl')



if __name__ == '__main__':
    main()
