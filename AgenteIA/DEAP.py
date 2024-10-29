from deap import base, creator, tools, algorithms
import random
from AgenteIA.Agente import Agente

creator.create("FitnessMin", base.Fitness, weights=(-1.0,))  # Minimizar
creator.create("Individual", list, fitness=creator.FitnessMin)

class AgenteGenetico(Agente):

    def __init__(self, num_genes, rango_genes, prob_mutacion, prob_cruce):
        super().__init__()
        self.__num_genes = num_genes
        self.__rango_genes = rango_genes
        self.__prob_mutacion = prob_mutacion
        self.__prob_cruce = prob_cruce

        # Crear el toolbox de DEAP
        self.toolbox = base.Toolbox()
        self.toolbox.register("gene", random.uniform, self.__rango_genes[0], self.__rango_genes[1])
        self.toolbox.register("individual", tools.initRepeat, creator.Individual, self.toolbox.gene, n=self.__num_genes)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)

        # Registrar la función de evaluación
        self.toolbox.register("evaluate", self.calcular_fitness)
        self.toolbox.register("mate", tools.cxBlend, alpha=0.5)
        self.toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=1, indpb=0.2)
        self.toolbox.register("select", tools.selTournament, tournsize=3)

    def calcular_fitness(self, individual):
        # Logica de fitness  sumar los genes del individuo
        return (sum(individual),)  # DEAP espera una tupla

    def ejecutar_algoritmo(self, num_generaciones, tamano_poblacion):
        # Crear población inicial
        population = self.toolbox.population(n=tamano_poblacion)

        # Evaluar la población inicial
        fitnesses = list(map(self.toolbox.evaluate, population))
        for ind, fit in zip(population, fitnesses):
            ind.fitness.values = fit

        # Ciclo de evolucion
        for gen in range(num_generaciones):
            # Selección
            offspring = self.toolbox.select(population, len(population))
            offspring = list(map(self.toolbox.clone, offspring))

            # Cruzar y mutar
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if random.random() < self.__prob_cruce:
                    self.toolbox.mate(child1, child2)
                    del child1.fitness.values
                    del child2.fitness.values

            for mutant in offspring:
                if random.random() < self.__prob_mutacion:
                    self.toolbox.mutate(mutant)
                    del mutant.fitness.values

            # Evaluar la nueva población
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = map(self.toolbox.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit

            # Reemplazar la población
            population[:] = offspring

        # Retornar la mejor solucion
        return tools.selBest(population, 1)[0]