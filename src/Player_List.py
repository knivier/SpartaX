# All Players
from Player import Player as pl 

# Health, attack, and defense 
# should be different for all
# Mana should be same for all

#     def __init__(self, name, health, attack, defense, special_attack_name, special_attack_damage):
class Draco(pl):
    def __init__(self):
        super().__init__("Draco", health=120, attack=25, defense=5, special_attack_name="Fireball", special_attack_damage=35)

class Hydra(pl):
    def __init__(self):
        super().__init__("Hydra", health=140, attack=30, defense=1, special_attack_name="Venom", special_attack_damage=35)

class Phoenix(pl):
    def __init__(self):
        super().__init__("Phoenix", health=160, attack=15, defense=25, special_attack_name="Rebirth", special_attack_damage=45)

class Lyra(pl):
    def __init__(self):
        super().__init__("Lyra", health=60, attack=40, defense=20, special_attack_name="Heal", special_attack_damage=50)

class Orion(pl):
    def __init__(self):
        super().__init__("Orion", health=110, attack=28, defense=8, special_attack_name="Arrow Storm", special_attack_damage=38)

class Pegasus(pl):
    def __init__(self):
        super().__init__("Pegasus", health=90, attack=32, defense=12, special_attack_name="Wing Slash", special_attack_damage=42)

class Andromeda(pl):
    def __init__(self):
        super().__init__("Andromeda", health=70, attack=37, defense=17, special_attack_name="Chain Strike", special_attack_damage=47)

class Centaurus(pl):
    def __init__(self):
        super().__init__("Centaurus", health=85, attack=33, defense=13, special_attack_name="Trample", special_attack_damage=43)

class Cassiopeia(pl):
    def __init__(self):
        super().__init__("Cassiopeia", health=75, attack=36, defense=18, special_attack_name="Poison Fang", special_attack_damage=46)