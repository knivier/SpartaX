import random

class wizard_bot:
    def __init__(self, difficulty):
        #add difficulty as variable
        self.health = 80 + (difficulty * 10)
        self.mana = 40 + (difficulty * 10)
        self.state = ""

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

def wizard_bot_turn(bot, player, difficult):
    #safety
    if difficult < 0:
        difficult = 0
    #easy/medium mode 
    if(difficult <= 3):
        number = random.randint(1,4)
        if number == 1: 
            bot.set_state("Rest")
        elif number == 2: 
            bot.set_state("Attack")
        elif number == 3: 
            bot.set_state("Defend")
        elif number == 4: 
            bot.set_state("Heal")
        return 
    # FSM - finite state machine to determine the wizard's action
    if bot.get_mana() == 0:
        bot.set_state("Rest")
    elif player.get_health() <= (difficult * 10) and bot.has_enough_mana(10):
        bot.set_state("Attack")
    elif bot.get_health() <= player.get_attack() and bot.has_enough_mana(20):
        bot.set_state("Defend")
    elif bot.get_health() <= 30 and bot.has_enough_mana(30):
        bot.set_state("Heal")
    else:
        bot.set_state("Attack")
    return 

