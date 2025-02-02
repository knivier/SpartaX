import pygame

class CharacterSprite(pygame.sprite.Sprite):
    def __init__(self, image_paths, pos, animation_speed=0.1):
        """
        image_paths: List of paths to images representing animation frames.
        pos: Initial position of the sprite.
        animation_speed: Controls the speed of the animation.
        """
        super().__init__()
        self.frames = [pygame.image.load(img).convert_alpha() for img in image_paths]
        self.current_frame = 0
        self.animation_speed = animation_speed
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(center=pos)
        self.animation_timer = 0  # Track animation time

    def update(self, delta_time):
        # Update animation based on elapsed time
        self.animation_timer += delta_time
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]

    def reset_animation(self):
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
