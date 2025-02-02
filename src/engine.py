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
import imaging
import yaml
import os
import cv2  # For color conversion
import logging
import time
import ai

# Ensure Pygame is initialized before anything else
pygame.init()
pygame.font.init()  # Explicitly initialize the font module

# Game Constants
ROUND_TIME = 60  # Total time for the entire battle (seconds)
TURN_TIME = 5  # Each turn lasts 5 seconds

# Set up logging
logging.basicConfig(
    filename="logs.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Log new session
logging.info(f"NEW SESSION ID: {time.time()}")


def calculate_defense_efficiency():
    """Return a tuple (fully_efficient, reduction).
    - fully_efficient is True 50% of the time.
    - If not fully efficient, reduction is between 40% and 80% (as a fraction)."""
    fully_efficient = random.choice([True, False])
    reduction = random.uniform(0.4, 0.8)
    logging.debug(
        f"Defense efficiency calculated: fully_efficient={fully_efficient}, reduction={reduction}"
    )
    return fully_efficient, reduction


class LogWindow:
    def __init__(self, rect):
        """
        rect: pygame.Rect defining where the log is drawn on the GUI surface.
        """
        self.rect = rect
        self.font = pygame.font.Font(None, 24)
        self.messages = []
        self.max_lines = 20
        logging.debug("LogWindow initialized")

    def add_message(self, message):
        self.messages.append(message)
        if len(self.messages) > self.max_lines:
            self.messages.pop(0)
        logging.debug(f"Message added to LogWindow: {message}")

    def update(self, surface):
        # Draw a background for the log area.
        pygame.draw.rect(surface, (30, 30, 30), self.rect)
        y = self.rect.y + 10
        for message in self.messages:
            text_surface = self.font.render(message, True, (255, 255, 255))
            surface.blit(text_surface, (self.rect.x + 10, y))
            y += 30
        logging.debug("LogWindow updated")


class GameEngine:
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        # Create a display of 1368x720.
        self.screen = pygame.display.set_mode((1368, 720))
        # self.screen = pygame.display.get_surface()
        # pygame.display.set_caption("Wizard Duel")
        self.clock = pygame.time.Clock()
        self.running = True

        # Set up a dedicated GUI surface for the right half.
        # Right half occupies x = 684 to 1368.
        self.gui_surface = pygame.Surface((1368 // 2, 720))
        # Positions for health/mana bars (relative to the GUI surface).
        self.p1_health_rect = pygame.Rect(16, 50, 200, 20)
        self.p1_mana_rect = pygame.Rect(16, 80, 200, 20)
        self.p2_health_rect = pygame.Rect(16, 150, 200, 20)
        self.p2_mana_rect = pygame.Rect(16, 180, 200, 20)
        # Log window area on the GUI surface.
        self.log_rect = pygame.Rect(16, 250, 652, 400)
        self.log_window = LogWindow(self.log_rect)
        logging.debug("GameEngine initialized")

    def update_camera_view(self):
        """
        Update the left half of the window with the latest camera frame.
        Assumes that imaging.to_window (global) is a BGR numpy array.
        """
        try:
            if imaging.to_window is not None:
                # Convert BGR to RGB.
                frame_rgb = cv2.cvtColor(imaging.to_window, cv2.COLOR_BGR2RGB)
                # Create a Pygame surface from the numpy array.
                frame_surface = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))
                # Scale frame to fill the left half (684x720).
                frame_surface = pygame.transform.scale(frame_surface, (684, 720))
                self.screen.blit(frame_surface, (0, 0))
                logging.debug("Camera view updated with new frame")
            else:
                pygame.draw.rect(self.screen, (0, 0, 0), (0, 0, 684, 720))
                logging.debug("Camera view updated with black screen")
        except pygame.error as e:
            logging.error(f"Pygame error in update_camera_view: {e}")

    def update_gui(self):
        """
        Draw the GUI on the right half: background, health/mana bars, and log window.
        """
        self.particle_effects = []
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
        # Draw player1's name above the health bar
        player1_name_surface = self.log_window.font.render(self.player1.get_name(), True, (255, 255, 255))
        self.gui_surface.blit(player1_name_surface, (self.p1_health_rect.x, self.p1_health_rect.y - 25))
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
        # Draw player2's name above the health bar
        player2_name_surface = self.log_window.font.render(self.player2.get_name(), True, (255, 255, 255))
        self.gui_surface.blit(player2_name_surface, (self.p2_health_rect.x, self.p2_health_rect.y - 25))
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
        for effect in self.particle_effects:
            effect.update()
            effect.draw(self.screen)

        # Remove dead particle effects
        self.particle_effects = [effect for effect in self.particle_effects if effect.particles]

        # Update log window on the GUI surface
        self.log_window.update(self.gui_surface)

        # Blit the GUI surface onto the right half of the main screen
        self.screen.blit(self.gui_surface, (684, 0))

    # Update the display
        pygame.display.update()
        logging.debug("GUI updated")

    def log(self, message):
        """Add a message to the log window."""
        self.log_window.add_message(message)
        logging.info(message)

    def process_round_moves(self, move1, move2):
        """
        Process both players' moves concurrently.
        move1: move chosen by player1 ("Attack", "Defending", "Resting", "Healing", "Special Attack")
        move2: move chosen by player2 ("Attack", "Defending", "Resting", "Healing", "Special Attack")
        """
        logging.debug(
            f"Processing moves: {self.player1.get_name()} -> {move1}, {self.player2.get_name()} -> {move2}"
        )
        # Process player1's move.
        self.particle_effects = []
        if move1 == "Attack":
            pygame.display.update()
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
                elif move2 == "Attacking":
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
        elif move1 == "Healing":
            if self.player1.get_mana() >= 30:
                self.player1.set_mana(self.player1.get_mana() - 30)
                health_gain = random.randint(15, 30)
                self.player1.set_health(self.player1.get_health() + health_gain)
                self.log(f"{self.player1.get_name()} heals and gains {health_gain} health!")
            else:
                self.log(
                    f"{self.player1.get_name()} tried to heal but didn't have enough mana!"
                )
        elif move1 == "Special Attack":
            if self.player1.get_mana() >= 50:
                self.player1.set_mana(self.player1.get_mana() - 50)
                damage = self.player1.get_attack() * 2
                self.player2.set_health(self.player2.get_health() - damage)
                self.log(
                    f"{self.player1.get_name()} uses a special attack on {self.player2.get_name()} for {damage} damage!"
                )
            else:
                self.log(
                    f"{self.player1.get_name()} tried to use a special attack but didn't have enough mana!"
                )

        # Process player2's move.
        if move2 == "Attack":
            
            pygame.display.update()
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
                elif move1 == "Attacking":
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
        elif move2 == "Healing":
            if self.player2.get_mana() >= 30:
                self.player2.set_mana(self.player2.get_mana() - 30)
                health_gain = random.randint(15, 30)
                self.player2.set_health(self.player2.get_health() + health_gain)
                self.log(f"{self.player2.get_name()} heals and gains {health_gain} health!")
            else:
                self.log(
                    f"{self.player2.get_name()} tried to heal but didn't have enough mana!"
                )
        elif move2 == "Special Attack":
            if self.player2.get_mana() >= 50:
                self.player2.set_mana(self.player2.get_mana() - 50)
                damage = self.player2.get_attack() * 2
                self.player1.set_health(self.player1.get_health() - damage)
                self.log(
                    f"{self.player2.get_name()} uses a special attack on {self.player1.get_name()} for {damage} damage!"
                )
            else:
                self.log(
                    f"{self.player2.get_name()} tried to use a special attack but didn't have enough mana!"
                )

    def battle_round(self, single_player=False, bot=None):
        """
        Main battle loop.
        For every TURN_TIME seconds, imaging.scan() is used to get both players' moves.
        The moves are processed, and both the camera view and GUI are updated.
        """
        logging.debug("Starting battle round")
        # Get moves from imaging.scan (blocks for TURN_TIME seconds).
        moves = imaging.scan(TURN_TIME, single_player)
        logging.debug(f"Scanned moves: {moves}")
        if not single_player:
            move_p1, move_p2 = moves
        else:
            move_p1 = moves
            if bot is None:
                logging.error("Bot is not defined in single player mode")
                raise ValueError("Bot is not defined in single player mode")
            move_p2 = ai.wizard_bot_turn(bot, self.player1)

        self.log(
            f"Moves this turn: {self.player1.get_name()} -> {move_p1}, {self.player2.get_name()} -> {move_p2}"
        )

        self.process_round_moves(move_p1, move_p2)

        # Update display: left half (camera) and right half (GUI).
        self.update_camera_view()
        self.update_gui()
        pygame.display.update()
        self.clock.tick(30)
        logging.debug("Battle round completed")

    def declare_winner(self):
        if self.player1.get_health() > self.player2.get_health():
            self.log(f"{self.player1.get_name()} wins!")
        elif self.player2.get_health() > self.player1.get_health():
            self.log(f"{self.player2.get_name()} wins!")
        else:
            self.log("It's a draw!")
        logging.info("Game ended, winner declared")
        # Keep the window open after the game ends until the user quits.
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    logging.info("Game window closed by user")
                    return
            self.update_camera_view()
            self.update_gui()
            pygame.display.update()
            self.clock.tick(30)

    def gameOver(self):
        if self.player1.get_health() <= 0 or self.player2.get_health() <= 0:
            logging.debug("Game over condition met")
            return True
        return False


def run():
    # Load configuration from YAML.
    yaml_path = os.path.join(os.path.dirname(__file__), "../properties.yaml")
    with open(yaml_path, "r") as file:
        properties = yaml.safe_load(file)
    logging.debug("Configuration loaded from YAML")

    player1_name = properties.get("game_options", {}).get("player1", {}).get("name")
    player2_name = properties.get("game_options", {}).get("player2", {}).get("name")
    if player1_name is None:
        logging.error("player1 is not specified in properties.yaml")
        raise ValueError("player1 is not specified in properties.yaml")
    if player2_name is None:
        logging.error("player2 is not specified in properties.yaml")
        raise ValueError("player2 is not specified in properties.yaml")

    single_player = properties.get("base_options", {}).get("mode") == "player_vs_ai"
    bot = None
    if single_player:
        bot = ai.wizard_bot()

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
        logging.error(f"Unknown player1: {player1_name}")
        raise ValueError(f"Unknown player1: {player1_name}")
    if p2_class is None:
        logging.error(f"Unknown player2: {player2_name}")
        raise ValueError(f"Unknown player2: {player2_name}")

    game = GameEngine(p1_class(), p2_class())
    logging.info("GameEngine instance created")
    while not game.gameOver():
        game.battle_round(single_player=single_player, bot=bot)
        pygame.time.wait(5000)
        # ? Logic for pausing game and resuming to let user see stats

    game.declare_winner()


if __name__ == "__main__":
    run()
