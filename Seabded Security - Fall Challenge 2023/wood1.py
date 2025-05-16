import sys
import math
from collections import Counter

# Score points by scanning valuable fish faster than your opponent.

TYPE = 4
COLORS = 3
MAX_X = 9999
MAX_Y = 9999

def print_large_info(gamestate):
    print("=== Game State Information ===", file=sys.stderr, flush=True)
    
    # Informations sur les drones
    print("Drones:", file=sys.stderr, flush=True)
    for drone in gamestate.my_drones:
        print(drone, file=sys.stderr, flush=True)

    # Informations sur les créatures visibles
    print("Visible Creatures:", file=sys.stderr, flush=True)
    for creature in gamestate.visible_creatures:
        print(creature, file=sys.stderr, flush=True)

    # Informations sur les créatures scannées
    print("Scanned Creatures:", file=sys.stderr, flush=True)
    for scanned in gamestate.scanned_creatures:
        print(scanned, file=sys.stderr, flush=True)

    # Informations sur les créatures sauvées
    print("Saved Creatures:", file=sys.stderr, flush=True)
    for saved in gamestate.saved_creatures:
        print(saved, file=sys.stderr, flush=True)

    # Informations sur les radars
    print("Radar Blip Count:", file=sys.stderr, flush=True)
    for radar in gamestate.radar_blip_count:
        print(radar, file=sys.stderr, flush=True)

    print("=== End of Game State Information ===", file=sys.stderr, flush=True)

class Drone:
    def __init__(self, drone_id, x, y, emergency, battery):
        self.drone_id = drone_id
        self.x = x
        self.y = y
        self.emergency = emergency
        self.battery = battery

    def __repr__(self):
        return f"Drone(drone_id={self.drone_id}, x={self.x}, y={self.y}, emergency={self.emergency}, battery={self.battery})"

class ScannedCreature:
    def __init__(self, scanned_by_drone_id, creature_id):
        self.scanned_by_drone_id = scanned_by_drone_id
        self.creature_id = creature_id

    def __repr__(self):
        return f"Scanned_by_drone={self.scanned_by_drone_id}, ScannedCreature(id={self.creature_id})"

class V_Creature:
    def __init__(self, creature_id, x, y, color, _type):
        self.creature_id = creature_id
        self.x = x
        self.y = y
        self.color = color
        self.type = _type

    def __repr__(self):
        return f"Creature(creature_id={self.creature_id}, x={self.x}, y={self.y}, color={self.color}, type={self.type})"

class SavedCreature:
    def __init__(self, creature_id):
        self.creature_id = creature_id
    
    def __repr__(self):
        return f"SavedCreature(id={self.creature_id})"

class Radar:
    def __init__(self, drone_id, creature_id, radar):
        self.drone_id = drone_id
        self.creature_id = creature_id
        self.radar = radar

    def __repr__(self):
        return f"Radar(drone_id={self.drone_id}, creature_id={self.creature_id}, radar={self.radar})"
    
    def __eq__(self, other):
        if not isinstance(other, Radar):
            return False
        return (self.creature_id == other.creature_id and self.radar == other.radar)

    def __hash__(self):
        return hash((self.creature_id, self.radar))

class EnemyDrone:
    def __init__(self, drone_id, drone_x, drone_y, emergency, battery):
        self.drone_id = drone_id
        self.x = drone_x
        self.y = drone_y
        self.emergency = emergency
        self.battery = battery
    
    def __repr__(self):
        return f"EnemyDrone(drone_id={self.drone_id}, x={self.x}, y={self.y}, emergency={self.emergency}, battery={self.battery})"

class EnemyScannedCreature:
    def __init__(self, scanned_by_drone_id, creature_id):
        self.scanned_by_drone_id = scanned_by_drone_id
        self.creature_id = creature_id

    def __repr__(self):
        return f"Scanned_by_enemy_drone={self.scanned_by_drone_id}, ScannedCreature(id={self.creature_id})"

class GameState:
    def __init__(self):
        self.my_drones = []
        self.enemy_drone = []
        self.scanned_creatures = []
        self.enemy_scanned_creatures = []
        self.visible_creatures = {}
        self.saved_creatures = []
        self.radar_blip_count = []
    
    def add_scanned_creatures(self, scanned_creature):
        self.scanned_creatures.append(scanned_creature)
    
    def update_scanned_creatures(self, creature_id, scanned_by_drone_id=None):
        found = False
        for scanned in self.scanned_creatures:
            if scanned.creature_id == creature_id:
                if scanned_by_drone_id is None:
                    scanned.scanned_by_drone_id = drone_id
                found = True
                break
        if not found:
            self.add_scanned_creatures(ScannedCreature(scanned_by_drone_id, creature_id))

    def add_enemy_scanned_creatures(self, enemy_scanned_creature):
        self.enemy_scanned_creatures.append(enemy_scanned_creature)

    def update_enemy_scanned_creatures(self, creature_id, scanned_by_drone_id=None):
        found = False
        for scanned in self.scanned_creatures:
            if scanned.creature_id == creature_id:
                if scanned_by_drone_id is None:
                    scanned.scanned_by_drone_id = drone_id
                found = True
                break
        if not found:
            self.add_enemy_scanned_creatures(EnemyScannedCreature(scanned_by_drone_id, creature_id))

    def add_drone(self, drone):
        self.my_drones.append(drone)
    
    def update_drone(self, drone_id, drone_x, drone_y, emergency, battery):
        found = False
        for drone in self.my_drones:
            if drone.drone_id == drone_id:
                drone.x = drone_x
                drone.y = drone_y
                drone.emergency = emergency
                drone.battery = battery
                found = True
                break
        if not found:
            self.add_drone(Drone(drone_id, drone_x, drone_y, emergency, battery))

    def add_creature(self, creature):
        self.visible_creatures[creature.creature_id] = creature
    
    def update_creature(self, creature_id, x, y, color=None, _type=None):
        if creature_id in self.visible_creatures:
            creature = self.visible_creatures[creature_id]
            creature.x = x
            creature.y = y
            # Mettre à jour la couleur et le type uniquement si ces valeurs sont fournies
            if color is not None:
                creature.color = color
            if _type is not None:
                creature.type = _type
        else:
            self.add_creature(V_Creature(creature_id, x, y, color, _type))
    
    def add_saved_creatures(self, scanned_creature):
        self.saved_creatures.append(scanned_creature)
    
    def update_saved_creatures(self, creature_id):
        found = False
        for saved in self.saved_creatures:
            if saved.creature_id == creature_id:
                found = True
                break
        if not found:
            self.add_saved_creatures(SavedCreature(creature_id))

    def add_radar(self, radar):
        self.radar_blip_count.append(radar)
    
    def update_radar(self, drone_id, creature_id, radar):
        new_radar = Radar(drone_id, creature_id, radar)
        if new_radar not in self.radar_blip_count:
            self.add_radar(new_radar)

    def add_enemy_drone(self, enemy_drone):
        self.enemy_drone.append(enemy_drone)
    
    def update_enemy_drone(self, drone_id, drone_x, drone_y, emergency, battery):
        found = False
        for drone in self.my_drones:
            if drone.drone_id == drone_id:
                drone.x = drone_x
                drone.y = drone_y
                drone.emergency = emergency
                drone.battery = battery
                found = True
                break
        if not found:
            self.add_enemy_drone(EnemyDrone(drone_id, drone_x, drone_y, emergency, battery))

    def __repr__(self):
        return f"GameState(visible_creatures={self.visible_creatures}, my_drones={self.my_drones}, saved_creatures={self.saved_creatures}, radar_blip_count={self.radar_blip_count}"

def distance_euclidean(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def is_list_empty(L):
    return L == []

# From Wood 3
def get_all_distance(my_drones, my_visible_creatures):
    distance = {}
    for drone in my_drones:
        for creature in my_visible_creatures:
            value = distance_euclidean(drone.x, drone.y, creature.x, creature.y)
            distance[creature.creature_id] = value
    return sorted(distance.items(), key=lambda t: t[1])

def move_towards_direction(drone, radar_direction):
    max_move_distance = 3000

    # Déterminer la direction en fonction du radar
    if radar_direction == "TL":
        # Haut-gauche
        new_x = drone.x - max_move_distance
        new_y = drone.y - max_move_distance
    elif radar_direction == "TR":
        # Haut-droite
        new_x = drone.x + max_move_distance
        new_y = drone.y - max_move_distance
    elif radar_direction == "BL":
        # Bas-gauche
        new_x = drone.x - max_move_distance
        new_y = drone.y + max_move_distance
    elif radar_direction == "BR":
        # Bas-droite
        new_x = drone.x + max_move_distance
        new_y = drone.y + max_move_distance
    else:
        # Si le radar ne détecte pas de direction, rester sur place
        new_x = drone.x
        new_y = drone.y

    new_x = max(0, min(new_x, MAX_X))
    new_y = max(0, min(new_y, MAX_Y))

    return new_x, new_y


def get_max_direction(non_scanned):
    if non_scanned:
        radar_list = [radar.radar for radar in gamestate.radar_blip_count if radar.creature_id in non_scanned]
    else:
        radar_list = [radar.radar for radar in gamestate.radar_blip_count]

    # print(f"Radar_list = {radar_list}", file=sys.stderr, flush=True)

    direction_counter = Counter(radar_list)

    filtering = max(direction_counter, key=lambda k: direction_counter[k])

    return filtering

# Vérifier les radars pour chaque créature et déplacer en fonction
def move_drone_based_on_radar(gamestate, non_scanned):
    direction_to = get_max_direction(non_scanned)
    print(f"Best Direction = {direction_to}", file=sys.stderr, flush=True)
    for drone in gamestate.my_drones:
        new_x, new_y = move_towards_direction(drone, direction_to)
        if drone.battery >= 5:
            print(f"MOVE {new_x} {new_y} 1")
        else:
            print(f"MOVE {new_x} {new_y} 0")


def remove_item(scanned_type_counts, scanned_color_counts):
    keys_to_remove = []

    # Iterate through the scanned creatures to determine which ones should be removed
    for creature_id in list(scanned_type_counts.keys()):
        if scanned_type_counts[creature_id] >= TYPE:
            keys_to_remove.append(creature_id)

    # Remove the keys from the dictionary
    for key in keys_to_remove:
        del scanned_type_counts[key]

    # Do the same for the scanned_color_counts dictionary if necessary
    keys_to_remove = []

    for color in list(scanned_color_counts.keys()):
        if scanned_color_counts[color] >= COLORS:
            keys_to_remove.append(color)

    for key in keys_to_remove:
        del scanned_color_counts[key]


gamestate = GameState()
tour = 0

creature_count = int(input())
for i in range(creature_count):
    creature_id, color, _type = [int(j) for j in input().split()]
    gamestate.update_creature(creature_id, 0, 0, color, _type)

# game loop
while True:
    tour += 1
    gamestate.radar_blip_count.clear()

    my_score = int(input())
    foe_score = int(input())

    my_scan_count = int(input())
    for i in range(my_scan_count):
        creature_id = int(input())
        gamestate.update_saved_creatures(creature_id)

    foe_scan_count = int(input())
    for i in range(foe_scan_count):
        creature_id = int(input())

    my_drone_count = int(input())
    for i in range(my_drone_count):
        drone_id, drone_x, drone_y, emergency, battery = [int(j) for j in input().split()]
        gamestate.update_drone(drone_id, drone_x, drone_y, emergency, battery)

    foe_drone_count = int(input())
    for i in range(foe_drone_count):
        drone_id, drone_x, drone_y, emergency, battery = [int(j) for j in input().split()]
        gamestate.update_enemy_drone(drone_id, drone_x, drone_y, emergency, battery)

    drone_scan_count = int(input())
    for i in range(drone_scan_count):
        drone_id, creature_id = [int(j) for j in input().split()]
        for drone in gamestate.my_drones:
            if drone_id == drone.drone_id:
                gamestate.update_scanned_creatures(creature_id, drone_id)
            else:
                gamestate.update_enemy_scanned_creatures(creature_id, drone_id)

    visible_creature_count = int(input())
    for i in range(visible_creature_count):
        creature_id, creature_x, creature_y, creature_vx, creature_vy = [int(j) for j in input().split()]
        gamestate.update_creature(creature_id, creature_x, creature_y)

    radar_blip_count = int(input())
    for i in range(radar_blip_count):
        inputs = input().split()
        drone_id = int(inputs[0])
        creature_id = int(inputs[1])
        radar = inputs[2]
        for drone in gamestate.my_drones:
            if drone_id == drone.drone_id:
                gamestate.update_radar(drone_id, creature_id, radar)

    # print(gamestate.radar_blip_count, file=sys.stderr, flush=True)
    # print(gamestate.visible_creatures, file=sys.stderr, flush=True)
    # print(gamestate.scanned_creatures, file=sys.stderr, flush=True)
    print(gamestate.enemy_drone, file=sys.stderr, flush=True)

    # Récupérer l'ensemble des IDs des créatures scannées
    scanned_ids = {scanned.creature_id for scanned in gamestate.scanned_creatures}

    # Récupérer l'ensemble des IDs des créatures sauvées
    saved_ids = {saved.creature_id for saved in gamestate.saved_creatures}

    # print(f"Visible ones = {visible_creatures_ids}", file=sys.stderr, flush=True)
    # print(f"Scanned Ones = {scanned_ids}", file=sys.stderr, flush=True)
    # print(f"Saved ones = {saved_ids}", file=sys.stderr, flush=True)
    
    enemy_scanned_ids = {scanned.creature_id for scanned in gamestate.enemy_scanned_creatures}

    # Filtrer les créatures qui ne sont pas encore scannees en comparant les id du radar et les creatures deja scannees
    non_scanned_creatures = [
        radar.creature_id for radar in gamestate.radar_blip_count 
        if radar.creature_id not in scanned_ids and radar.creature_id not in saved_ids
    ]

    # id que mes drones ont scannee mais que les drones enemy n'ont pas scannee
    creatures_to_afraid = [
        radar.creature_id for radar in gamestate.radar_blip_count 
        if radar.creature_id in scanned_ids and radar.creature_id not in enemy_scanned_ids
    ]

    if not non_scanned_creatures:    
        for drone in gamestate.my_drones:
            if drone.battery >= 5:
                print(f"MOVE {drone.x} 500 1")
            else:
                print(f"MOVE {drone.x} 500 0")
    elif non_scanned_creatures:
        move_drone_based_on_radar(gamestate, non_scanned_creatures)
    else:
        print("WAIT 0")

