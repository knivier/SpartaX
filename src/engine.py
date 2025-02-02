import time
import random
import pygame
from Player_List import Draco, Hydra, Phoenix, Lyra, Orion, Pegasus, Andromeda, Centaurus, Cassiopeia
from imaging import scan
import yaml
import os

ROUND_TIME = 60  # Each round lasts 60 seconds
TURN_TIME = 5  # Each player has 5 seconds per attack

pygame.init()

def calculate_defense():
    return random.randint(1, 2) == 1, random.randint(40, 80) / 100

def calculate_rest():
    return random.randint(20, 35)

class GameEngine:
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Wizard Duel")
        self.clock = pygame.time.Clock()
        self.running = True
        self.setup_gui()
    
    def setup_gui(self):
        self.health_bars = {
            self.player1: pygame.Rect(50, 50, 200, 20),
            self.player2: pygame.Rect(550, 50, 200, 20)
        }
        self.mana_bars = {
            self.player1: pygame.Rect(50, 80, 200, 20),
            self.player2: pygame.Rect(550, 80, 200, 20)
        }
    
    def update_gui(self):
        self.screen.fill((0, 0, 0))
        for player in [self.player1, self.player2]:
            health_bar = self.health_bars[player]
            mana_bar = self.mana_bars[player]
            health_width = int((player.health / 100) * 200)
            mana_width = int((player.mana / 100) * 200)
            pygame.draw.rect(self.screen, (255, 0, 0), (health_bar.x, health_bar.y, health_width, health_bar.height))
            pygame.draw.rect(self.screen, (0, 0, 255), (mana_bar.x, mana_bar.y, mana_width, mana_bar.height))
        pygame.display.flip()
    
    def battle_round(self):
        start_time = time.time()
        while time.time() - start_time < ROUND_TIME and self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            
            move_p1, move_p2 = scan(TURN_TIME, False)
            self.process_move(self.player1, self.player2, move_p1)
            self.process_move(self.player2, self.player1, move_p2)
            self.update_gui()
            
            if self.player1.health <= 0 or self.player2.health <= 0:
                break
            
            self.clock.tick(30)
        
        self.declare_winner()
    
    def process_move(self, attacker, defender, move):
        if move == "Attack":
            if attacker.mana >= 20:
                attacker.mana -= 20
                damage = attacker.attack - defender.defense
                if damage > 0:
                    if defender.current_action == "Resting":
                        damage = int(damage * 1.5)
                    defender.health -= damage
                    print(f"{attacker.name} attacks {defender.name} for {damage} damage!")
        elif move == "Defending":
            efficient, reduction = calculate_defense()
            if attacker.mana >= 20:
                attacker.mana -= 20
                if efficient:
                    attacker.defense *= reduction
                    print(f"{attacker.name} is defending efficiently, reducing damage by {int(reduction * 100)}%!")
        elif move == "Resting":
            heal = calculate_rest()
            attacker.health += heal
            print(f"{attacker.name} rests and heals {heal} HP!")
    
    def declare_winner(self):
        if self.player1.health > self.player2.health:
            print(f"{self.player1.name} wins!")
        elif self.player2.health > self.player1.health:
            print(f"{self.player2.name} wins!")
        else:
            print("It's a draw!")
    
if __name__ == "__main__":
    yaml_path = os.path.join(os.path.dirname(__file__), '../properties.yaml')
    with open(yaml_path, 'r') as file:
        properties = yaml.safe_load(file)

    player1_name = properties.get('game_options', {}).get('player1', {}).get('name')
    player2_name = properties.get('game_options', {}).get('player2', {}).get('name')

    if player1_name is None:
        raise ValueError("player1 is not specified in properties.yaml")
    if player2_name is None:
        raise ValueError("player2 is not specified in properties.yaml")

    if player1_name == "Draco":
        player1 = Draco()
    elif player1_name == "Hydra":
        player1 = Hydra()
    elif player1_name == "Phoenix":
        player1 = Phoenix()
    elif player1_name == "Lyra":
        player1 = Lyra()
    elif player1_name == "Orion":
        player1 = Orion()
    elif player1_name == "Pegasus":
        player1 = Pegasus()
    elif player1_name == "Andromeda":
        player1 = Andromeda()
    elif player1_name == "Centaurus":
        player1 = Centaurus()
    elif player1_name == "Cassiopeia":
        player1 = Cassiopeia()
    else:
        raise ValueError(f"Unknown player1: {player1_name}")

    if player2_name == "Draco":
        player2 = Draco()
    elif player2_name == "Hydra":
        player2 = Hydra()
    elif player2_name == "Phoenix":
        player2 = Phoenix()
    elif player2_name == "Lyra":
        player2 = Lyra()
    elif player2_name == "Orion":
        player2 = Orion()
    elif player2_name == "Pegasus":
        player2 = Pegasus()
    elif player2_name == "Andromeda":
        player2 = Andromeda()
    elif player2_name == "Centaurus":
        player2 = Centaurus()
    elif player2_name == "Cassiopeia":
        player2 = Cassiopeia()
    else:
        raise ValueError(f"Unknown player2: {player2_name}")

    game = GameEngine(player1, player2)
    game.battle_round()
    pygame.quit()