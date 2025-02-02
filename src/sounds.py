import pygame

class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {
            'Attack': pygame.mixer.Sound('src/sounds/attack.wav'),
            'Heal': pygame.mixer.Sound('src/sounds/heal.wav'),
            'Special': pygame.mixer.Sound('src/sounds/special.mp3')
        }
        
    def play_sound(self, action):
        if action in self.sounds:
            self.sounds[action].play()
