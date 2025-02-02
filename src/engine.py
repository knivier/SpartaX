import time
import random
import pygame
from Player_List import (
    Draco,
    Hydra,
    Phoenix,
    Lyra,
    Orion,
    Pegasus,
    Andromeda,
    Centaurus,
    Cassiopeia,
)
# from imaging import scan, to_window
import imaging
import yaml
import os
import cv2  # For color conversion

# Ensure Pygame is initialized before anything else
pygame.init()
pygame.font.init()  # Explicitly initialize the font module

# Game Constants
ROUND_TIME = 60  # Total time for the entire battle (seconds)
TURN_TIME = 5  # Each turn lasts 5 seconds


def calculate_defense_efficiency():
    """Return a tuple (fully_efficient, reduction).
    - fully_efficient is True 50% of the time.
    - If not fully efficient, reduction is between 40% and 80% (as a fraction)."""
    fully_efficient = random.choice([True, False])
    reduction = random.uniform(0.4, 0.8)
    return fully_efficient, reduction


class LogWindow:
    def __init__(self, rect):
        """
        rect: pygame.Rect defining where the log is drawn on the GUI surface.
        """
        if not pygame.get_init():
            pygame.init()
        self.rect = rect
        self.font = pygame.font.Font(None, 24)
        self.messages = []
        self.max_lines = 20

    def add_message(self, message):
        self.messages.append(message)
        if len(self.messages) > self.max_lines:
            self.messages.pop(0)

    def update(self, surface):
        if not pygame.get_init():
            pygame.init()
        # Draw a background for the log area.
        pygame.draw.rect(surface, (30, 30, 30), self.rect)
        y = self.rect.y + 10
        for message in self.messages:
            text_surface = self.font.render(message, True, (255, 255, 255))
            surface.blit(text_surface, (self.rect.x + 10, y))
            y += 30


class GameEngine:
    def __init__(self, player1, player2):
        if not pygame.get_init():
            pygame.init()
        self.player1 = player1
        self.player2 = player2
        # Create a display of 1368x720.
        self.screen = pygame.display.set_mode((1368, 720))
        pygame.display.set_caption("Wizard Duel")
        self.clock = pygame.time.Clock()
        self.running = True

        # Set up a dedicated GUI surface for the right half.
        # Right half occupies x = 684 to 1368.
        self.gui_surface = pygame.Surface((684, 720))
        # Positions for health/mana bars (relative to the GUI surface).
        self.p1_health_rect = pygame.Rect(16, 50, 200, 20)
        self.p1_mana_rect = pygame.Rect(16, 80, 200, 20)
        self.p2_health_rect = pygame.Rect(16, 150, 200, 20)
        self.p2_mana_rect = pygame.Rect(16, 180, 200, 20)
        # Log window area on the GUI surface.
        self.log_rect = pygame.Rect(16, 250, 652, 400)
        self.log_window = LogWindow(self.log_rect)

    def update_camera_view(self):
        """
        Update the left half of the window with the latest camera frame.
        Assumes that imaging.to_window (global) is a BGR numpy array.
        """
        if not pygame.get_init():
            pygame.init()
        try:
            if imaging.to_window is not None:
                # Convert BGR to RGB.
                frame_rgb = cv2.cvtColor(imaging.to_window, cv2.COLOR_BGR2RGB)
                # Create a Pygame surface from the numpy array.
                frame_surface = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))
                # Scale frame to fill the left half (684x720).
                frame_surface = pygame.transform.scale(frame_surface, (684, 720))
                self.screen.blit(frame_surface, (0, 0))
            else:
                pygame.draw.rect(self.screen, (0, 0, 0), (0, 0, 684, 720))
        except pygame.error:
            pass

    def update_gui(self):
        """
        Draw the GUI on the right half: background, health/mana bars, and log window.
        """
        if not pygame.get_init():
            pygame.init()

        self.gui_surface.fill((50, 50, 50))
        # Draw health/mana bars for player1.
        p1_health_width = int((self.player1.get_health() / 100) * 200)
        pygame.draw.rect(
            self.gui_surface,
            (255, 0, 0),
            (
                self.p1_health_rect.x,
                self.p1_health_rect.y,
                p1_health_width,
                self.p1_health_rect.height,
            ),
        )
        p1_mana_width = int((self.player1.get_mana() / 100) * 200)
        pygame.draw.rect(
            self.gui_surface,
            (0, 0, 255),
            (
                self.p1_mana_rect.x,
                self.p1_mana_rect.y,
                p1_mana_width,
                self.p1_mana_rect.height,
            ),
        )
        # Draw health/mana bars for player2.
        p2_health_width = int((self.player2.get_health() / 100) * 200)
        pygame.draw.rect(
            self.gui_surface,
            (255, 0, 0),
            (
                self.p2_health_rect.x,
                self.p2_health_rect.y,
                p2_health_width,
                self.p2_health_rect.height,
            ),
        )
        p2_mana_width = int((self.player2.get_mana() / 100) * 200)
        pygame.draw.rect(
            self.gui_surface,
            (0, 0, 255),
            (
                self.p2_mana_rect.x,
                self.p2_mana_rect.y,
                p2_mana_width,
                self.p2_mana_rect.height,
            ),
        )
        # Update log window on the GUI surface.
        self.log_window.update(self.gui_surface)
        # Blit the GUI surface onto the right half of the main screen.
        self.screen.blit(self.gui_surface, (684, 0))

    def log(self, message):
        """Add a message to the log window."""
        self.log_window.add_message(message)

    def process_round_moves(self, move1, move2):
        """
        Process both players' moves concurrently.
        move1: move chosen by player1 ("Attack", "Defending", "Resting")
        move2: move chosen by player2 ("Attack", "Defending", "Resting")
        """
        # Process player1's move.
        if move1 == "Attack":
            if self.player1.get_mana() >= 20:
                self.player1.set_mana(self.player1.get_mana() - 20)
                if move2 == "Defending":
                    damage = self.player1.get_attack() - self.player2.get_defense()
                    if damage < 0:
                        damage = 0
                    fully_efficient, reduction = calculate_defense_efficiency()
                    if fully_efficient:
                        damage = 0
                        self.log(
                            f"{self.player2.get_name()} defended fully against {self.player1.get_name()}'s attack!"
                        )
                    else:
                        damage = int(damage * (1 - reduction))
                        self.log(
                            f"{self.player2.get_name()} defended inefficiently, reducing damage by {int(reduction * 100)}%!"
                        )
                elif move2 == "Resting":
                    damage = int(self.player1.get_attack() * 1.5)
                elif move2 == "Attack":
                    damage = self.player1.get_attack()
                else:
                    damage = self.player1.get_attack()
                self.player2.set_health(self.player2.get_health() - damage)
                self.log(
                    f"{self.player1.get_name()} attacks {self.player2.get_name()} for {damage} damage!"
                )
            else:
                self.log(
                    f"{self.player1.get_name()} tried to attack but didn't have enough mana!"
                )
        elif move1 == "Defending":
            if self.player1.get_mana() >= 20:
                self.player1.set_mana(self.player1.get_mana() - 20)
                self.log(f"{self.player1.get_name()} is defending this turn!")
            else:
                self.log(
                    f"{self.player1.get_name()} tried to defend but didn't have enough mana!"
                )
        elif move1 == "Resting":
            mana_gain = random.randint(20, 35)
            self.player1.set_mana(self.player1.get_mana() + mana_gain)
            self.log(f"{self.player1.get_name()} rests and gains {mana_gain} mana!")

        # Process player2's move.
        if move2 == "Attack":
            if self.player2.get_mana() >= 20:
                self.player2.set_mana(self.player2.get_mana() - 20)
                if move1 == "Defending":
                    damage = self.player2.get_attack() - self.player1.get_defense()
                    if damage < 0:
                        damage = 0
                    fully_efficient, reduction = calculate_defense_efficiency()
                    if fully_efficient:
                        damage = 0
                        self.log(
                            f"{self.player1.get_name()} defended fully against {self.player2.get_name()}'s attack!"
                        )
                    else:
                        damage = int(damage * (1 - reduction))
                        self.log(
                            f"{self.player1.get_name()} defended inefficiently, reducing damage by {int(reduction * 100)}%!"
                        )
                elif move1 == "Resting":
                    damage = int(self.player2.get_attack() * 1.5)
                elif move1 == "Attack":
                    damage = self.player2.get_attack()
                else:
                    damage = self.player2.get_attack()
                self.player1.set_health(self.player1.get_health() - damage)
                self.log(
                    f"{self.player2.get_name()} attacks {self.player1.get_name()} for {damage} damage!"
                )
            else:
                self.log(
                    f"{self.player2.get_name()} tried to attack but didn't have enough mana!"
                )
        elif move2 == "Defending":
            if self.player2.get_mana() >= 20:
                self.player2.set_mana(self.player2.get_mana() - 20)
                self.log(f"{self.player2.get_name()} is defending this turn!")
            else:
                self.log(
                    f"{self.player2.get_name()} tried to defend but didn't have enough mana!"
                )
        elif move2 == "Resting":
            mana_gain = random.randint(20, 35)
            self.player2.set_mana(self.player2.get_mana() + mana_gain)
            self.log(f"{self.player2.get_name()} rests and gains {mana_gain} mana!")

    def battle_round(self):
        """
        Main battle loop.
        For every TURN_TIME seconds, imaging.scan() is used to get both players' moves.
        The moves are processed, and both the camera view and GUI are updated.
        """

        #     # Get moves from imaging.scan (blocks for TURN_TIME seconds).
        move_p1, move_p2 = imaging.scan(TURN_TIME, False)
        self.log(
            f"Moves this turn: {self.player1.get_name()} -> {move_p1}, {self.player2.get_name()} -> {move_p2}"
        )

        self.process_round_moves(move_p1, move_p2)

        # Update display: left half (camera) and right half (GUI).
        self.update_camera_view()
        self.update_gui()
        pygame.display.update()
        self.clock.tick(30)

    def declare_winner(self):
        if not pygame.get_init():
            pygame.init()
        if self.player1.get_health() > self.player2.get_health():
            self.log(f"{self.player1.get_name()} wins!")
        elif self.player2.get_health() > self.player1.get_health():
            self.log(f"{self.player2.get_name()} wins!")
        else:
            self.log("It's a draw!")
        # Keep the window open after the game ends until the user quits.
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
            self.update_camera_view()
            self.update_gui()
            pygame.display.update()
            self.clock.tick(30)
    
    def gameOver(self):
        if self.player1.get_health() <= 0 or self.player2.get_health() <= 0:
            return True
        return False


def run():
    if not pygame.get_init():
        pygame.init()
    # Load configuration from YAML.
    yaml_path = os.path.join(os.path.dirname(__file__), "../properties.yaml")
    with open(yaml_path, "r") as file:
        properties = yaml.safe_load(file)

    player1_name = properties.get("game_options", {}).get("player1", {}).get("name")
    player2_name = properties.get("game_options", {}).get("player2", {}).get("name")
    if player1_name is None:
        raise ValueError("player1 is not specified in properties.yaml")
    if player2_name is None:
        raise ValueError("player2 is not specified in properties.yaml")

    player_classes = {
        "Draco": Draco,
        "Hydra": Hydra,
        "Phoenix": Phoenix,
        "Lyra": Lyra,
        "Orion": Orion,
        "Pegasus": Pegasus,
        "Andromeda": Andromeda,
        "Centaurus": Centaurus,
        "Cassiopeia": Cassiopeia,
    }
    p1_class = player_classes.get(player1_name)
    p2_class = player_classes.get(player2_name)
    if p1_class is None:
        raise ValueError(f"Unknown player1: {player1_name}")
    if p2_class is None:
        raise ValueError(f"Unknown player2: {player2_name}")

    game = GameEngine(p1_class(), p2_class())
    # game.battle_round()
    while not game.gameOver():
        game.battle_round()
        
    game.declare_winner()
    


if __name__ == "__main__":
    run()
