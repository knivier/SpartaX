import random 
import pygame

class Particle:
    def __init__(self, pos, velocity, color, size, lifespan):
        self.pos = list(pos)
        self.velocity = velocity
        self.color = color
        self.size = size
        self.lifespan = lifespan
        self.age = 0

    def update(self):
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]
        self.age += 1
        self.size = max(0, self.size - 0.1)  

    def is_dead(self):
        return self.age >= self.lifespan or self.size <= 0

    def draw(self, surface):
        if self.size > 0:
            pygame.draw.circle(surface, self.color, (int(self.pos[0]), int(self.pos[1])), int(self.size))


class ParticleEffect:
    def __init__(self, pos, target_pos, num_particles, color, max_lifespan=30):
        self.particles = [
            Particle(
                pos=pos,
                velocity=(
                    random.uniform((target_pos[0] - pos[0]) * 0.01, (target_pos[0] - pos[0]) * 0.02),
                    random.uniform((target_pos[1] - pos[1]) * 0.01, (target_pos[1] - pos[1]) * 0.02),
                ),
                color=color,
                size=random.uniform(3, 6),
                lifespan=random.randint(max_lifespan // 2, max_lifespan)
            )
            for _ in range(num_particles)
        ]

    def update(self):
        self.particles = [particle for particle in self.particles if not particle.is_dead()]
        for particle in self.particles:
            particle.update()

    def draw(self, surface):
        for particle in self.particles:
            particle.draw(surface)