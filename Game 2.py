import random
import time
import networkx as nx

# Game Setup
class Airport:
    def __init__(self, name, coin_bonus=0, fuel_cost=0, secret_route=None):
        self.name = name
        self.coin_bonus = coin_bonus
        self.fuel_cost = fuel_cost
        self.secret_route = secret_route  # Hidden airport connections

class Player:
    def __init__(self, role, location, coins, mileage):
        self.role = role  # "police" or "thief"
        self.location = location
        self.coins = coins
        self.mileage = mileage
        self.traps = set()
        self.hidden = False

    def move(self, destination, cost):
        if self.mileage < cost:
            print(f"{self.role.capitalize()} doesn't have enough mileage!")
            return False
        self.mileage -= cost
        self.location = destination
        print(f"{self.role.capitalize()} moved to {destination}")
        return True

    def refuel(self, cost, mileage_gain):
        if self.coins < cost:
            print("Not enough coins to refuel!")
            return False
        self.coins -= cost
        self.mileage += mileage_gain
        print(f"{self.role.capitalize()} refueled!")
        return True

class Game:
    def __init__(self):
        self.map = nx.Graph()
        self.players = {}
        self.setup_map()
        self.setup_players()

    def setup_map(self):
        # Define airports with connections, fuel costs, and bonuses
        airports = [
            Airport("London", coin_bonus=50, fuel_cost=20, secret_route="Dublin"),
            Airport("Paris", coin_bonus=30, fuel_cost=15),
            Airport("Berlin", coin_bonus=40, fuel_cost=25),
            Airport("Rome", coin_bonus=20, fuel_cost=20, secret_route="Madrid"),
            Airport("Madrid", coin_bonus=30, fuel_cost=20),
            Airport("Dublin", coin_bonus=50, fuel_cost=15),
        ]

        # Add airports and connections
        for airport in airports:
            self.map.add_node(airport.name, data=airport)

        # Connect airports with mileage costs
        self.map.add_edge("London", "Paris", weight=50)
        self.map.add_edge("London", "Berlin", weight=100)
        self.map.add_edge("Paris", "Rome", weight=70)
        self.map.add_edge("Berlin", "Rome", weight=80)
        self.map.add_edge("Rome", "Madrid", weight=60)
        self.map.add_edge("Dublin", "London", weight=40)

    def setup_players(self):
        # Initialize players
        police = Player("police", location="London", coins=100, mileage=300)
        thief = Player("thief", location="Paris", coins=100, mileage=300)
        self.players = {"police": police, "thief": thief}

    def detect_thief(self):
        # Check if the thief is within a 3-airport radius
        police = self.players["police"]
        thief = self.players["thief"]
        nearby_airports = nx.single_source_dijkstra_path_length(
            self.map, police.location, cutoff=3
        ).keys()
        return thief.location in nearby_airports

    def take_turn(self, role):
        player = self.players[role]
        opponent = self.players["thief" if role == "police" else "police"]

        print(f"\n{role.capitalize()}'s turn:")
        print(f"Location: {player.location}, Coins: {player.coins}, Mileage: {player.mileage}")

        # Actions
        actions = ["Move", "Refuel"]
        if role == "police":
            actions += ["Set Trap", "Disable Secret Routes"]
        elif role == "thief":
            actions += ["Hide", "Steal Coins"]

        print("Actions:", ", ".join(actions))
        action = input("Choose an action: ").strip().lower()

        if action == "move":
            self.handle_move(player)
        elif action == "refuel":
            self.handle_refuel(player)
        elif action == "set trap" and role == "police":
            self.handle_trap(player)
        elif action == "disable secret routes" and role == "police":
            print("Secret routes disabled for this turn!")
        elif action == "hide" and role == "thief":
            player.hidden = True
            print("Thief is now hidden!")
        elif action == "steal coins" and role == "thief":
            if opponent.location in nx.neighbors(self.map, player.location):
                player.coins += 50
                opponent.coins -= 50
                print("Thief stole 50 coins!")
            else:
                print("No nearby police to steal from!")

    def handle_move(self, player):
        current_airport = player.location
        neighbors = self.map.neighbors(current_airport)
        print("Available destinations:", ", ".join(neighbors))

        destination = input("Enter destination: ").strip()
        if destination in neighbors:
            cost = self.map[current_airport][destination]["weight"]
            player.move(destination, cost)
        else:
            print("Invalid destination!")

    def handle_refuel(self, player):
        current_airport = self.map.nodes[player.location]["data"]
        if player.refuel(current_airport.fuel_cost, 100):
            print("Refuel successful!")

    def handle_trap(self, player):
        trap_location = input("Enter airport to set trap: ").strip()
        if trap_location in self.map.nodes:
            player.traps.add(trap_location)
            print(f"Trap set at {trap_location}!")
        else:
            print("Invalid airport!")

    def play(self):
        turn = 0
        while True:
            current_player = "police" if turn % 2 == 0 else "thief"
            self.take_turn(current_player)

            # Check for win conditions
            if self.players["police"].location == self.players["thief"].location:
                print("Police captured the thief! Game over!")
                break

            turn += 1


# Run the game
game = Game()
game.play()
