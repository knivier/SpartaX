import pygame
import yaml
import sys
import os
import Player_List

# Load game options from YAML file, defaults are preset if yaml is errored
def load_options():
    try:
        yaml_path = os.path.join(os.path.dirname(__file__), '../properties.yaml')
        with open(yaml_path, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError: 
        return {
            "base_options": {
                "mode": "two_player",
                "debug_mode": False,
                "splitscreen": False,
                "skeleton": False,
                "difficulty": 2  # Ensure difficulty is included here
            },
            "game_options": {
                "ai": {
                    "attack": 0,
                    "health": 0,
                    "mana": 0
                }
            }
        }

# Save game options to YAML file
def save_options(options):
    yaml_path = os.path.join(os.path.dirname(__file__), '../properties.yaml')
    with open(yaml_path, 'w') as file:
        yaml.dump(options, file)

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600  # Init heights, can change to 1020x1080rez
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('WizViz')

# Colors
WHITE, BLACK, GRAY, LIGHT_GRAY = (255, 255, 255), (0, 0, 0), (200, 200, 200), (220, 220, 220)
BLUE, LIGHT_BLUE, DARK_GRAY, GREEN, RED = (0, 0, 255), (173, 216, 230), (50, 50, 50), (0, 255, 0), (255, 0, 0)

# Fonts
FONT, TITLE_FONT, TOOLTIP_FONT = pygame.font.Font(None, 36), pygame.font.Font(None, 72), pygame.font.Font(None, 24)

# Load options
options = load_options()
print(options)

# Button class for UI
def draw_button(text, x, y, width, height, color, hover_color, mouse_pos):
    rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, hover_color if rect.collidepoint(mouse_pos) else color, rect, border_radius=10)
    text_surface = FONT.render(text, True, BLACK)
    screen.blit(text_surface, text_surface.get_rect(center=rect.center))
    return rect

# Main menu
def main_menu():
    running = True
    while running:
        screen.fill(WHITE)
        mouse_pos = pygame.mouse.get_pos()
        
        title_text = TITLE_FONT.render('WizViz', True, DARK_GRAY)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 100))

        buttons = {
            "Play": draw_button('Play', 350, 250, 100, 50, GRAY, LIGHT_BLUE, mouse_pos),
            "Options": draw_button('Options', 350, 320, 100, 50, GRAY, LIGHT_BLUE, mouse_pos),
            "Quit": draw_button('Quit', 350, 390, 100, 50, GRAY, LIGHT_BLUE, mouse_pos)
        }
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if buttons["Play"].collidepoint(event.pos):
                    start_game() # Start game, ideally close this one after the next file starts
                elif buttons["Options"].collidepoint(event.pos):
                    options_menu()
                elif buttons["Quit"].collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()
        
        pygame.display.flip()

# Options menu
def options_menu():
    running = True
    var = True
    while running:
        screen.fill(WHITE)
        mouse_pos = pygame.mouse.get_pos()
        
        option_keys = list(options["base_options"].keys())
        if var:
            print(option_keys)
            var = not var
        
        y_offset = 20
        option_rects = {}
        
        for key in option_keys:
            # Handling 'difficulty' separately since it's a number
            if key == "difficulty":
                option_text = f'{key.capitalize()}: {options["base_options"][key]}'
                option_rects[key] = draw_button(option_text, 200, y_offset, 400, 40, GRAY, LIGHT_BLUE, mouse_pos)
                y_offset += 60
            else:
                option_text = f'{key.capitalize()}: {options["base_options"][key]}'
                option_rects[key] = draw_button(option_text, 200, y_offset, 400, 40, GRAY, LIGHT_BLUE, mouse_pos)
                y_offset += 60
        
        ai_keys = list(options["game_options"]["ai"].keys())
        for key in ai_keys:
            option_text = f'AI {key.capitalize()}: {options["game_options"]["ai"][key]}'
            option_rects[key] = draw_button(option_text, 200, y_offset, 400, 40, GRAY, LIGHT_BLUE, mouse_pos)
            y_offset += 60
        
        buttons = {
            "Save": draw_button('Save', SCREEN_WIDTH // 2 + 100, 500, 150, 50, GREEN, LIGHT_BLUE, mouse_pos),
            "Back": draw_button('Back', SCREEN_WIDTH // 2 - 250, 500, 150, 50, RED, LIGHT_BLUE, mouse_pos)
        }
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for key, rect in option_rects.items():
                    if rect.collidepoint(event.pos):
                        if key in options["base_options"]:
                            if isinstance(options["base_options"][key], bool):
                                options["base_options"][key] = not options["base_options"][key]
                            elif key == "mode":
                                options["base_options"][key] = "player_vs_ai" if options["base_options"][key] == "two_player" else "two_player"
                            elif key == "difficulty":
                                # For 'difficulty', let the user change the difficultyiculty
                                options["base_options"][key] = (options["base_options"][key] % 5) + 1  # Toggle between 1, 2, 3 for difficulty
                        elif key in options["game_options"]["ai"]:
                            options["game_options"]["ai"][key] += 1  # Increment AI options for simplicity
                if buttons["Save"].collidepoint(event.pos):
                    save_options(options)
                    running = False
                elif buttons["Back"].collidepoint(event.pos):
                    running = False

        pygame.display.flip()

# Start game
def start_game():
    def select_player_menu(player_num):
        running = True
        selected_player = None
        players = [Player_List.Draco(), Player_List.Hydra(), Player_List.Phoenix(), Player_List.Lyra(), Player_List.Orion(), Player_List.Pegasus(), Player_List.Andromeda(), Player_List.Centaurus(), Player_List.Cassiopeia()]
        player_names = [player.getName() for player in players]
        
        while running:
            screen.fill(WHITE)
            mouse_pos = pygame.mouse.get_pos()
            
            title_text = TITLE_FONT.render(f'Select Player {player_num}', True, DARK_GRAY)
            screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))
            
            y_offset = 150
            player_rects = {}
            
            for name in player_names:
                player_rects[name] = draw_button(name, 300, y_offset, 200, 50, GRAY, LIGHT_BLUE, mouse_pos)
                y_offset += 70
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for name, rect in player_rects.items():
                        if rect.collidepoint(event.pos):
                            selected_player = name
                            running = False
            
            pygame.display.flip()
        
        return selected_player

    player1 = select_player_menu(1)
    options["game_options"]["player1"] = {"name": player1}
    save_options(options)

    player2 = select_player_menu(2)
    options["game_options"]["player2"] = {"name": player2}
    save_options(options)

    def countdown():
        for i in range(3, 0, -1):
            screen.fill(WHITE)
            countdown_text = TITLE_FONT.render(str(i), True, DARK_GRAY)
            screen.blit(countdown_text, (SCREEN_WIDTH // 2 - countdown_text.get_width() // 2, SCREEN_HEIGHT // 2 - countdown_text.get_height() // 2))
            pygame.display.flip()
            pygame.time.delay(1000)

    countdown()
    pygame.quit()
    import engine
    engine.run()

# Run main menu
main_menu()
pygame.quit()
