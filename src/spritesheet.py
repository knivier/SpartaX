import pygame

class SpriteManager:
    def __init__(self):
        self.sprite_sheet = pygame.image.load('spritesheet.png').convert_alpha()
        self.character_sprites = {
            'Centaurus': {'x': 0, 'y': 0},
            'Pegasus': {'x': 0, 'y': 1},
            'Phoenix': {'x': 0, 'y': 2},
            'Dragon': {'x': 0, 'y': 3}
        }
        self.sprite_size = 24  # Size of each sprite frame
        
    def get_sprite(self, character_name, action):
        if character_name not in self.character_sprites:
            return None
            
        char_pos = self.character_sprites[character_name]
        action_frames = {
            'Idle': 0,
            'Attack': 1,
            'Defend': 2,
            'Special': 3
        }
        
        x = char_pos['x'] + (action_frames.get(action, 0) * self.sprite_size)
        y = char_pos['y'] * self.sprite_size
        
        sprite = pygame.Surface((self.sprite_size, self.sprite_size), pygame.SRCALPHA)
        sprite.blit(self.sprite_sheet, (0, 0), (x, y, self.sprite_size, self.sprite_size))
        return pygame.transform.scale(sprite, (72, 72))  # Scale up for display
