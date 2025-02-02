import os
import random
import yaml


class wizard_bot:
    def __init__(self):
        def loadDifficulty():
            try:
                yaml_path = os.path.join(
                    os.path.dirname(__file__), "../properties.yaml"
                )
                with open(yaml_path, "r") as file:
                    properties = yaml.safe_load(file)
                    difficulty = properties.get("base_options", {}).get("difficulty", 2)
                    health_base = (
                        properties.get("game_options", {})
                        .get("ai", {})
                        .get("health", 0)
                    )
                    attack_base = (
                        properties.get("game_options", {})
                        .get("ai", {})
                        .get("attack", 0)
                    )
                    mana_base = (
                        properties.get("game_options", {}).get("ai", {}).get("mana", 0)
                    )
            except FileNotFoundError:
                difficulty = 2
            return [difficulty, health_base, attack_base, mana_base]

        self.difficulty = loadDifficulty()[0]
        self.health = loadDifficulty()[1] + (self.difficulty * 10)
        self.mana = loadDifficulty()[2] + (self.difficulty * 10)
        self.attack = loadDifficulty()[3] + (self.difficulty + 10)
        self.state = ""

    def get_attack(self):
        return self.attack

    def set_attack(self, value):
        self.attack = value

    def get_mana(self):
        return self.mana

    def get_health(self):
        return self.health

    def set_mana(self, value):
        self.mana += value
        if self.mana < 0:
            self.mana = 0

    def set_health(self, value):
        self.health += value
        if self.health < 0:
            self.health = 0

    def set_state(self, state2):
        self.state = state2

    def get_state(self):
        return self.state

    def has_enough_mana(self, value):
        return self.mana >= value


def wizard_bot_turn(bot, player):
    # safety
    if bot.difficulty < 0:
        bot.difficulty = 0
    if bot.difficulty > 5:
        bot.difficulty = 5
    # easy/medium mode
    if bot.difficulty <= 3:
        number = random.randint(1, 5)
        if number == 1:
            bot.set_state("Resting")
        elif number == 2:
            bot.set_state("Attacking")
        elif number == 3:
            bot.set_state("Defending")
        elif number == 4:
            bot.set_state("Healing")
        else:
            bot.set_state("Special Attack")
        return bot.get_state()
    # FSM - finite state machine to determine the wizard's action
    if bot.get_mana() == 0:
        bot.set_state("Resting")
    elif player.get_health() <= bot.get_attack() and bot.has_enough_mana(10):
        bot.set_state("Attacking")
    elif bot.get_health() <= player.get_attack() and bot.has_enough_mana(20):
        bot.set_state("Defending")
    elif bot.get_health() <= 30 and bot.has_enough_mana(30):
        bot.set_state("Healing")
    else:
        bot.set_state("Attack")
    return bot.get_state()
