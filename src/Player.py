# player.py
import random
class Player:
    def __init__(self, name, health, attack, defense, special_attack_name, special_attack_damage):
        self.name = name
        self.health = health
        self.attack = attack
        self.mana = random.randint(80, 120)
        x = random.randint(1, 2)
        self.defense = defense
        # if x is 1: # 50% chance for inefficiency
        #     def_mult = random.randint(40, 80)
        #     self.defense = self.defense * (def_mult / 100)
        self.special_attack_name = special_attack_name
        self.special_attack_damage = special_attack_damage
        if self.mana < 100:
            self.special_attack_damage *= 1.25

    def getName(self):
        return self.name
    
    def setName(self, name):
        self.name = name

    def getAttack(self):
        return self.attack
    
    def setAttack(self, attack):
        self.attack = attack
    
    def getDefense(self):
        return self.defense
    
    def setDefense(self, defense):
        self.defense = defense
    
    def getSpecialAttackName(self):
        return self.special_attack_name
    
    def setSpecialAttackName(self, special_attack_name):
        self.special_attack_name = special_attack_name
    
    def getSpecialAttackDamage(self):
        return self.special_attack_damage
    
    def setSpecialAttackDamage(self, special_attack_damage):
        self.special_attack_damage = special_attack_damage

    def getHealth(self):
        return self.health

    def setHealth(self, health):
        self.health = health

    def getMana(self):
        return self.mana
    
    def setMana(self, mana):
        self.mana = mana
