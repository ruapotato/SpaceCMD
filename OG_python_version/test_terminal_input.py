#!/usr/bin/env python3
"""
Test terminal input rendering to debug typing visibility
"""

import pygame
from core.gui.themes import Theme

pygame.init()
Theme.init_fonts()

screen = pygame.display.set_mode((800, 200))
pygame.display.set_caption("Terminal Input Test")

input_text = ""
cursor_pos = 0
cursor_visible = True
cursor_blink_time = 0

clock = pygame.time.Clock()
running = True

while running:
    dt = clock.tick(60) / 1000.0

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_BACKSPACE:
                if cursor_pos > 0:
                    input_text = input_text[:cursor_pos-1] + input_text[cursor_pos:]
                    cursor_pos -= 1
            elif event.key == pygame.K_RETURN:
                print(f"Entered: {input_text}")
                input_text = ""
                cursor_pos = 0
            elif event.unicode and event.unicode.isprintable():
                input_text = input_text[:cursor_pos] + event.unicode + input_text[cursor_pos:]
                cursor_pos += 1
                print(f"Typed '{event.unicode}' - input_text is now: '{input_text}'")

    # Update cursor blink
    cursor_blink_time += dt
    if cursor_blink_time >= 0.5:
        cursor_visible = not cursor_visible
        cursor_blink_time = 0

    # Render
    screen.fill((10, 10, 30))

    # Prompt
    prompt = "test:/ $ "
    if Theme.FONT_TERMINAL:
        prompt_surface = Theme.FONT_TERMINAL.render(prompt, True, (100, 255, 150))
        screen.blit(prompt_surface, (10, 80))

        # Input text
        prompt_width = prompt_surface.get_width()
        input_surface = Theme.FONT_TERMINAL.render(input_text, True, (200, 255, 200))
        screen.blit(input_surface, (10 + prompt_width, 80))

        # Cursor
        char_width = Theme.FONT_TERMINAL.size("W")[0]
        cursor_x = 10 + prompt_width + cursor_pos * char_width
        if cursor_visible:
            pygame.draw.rect(screen, (0, 255, 100), (cursor_x, 80, max(2, char_width), 14))

    # Debug info
    if Theme.FONT_TERMINAL:
        debug = f"input_text: '{input_text}' | cursor_pos: {cursor_pos} | len: {len(input_text)}"
        debug_surface = Theme.FONT_TERMINAL.render(debug, True, (255, 255, 0))
        screen.blit(debug_surface, (10, 150))

    pygame.display.flip()

pygame.quit()
