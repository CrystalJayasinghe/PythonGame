import pygame
import random
import networkx as nx

# Initialize pygame
pygame.init()

# Screen dimensions and setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chase the Criminal")
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# Fonts
font = pygame.font.Font(None, 36)

# Create the airport map (Graph structure)
class Airport:
    def __init__(self, name, x, y, coin_bonus=0, fuel_cost=0, secret_route=None):
        self.name = name
        self.x = x
        self.y = y
        self.coin_bonus = coin_bonus
        self.fuel_cost = fuel_cost
        self.secret_route = secret_route  # Hidden airport connections

# Define airports and their positions on the map
AIRPORTS = [
    Airport("London", 100, 100, coin_bonus=50, fuel_cost=20, secret_route="Dublin"),
    Airport("Paris", 300, 150, coin_bonus=30, fuel_cost=15),
    Airport("Berlin", 500, 100, coin_bonus=40, fuel_cost=25),
    Airport("Rome", 400, 400, coin_bonus=20, fuel_cost=20, secret_route="Madrid"),
    Airport("Madrid", 200, 400, coin_bonus=30, fuel_cost=20),
    Airport("Dublin", 150, 250, coin_bonus=50, fuel_cost=15),
]

# Define connections and costs
GRAPH = nx.Graph()
for airport in AIRPORTS:
    GRAPH.add_node(airport.name, data=airport)

GRAPH.add_edge("London", "Paris", weight=50)
GRAPH.add_edge("London", "Berlin", weight=100)
GRAPH.add_edge("Paris", "Rome", weight=70)
GRAPH.add_edge("Berlin", "Rome", weight=80)
GRAPH.add_edge("Rome", "Madrid", weight=60)
GRAPH.add_edge("Dublin", "London", weight=40)

# Player class
class Player:
    def __init__(self, role, location, coins, mileage):
        self.role = role
        self.location = location
        self.coins = coins
        self.mileage = mileage
        self.traps = set()
        self.hidden = False

    def move(self, destination, cost):
        if self.mileage < cost:
            return False
        self.mileage -= cost
        self.location = destination
        return True

    def refuel(self, cost, mileage_gain):
        if self.coins < cost:
            return False
        self.coins -= cost
        self.mileage += mileage_gain
        return True

# Initialize players
police = Player("police", "London", 100, 300)
thief = Player("thief", "Paris", 100, 300)

# Draw map
def draw_map():
    screen.fill(WHITE)
    # Draw connections
    for u, v in GRAPH.edges:
        start_airport = GRAPH.nodes[u]["data"]
        end_airport = GRAPH.nodes[v]["data"]
        pygame.draw.line(screen, BLACK, (start_airport.x, start_airport.y), (end_airport.x, end_airport.y), 2)
    # Draw airports
    for airport in AIRPORTS:
        pygame.draw.circle(screen, BLUE if airport.name != thief.location else RED, (airport.x, airport.y), 20)
        text = font.render(airport.name, True, BLACK)
        screen.blit(text, (airport.x - 20, airport.y - 30))
    # Draw player locations
    police_airport = next(a for a in AIRPORTS if a.name == police.location)
    pygame.draw.circle(screen, GREEN, (police_airport.x, police_airport.y), 25, 2)

# Game loop
def main():
    running = True
    turn = 0  # Alternates between police and thief
    while running:
        clock.tick(60)
        draw_map()

        # Display stats
        police_stats = font.render(f"Police: {police.location} | Coins: {police.coins} | Mileage: {police.mileage}", True, BLACK)
        thief_stats = font.render(f"Thief: {thief.location} | Coins: {thief.coins} | Mileage: {thief.mileage}", True, BLACK)
        screen.blit(police_stats, (10, 10))
        screen.blit(thief_stats, (10, 40))

        pygame.display.flip()

        # Turn-based actions
        if turn % 2 == 0:
            # Police turn
            print("Police's turn! Select an action (Move, Refuel, Set Trap): ")
            action = input("Action: ").lower()
            if action == "move":
                available_moves = list(GRAPH.neighbors(police.location))
                print("Available moves:", ", ".join(available_moves))
                destination = input("Enter destination: ").strip()
                if destination in available_moves:
                    cost = GRAPH[police.location][destination]["weight"]
                    police.move(destination, cost)
            elif action == "refuel":
                current_airport = GRAPH.nodes[police.location]["data"]
                police.refuel(current_airport.fuel_cost, 100)
            elif action == "set trap":
                trap_location = input("Enter airport to set trap: ").strip()
                police.traps.add(trap_location)
                print(f"Trap set at {trap_location}")
        else:
            # Thief's turn (Simple AI)
            print("Thief's turn!")
            available_moves = list(GRAPH.neighbors(thief.location))
            destination = random.choice(available_moves)
            cost = GRAPH[thief.location][destination]["weight"]
            thief.move(destination, cost)
            print(f"Thief moved to {destination}")

        # Win condition: Police catches thief
        if police.location == thief.location:
            print("Police caught the thief! Game over!")
            running = False

        turn += 1

    pygame.quit()

if __name__ == "__main__":
    main()
