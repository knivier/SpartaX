import random

class Player:
    def __init__(self, name, health, attack, defense, special_attack_name, special_attack_damage):
        self.name = name
        self.health = health
        self.attack = attack
        self.mana = random.randint(80, 120)
        self.defense = defense
        self.special_attack_name = special_attack_name
        self.special_attack_damage = special_attack_damage

        if self.mana < 100:
            self.special_attack_damage *= 1.25

    def get_name(self):
        return self.name
    
    def set_name(self, name):
        self.name = name

    def get_attack(self):
        return self.attack
    
    def set_attack(self, attack):
        self.attack = attack
    
    def get_defense(self):
        return self.defense
    
    def set_defense(self, defense):
        self.defense = defense
    
    def get_special_attack_name(self):
        return self.special_attack_name
    
    def set_special_attack_name(self, special_attack_name):
        self.special_attack_name = special_attack_name
    
    def get_special_attack_damage(self):
        return self.special_attack_damage
    
    def set_special_attack_damage(self, special_attack_damage):
        self.special_attack_damage = special_attack_damage

    def get_health(self):
        return self.health

    def set_health(self, health):
        self.health = health

    def get_mana(self):
        return self.mana
    
    def set_mana(self, mana):
        self.mana = mana
