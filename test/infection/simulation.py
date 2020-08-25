from knowledge_sim import Simulator, State
from random import sample, random, randint

def get_next_tasks(task, agent=None):
    next_task = list(task.hasNextTask)[0]
    if agent is None:
        return [State(next_task.definedBy, agent, next_task, next_task.time_to_complete) for agent in list(next_task.assignedTo)]

    return [State(next_task.definedBy, agent, next_task, next_task.time_to_complete)]

@Simulator.behavior('api://epi_sim/behavior/checkHealth')
def check_health(citizen, task, simulator=None, *args, **kwargs):
    oo = simulator.ontology
    infected_contact = any([contact.healthState in [oo.infected, oo.deceased, oo.recovered] for contact in citizen.contacts])
    
    if citizen.healthState == oo.infected:
        citizen.survivebility -= task.time_to_complete

    if citizen.survivebility <= 0:
        citizen.healthState = oo.deceased
        print('citizen deceased: ', citizen.name)
    elif citizen.healthState == oo.infected and random() > 0.7: 
        citizen.healthState = oo.recovered
        print('citizen recovered: ', citizen.name)

    if citizen.healthState == oo.susceptible and infected_contact and random() > 0.4:
        citizen.healthState = oo.infected
        print('citizen infected: ', citizen.name)
    oo = simulator.ontology
    oo.save('./output.owl')

    simulator.sync_reasoner()
    return get_next_tasks(task, citizen)

@Simulator.behavior('api://epi_sim/behavior/goToWork')
def go_to_work(citizen, task, simulator=None, *args, **kwargs):
    behavior = kwargs['behavior']
    oo = simulator.ontology
    if citizen.healthState in [oo.deceased, oo.recovered] :
        return State.NILL

    citizen.currentlyIn = citizen.worksAt
    return [State(behavior.triggers, citizen, task, 1)]

@Simulator.behavior('api://epi_sim/behavior/goToHome')
def go_to_home(citizen, task, simulator=None, *args, **kwargs):
    behavior = kwargs['behavior']
    oo = simulator.ontology    
    if citizen.healthState in [oo.deceased, oo.recovered]:
        return State.NILL

    citizen.currentlyIn = citizen.staysAt    
    return [State(behavior.triggers, citizen, task, 1)]    

@Simulator.behavior('api://epi_sim/behavior/infectSomeContacts')
def infect_contacts(citizen, task, simulator=None, *args, **kwargs):
    behavior = kwargs['behavior']
    building  = citizen.currentlyIn
    oo = simulator.ontology
    oo.save('./output.owl')

    simulator.sync_reasoner()
    sample_size = 2 if len(building.currentlyHas) >= 2 else len(building.currentlyHas)
    for inmate in sample(building.currentlyHas, sample_size):
        if citizen != inmate:
            citizen.contacts.append(inmate)
        
    simulator.sync_reasoner()
    return [State(behavior.triggers, citizen, task, 1)]    

@Simulator.behavior('api://epi_sim/behavior/initializeSimulation')    
def initialize(simulator_agent, task, simulator=None, *args, **kwargs):
    oo = simulator.ontology
    citizens = oo.Citizen.instances()
    infected_citizens = sample(citizens, 2)

    for citizen in citizens:
        if citizen in infected_citizens:
            citizen.healthState = oo.infected
        else:
            citizen.healthState = oo.susceptible
            
        citizen.currentlyIn = citizen.staysAt
        citizen.survivebility = randint(12, 120)
        oo.task_go_to_work.assignedTo.append(citizen)
        oo.task_go_to_home.assignedTo.append(citizen)

    simulator.sync_reasoner()
    return get_next_tasks(task)
    
@Simulator.behavior('api://epi_sim/behavior/simulate')
def simulate(simulator_agent,  *args, **kwargs):
    behavior = kwargs['behavior']
    simulation = list(simulator_agent.simulates)[0]
    
    return [State(task.definedBy, simulator_agent, task) for task in list(simulation.hasTask)]

def main():
    Simulator.init(
        ontology_uri="./infect.owl",
        agent_class="Citizen",
        behavior_class="Behavior",
        uri_property="uri",
        simulator="simulator",
        simulate="simulate"
    )
    
    Simulator.run(until = 169)
    simulator = Simulator.get_instance()
    oo = simulator.ontology
    oo.save('./output.owl')
    print("Simulation Done...")


if __name__ == '__main__':
    main()
