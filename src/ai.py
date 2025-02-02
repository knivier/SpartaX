class wizard_bot:
    def __init__(self, health=100, mana=50):
        self.health = health
        self.mana = mana
        self.state = "Idle"

    def get_mana(self):
        return self.mana
    
    def get_health(self):
        return self.health
    
    def change_mana(self, value):
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
    # FSM - finite state machine to determine the wizard's action
    if bot.get_mana() == 0:
        bot.set_state("Rest")
    elif bot.get_health() <= 20 and bot.has_enough_mana(10) and player.get_health() <= 10:
        bot.set_state("Attack")
    elif bot.get_health() <= 20 and bot.has_enough_mana(20) and player.get_health() > 10:
        bot.set_state("Heal")
    elif bot.get_health() <= 30 and bot.has_enough_mana(10):
        bot.set_state("Defend")
    else:
        bot.set_state("Attack")

