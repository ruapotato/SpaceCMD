#!/usr/bin/env python3
"""Test the map GUI widget"""

import pygame
import sys

# Add core to path
sys.path.insert(0, '/home/david/SpaceCMD')

from core.ships import create_ship
from core.ship_os import ShipOS
from core.world_manager import WorldManager
from core.gui.map_widget import MapWidget
from core.gui.themes import Theme

print("Initializing test...")

# Initialize pygame
pygame.init()
Theme.init_fonts()

# Create screen
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Map Widget Test")

# Create ship and world
ship = create_ship("kestrel")
ship_os = ShipOS(ship)
ship_os.boot(verbose=False)
ship_os.login('root', 'root')

# Create small world for testing
world_manager = WorldManager(ship_os, num_sectors=4)
ship_os.world_manager = world_manager

# Create map widget
map_widget = MapWidget(800, 600)
map_widget.set_world_manager(world_manager)
map_widget.ship_os = ship_os

print(f"Map created with {len(world_manager.world_map.nodes)} nodes")

current = world_manager.world_map.get_current_node()
print(f"Current node: {current.id} ({current.type.value})")

available = world_manager.get_available_jumps()
print(f"Available jumps: {len(available)}")
for node in available[:5]:
    print(f"  - {node.id}: {node.type.value}")

print("\nMap widget ready!")
print("Controls:")
print("  Click on nodes to jump")
print("  ESC to quit")
print()

# Main loop
clock = pygame.time.Clock()
running = True

while running:
    dt = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

        # Pass events to map widget
        mouse_pos = pygame.mouse.get_pos()
        map_widget.handle_event(event, mouse_pos)

    # Update
    map_widget.update(dt)

    # Render
    screen.fill((0, 0, 0))
    map_surface = map_widget.render()
    screen.blit(map_surface, (0, 0))

    pygame.display.flip()

pygame.quit()
print("Test complete!")
