import pygame
import yaml
import game
import sys

# Load game options from YAML file, defaults are preset if yaml is errored
def load_options():
    try:
        with open('../properties.yaml', 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        return {
            "base_options": {
            "mode": "two_player",
            "debug_mode": False,
            "splitscreen": False,
            "skeleton": False
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
    with open('../properties.yaml', 'w') as file:
        yaml.dump(options, file)

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600 # Init heights, can change to 1020x1080rez
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('WizViz')

# Colors
WHITE, BLACK, GRAY, LIGHT_GRAY = (255, 255, 255), (0, 0, 0), (200, 200, 200), (220, 220, 220)
BLUE, LIGHT_BLUE, DARK_GRAY, GREEN, RED = (0, 0, 255), (173, 216, 230), (50, 50, 50), (0, 255, 0), (255, 0, 0)

# Fonts
FONT, TITLE_FONT, TOOLTIP_FONT = pygame.font.Font(None, 36), pygame.font.Font(None, 72), pygame.font.Font(None, 24)

# Load options
options = load_options()

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
            while running:
                screen.fill(WHITE)
                mouse_pos = pygame.mouse.get_pos()
                
                option_keys = list(options["base_options"].keys())
                y_offset = 60
                option_rects = {}
                
                for key in option_keys:
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
                                elif key in options["game_options"]["ai"]:
                                    options["game_options"]["ai"][key] += 1  # Increment AI options for simplicity
                        if buttons["Save"].collidepoint(event.pos):
                            save_options(options)
                            running = False
                        elif buttons["Back"].collidepoint(event.pos):
                            running = False

                pygame.display.flip()
        pygame.display.flip()

# Start game
def start_game():
    game.run()

# Run main menu
main_menu()
pygame.quit()
