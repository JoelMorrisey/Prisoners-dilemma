import random
from deap import base, creator, tools
# 1 => defect
# 0 => comply
def payoff_to_ind1(individual1, individual2, game):
    BothDefect = 1;
    DeflectComply = 5;
    ComplyDefect = 0;
    BothComply = 3;
    #change game type
    if game == "GC":
        BothDefect = BothDefect-1;
        ComplyDefect = ComplyDefect+1;
        
    
    if individual1[-1] == individual2[-1]:
        if individual1[-1] == 1:
            return BothDefect
        return BothComply
    
    if individual1[-1] == 1:
        return DeflectComply
    return ComplyDefect

def move_by_ind1(individual1, individual2, round):
    strate = 0
    if round >= 1:
        strate = strate + (individual1[-1] * 1)
        strate = strate + (individual2[-1] * 2)
        strate = strate + 1
        if  round >= 2:
            strate = strate + (individual1[-2] * 4)
            strate = strate + (individual2[-2] * 8)
            strate = strate + 3
    return individual1[strate]

def process_move(individual, move, memory_depth):
    if memory_depth <= 0 or memory_depth > len(individual):
        return False
    del individual[-memory_depth]
    individual.append(move)
    return True

#create a way to allow individuals to fight
def fight(individual1, individual2, num_of_games, game, memory_depth):
    totalP1 = 0
    totalP2 = 0
    for x in range(num_of_games):
        moveP1 = move_by_ind1(individual1, individual2, x)
        moveP2 = move_by_ind1(individual2, individual1, x)
        process_move(individual1, moveP1, memory_depth)
        process_move(individual2, moveP2, memory_depth)
        totalP1 = totalP1 + payoff_to_ind1(individual1, individual2, game)
        totalP2 = totalP2 + payoff_to_ind1(individual2, individual1, game)
    return (totalP1,), (totalP2,)

def populationFight(toolbox, population):
    for x in population:
        x.fitness = (0,)
    for p1 in range(len(population)-1):
        for p2 in population[p1+1:]:
            P1score, P2score = toolbox.fight(population[p1], p2)
            population[p1].fitness = (population[p1].fitness[0] + P1score[0],)
            p2.fitness = (p2.fitness[0] + P2score[0],)

# Create the toolbox with the right parameters
def create_toolbox(num_of_bits, num_of_games, game_type, memory_depth):
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMax)
    
    # Initialize the toolbox
    toolbox = base.Toolbox()
    
    # Generate attributes 
    toolbox.register("attr_bool", random.randint, 0, 1)
    
    # Initialize structures
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_bool, num_of_bits)
    
    # Define the population to be a list of individuals
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    
    # Define the fighting method
    toolbox.register("fight", fight, num_of_games=num_of_games, game=game_type, memory_depth=memory_depth)
        
    toolbox.register("populationFight", populationFight, toolbox)
    
    # Register the evaluation operator 
    toolbox.register("payoff", payoff_to_ind1, game=game_type)

    # Register the crossover operator
    toolbox.register("mate", tools.cxTwoPoint)

    # Register a mutation operator
    toolbox.register("mutate", tools.mutFlipBit, indpb=0.5)

    # Operator for selecting individuals for breeding
    toolbox.register("select", tools.selTournament, tournsize=3, fit_attr='fitness')
    
    return toolbox

def runGeneticGame(gameType, number_of_games = 136, memory_depth = 2, populationSize=100, num_generations = 100
                   , probab_crossing=0.5, probab_mutating = 0.2):
    #create toolbox
    toolbox = create_toolbox((2**(memory_depth*2))+(2**memory_depth)+memory_depth+1, number_of_games, 
                             gameType, memory_depth)
    #create population
    population = toolbox.population(n=populationSize)
    
    for g in range(num_generations):
        print("\n===== Generation", g)
        #make everyone fight and give them a fitness based on there preformance
        toolbox.populationFight(population)

        # -----
        # print out all the information about this generation
        # -----
        # Gather all the fitnesses in one list and print the stats
        fits = [] # collect all fitnessses
        bestPerson = population[0] #best player
        uniqueFitnesses = [] # unique fitnesses
        unique = [] # unique players
        for x in population:
            fits.append(x.fitness[0])
            if x.fitness[0] not in uniqueFitnesses:
                uniqueFitnesses.append(x.fitness[0])
            if x not in unique:
                unique.append(x)
            if x.fitness[0] > bestPerson.fitness[0]:
                bestPerson = x
            
        length = len(population)
        mean = sum(fits) / length
        sum2 = sum(x*x for x in fits)
        std = abs(sum2 / length - mean**2)**0.5
        
        print("unique players = ", len(unique) ,", unique fitnesses = ", len(uniqueFitnesses))
        print('Min =', min(fits), ', Max =', max(fits))
        print('Average =', round(mean, 2), ', Standard deviation =', round(std, 2))
        
        print("bestPerson:",bestPerson)
        
        # -----
        # Produce offspring and set that as the population
        # -----
        offspring = toolbox.select(population, len(population))
        
        # Clone the selected individuals
        offspring = list(map(toolbox.clone, offspring))
        
        #preform the crossover
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            # Cross two individuals
            if random.random() < probab_crossing:
                toolbox.mate(child1, child2)
        
        # Apply mutation
        for mutant in offspring:
            # Mutate an individual
            if random.random() < probab_mutating:
                toolbox.mutate(mutant)
        
        offspring[0] = bestPerson #place best child into new generation
        population = offspring
        
        #remove all the fitness values      
        for x in population:
            x.fitness = (0,)
            del x.fitness


runGeneticGame("PD")
#runGeneticGame("GC") #uncomment this line to do GC and comment line above

