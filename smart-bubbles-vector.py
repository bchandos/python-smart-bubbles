from graphics import *
from math import *
from noise import pnoise1
import time
from random import random, uniform,


FRAME_RATE = 60
POPULATION = 10
GRAVITY_FACTOR = 0.04
MUTATION_RATE = 0.05


class Vector:

    def __init__(self, x = 0.0, y = 0.0):
        self.x = x
        self.y = y

    @property
    def magnitude(self):
        return sqrt(self.x ** 2 + self.y ** 2)

    @property
    def angle(self):
        return atan2(self.y, self.x)

    @classmethod
    def from_angle(cls, angle, magnitude = 1):
        x = magnitude * cos(angle)
        y = magnitude * sin(angle)
        return cls(x, y)

    def __add__(self, other):
        x = self.x + other.x
        y = self.y + other.y
        return Vector(x, y)

    def __sub__(self, other):
        x = self.x + -other.x
        y = self.y + -other.y
        return Vector(x, y)

    def __str__(self):
        return f'Vector at ({self.x}, {self.y}), of magnitude {self.magnitude} and theta {self.angle}.'

               
class Target:

    def __init__(self, pos_x, pos_y, radius):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.radius = radius
        self.drawing = Circle(Point(self.pos_x, self.pos_y), radius)

    def render(self, window):
        self.drawing.draw(window)

        
class Bubble:
    
    def __init__(self, pos_x, pos_y, velocity, lifespan, target, dna=None):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.velocity = velocity
        self.drawing = Circle(Point(self.pos_x, self.pos_y), 3)
        self.lifespan = lifespan
        self.target = target
        self.dead = False
        self.hit_object = False
        self.hit_target = False
        if not dna:
            self.dna = DNA(self.lifespan).genes
        else:
            self.dna = dna
                
    def render(self, window):
        self.drawing.draw(window)
       
    def update(self, window):
        if not self.dead:
            if self.lifespan > 0:
                self.lifespan -= 1
                index = (len(self.dna) - self.lifespan) - 1
                self.apply_force([dna[index], gravity])

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

    def apply_force(self, forces):
        for force in forces:
            offset_x += self.velocity.x + force.x
            offset_y += self.velocity.y + force.y
        self.drawing.move(offset_x, offset_y)
        self.pos_x = self.drawing.getCenter().getX()
        self.pos_y = self.drawing.getCenter().getY()
        
    def die(self):
        self.dead = True
        self.drawing.undraw()
        # begin fitness calculation
        if self.hit_object:
            #penalty for hitting an object
            multiplier = 0.1
        elif self.hit_target:
            #bonus for reaching the target
            multiplier = 5
        else:
            multiplier = 1
        distance = hypot(self.target.pos_x - self.pos_x, self.target.pos_y - self.pos_y)
        self.fitness = (1 / distance) * 1000 * multiplier
        print(self.fitness)


class DNA:
    # future task: implement as emulated list type
    def __init__(self, size=None, genes=None):
        # size is the number of genes in the DNA - could be the lifespan of the bubble, or some fraaction?
        # genes is a list of angles or headings
        if genes:
            self.genes = genes
            self.size = len(self.genes)
        elif not size:
            self.genes = []
            self.size = 100 # default
        else:
            self.genes = []
            self.size = size
        # genes is the substance of DNA

    def __add__(self, other):
        # this is where we splice together two genes
        length = self.size
        # spliced genes are a simple mean of matching elements
        spliced_genes = [sum(gene) / len(gene) for gene in zip(self.genes, other.genes)]
        # another option that just randomly selects genes between the two parents
        # spliced_genes = [gene[round(random())] for gene in zip(self.genes, other.genes)]
        return DNA(length, spliced_genes)

    def mutate(self, mutation_rate):
        for index, gene in enumerate(self.genes):
            if random() < mutation_rate:
                self.genes[index] = gene + uniform(-1, 1)



def main():
    win = GraphWin(width = 600, height = 400) # create a window
    target = Target(300, 75, 10)
    target.render(win)
    bubbles = [Bubble(win.width/2, win.height + 15, 6, 225, target) for x in range(POPULATION)]
    for bubble in bubbles:
        bubble.render(win) 
    while not win.checkMouse():
        for bubble in bubbles:
            bubble.update(win)
        time.sleep(1/FRAME_RATE)
    while True:
        bubbles = [Bubble(win.width/2, win.height + 15, 6, 225, target, next_gen[x]) for x in range(POPULATION)]
        for bubble in bubbles:
            bubble.render(win) 
        while not all([b.dead for b in bubbles]):
            for bubble in bubbles:
                bubble.update(win)
            time.sleep(1/FRAME_RATE)
    win.close()

if __name__ == "__main__":
    main()

