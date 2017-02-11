from graphics import *
from math import *
from noise import pnoise1
from time import sleep
from random import random, uniform, randrange, choices
from vector import Vector

FRAME_RATE = 120
POPULATION = 10
NUMBER_OBSTACLES = 5
GRAVITY_FACTOR = 0.05
MUTATION_RATE = 0.25
LIFE_GENE_RATIO = 10


class Obstacle:
    def __init__(self, pos_x, pos_y, radius):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.radius = radius
        self.drawing = Circle(Point(self.pos_x, self.pos_y), radius)
        self.drawing.setFill("red")

    def render(self, window):
        self.drawing.draw(window)


class Target:
    def __init__(self, pos_x, pos_y, radius):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.radius = radius
        self.drawing = Circle(Point(self.pos_x, self.pos_y), radius)

    def render(self, window):
        self.drawing.draw(window)


class Bubble:
    def __init__(self, pos_x, pos_y, velocity_mag, lifespan, target, obstacles=None, dna=None):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.velocity = velocity_mag
        self.drawing = Circle(Point(self.pos_x, self.pos_y), 3)
        self.lifespan = lifespan
        self.target = target
        self.dead = False
        self.hit_object = False
        self.hit_target = False
        self.obstacles = obstacles
        if not dna:
            self.dna = DNA(self.lifespan / LIFE_GENE_RATIO).genes
        else:
            self.dna = dna

    def render(self, window):
        self.drawing.draw(window)

    def update(self, window):
        if not self.dead:
            if self.lifespan > 0:
                self.lifespan -= 1
                index = (len(self.dna) * LIFE_GENE_RATIO - self.lifespan) - 1
                self.velocity -= GRAVITY_FACTOR
                self.apply_force([Vector.from_angle(self.dna[index // LIFE_GENE_RATIO], self.lifespan / 40),
                                                    Vector(0, min(self.velocity, 10))])

            elif self.lifespan <= 0:
                self.die()
            if self.pos_x > window.width + 3 or self.pos_x < 0 - 3:
                # leaves screen to right or left
                self.hit_object = True
                self.die()
            if hypot(self.target.pos_x - self.pos_x, self.target.pos_y - self.pos_y) < 10:
                # enter a 10 pixel radius of the target
                self.hit_target = True
                self.die()
            for obstacle in self.obstacles:
                if hypot(obstacle.pos_x - self.pos_x, obstacle.pos_y - self.pos_y) < obstacle.radius:
                    # enter a 10 pixel radius of the obstacle
                    self.hit_object = True
                    self.die()

    def apply_force(self, forces):
        change_vector = Vector()
        for force in forces:
            change_vector += force
        self.drawing.move(change_vector.x, -change_vector.y)
        self.pos_x = self.drawing.getCenter().getX()
        self.pos_y = self.drawing.getCenter().getY()

    def die(self):
        self.dead = True
        self.drawing.undraw()
        # begin fitness calculation
        if self.hit_object:
            # penalty for hitting an object
            multiplier = 0.5
        elif self.hit_target:
            # bonus for reaching the target
            multiplier = 2
        else:
            multiplier = 1
        distance = hypot(self.target.pos_x - self.pos_x, self.target.pos_y - self.pos_y)
        self.fitness = ((1 / distance) * 1000 * multiplier)


class DNA:
    # future task: implement as emulated list type
    def __init__(self, size, genes=None):
        # size is the number of genes in the DNA - could be the lifespan of the bubble, or some fraction?
        # genes is a list of angles or headings
        if genes:
            self.genes = genes
            self.size = len(self.genes)
        else:
            self.size = int(size)
            noise_seed = uniform(0, 1024)
            heading_seed = uniform(1/3, 2/3)
            self.genes = [(pnoise1((x / 7) + noise_seed) + 1) * (pi * heading_seed) for x in range(self.size)]

    def __add__(self, other):
        # this is where we splice together two DNA gene sets
        length = self.size
        # spliced genes are a simple mean of matching elements
        # spliced_genes = [sum(gene) / len(gene) for gene in zip(self.genes, other.genes)]
        # another option that just randomly selects genes between the two parents
        spliced_genes = [gene[round(random())] for gene in zip(self.genes, other.genes)]
        return DNA(length, spliced_genes)

    def mutate(self, mutation_rate):
       for index, gene in enumerate(self.genes):
            if random() < mutation_rate:
                self.genes[index] += uniform(-0.75, 0.75)

def mate_and_mutate(population):
    fitnesses = [item.fitness for item in population]
    dnas = [item.dna for item in population]
    children = []
    for n in range(len(population)):
        parents = choices(dnas, weights=fitnesses, k=2)
        child = DNA(len(parents[0]), parents[0]) + DNA(len(parents[1]), parents[1])
        child.mutate(MUTATION_RATE)
        children.append(child)
    return children

def main():
    window = GraphWin(width=600, height=400)
    target = None
    bubbles = []
    obstacles = []
    for i in range(1000):
        hit_obs = 0
        hit_targ = 0
        if i % 100 == 0:
            if obstacles:
                for obstacle in obstacles:
                    obstacle.drawing.undraw()
            obstacles = [Obstacle(randrange(0, window.width), randrange(0, window.height), randrange(5, 25)) for x in
                         range(NUMBER_OBSTACLES)]
            for obstacle in obstacles:
                obstacle.render(window)
            if target:
                target.drawing.undraw()
            target = Target(randrange(150, 450), randrange(10, 150), 10)
            target.render(window)
        if not bubbles:
            # first generation
            bubbles = [Bubble(window.width / 2, window.height - 15, 3, 220, target, obstacles) for x in range(POPULATION)]
        else:
            # all subsequent generations
            next_gen = mate_and_mutate(bubbles)
            bubbles = [Bubble(window.width / 2 + uniform(-x, x), window.height - 15, 3, 250, target, obstacles, next_gen[x].genes) for x in range(POPULATION)]
        for bubble in bubbles:
            bubble.render(window)
        while not all([bubble.dead for bubble in bubbles]):
            for bubble in bubbles:
                bubble.update(window)
            sleep(1 / FRAME_RATE)
        for bubble in bubbles:
            if bubble.hit_object:
                hit_obs += 1
            if bubble.hit_target:
                hit_targ += 1
        print(f'Generation: {i}')
        print(f'Died on obstacle or edge: {hit_obs}')
        print(f'Made it to target: {hit_targ}')

    sleep(3)
    window.close()

if __name__ == "__main__":
    main()
