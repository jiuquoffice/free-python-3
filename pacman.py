"""
Simplified Pacman.

Written by Grant Jenks
http://www.grantjenks.com/

DISCLAIMER
THERE IS NO WARRANTY FOR THE PROGRAM, TO THE EXTENT PERMITTED BY APPLICABLE
LAW. EXCEPT WHEN OTHERWISE STATED IN WRITING THE COPYRIGHT HOLDERS AND/OR
OTHER PARTIES PROVIDE THE PROGRAM "AS IS" WITHOUT WARRANTY OF ANY KIND,
EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE
ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF THE PROGRAM IS WITH YOU.
SHOULD THE PROGRAM PROVE DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY
SERVICING, REPAIR OR CORRECTION.

Copyright
This work is licensed under the
Creative Commons Attribution-NonCommercial-NoDerivs 3.0 Unported License.
To view a copy of this license, visit
http://creativecommons.org/licenses/by-nc-nd/3.0/
or send a letter to Creative Commons, 171 Second Street, Suite 300,
San Francisco, California, 94105, USA
"""

import sys
import pygame
import random
from pygame.locals import *

pygame.init()

font = pygame.font.Font(None, 24)
pacman_img = pygame.image.load('pacman.jpg')
ghost_img = pygame.image.load('ghost.jpg')
clock = pygame.time.Clock()
screen = pygame.display.set_mode((340, 400))

class Game:
    """Track pacman game state."""
    def __init__(self):
        """Initialize game."""
        self.reset()

    def reset(self):
        """Reset game to initial game state."""
        self.running = True
        self.score = 0

        self.tiles_width = 17
        self.tiles = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                      0, 2, 2, 2, 2, 2, 2, 2, 0, 2, 2, 2, 2, 2, 2, 2, 0,
                      0, 2, 0, 0, 2, 0, 0, 2, 0, 2, 0, 0, 2, 0, 0, 2, 0,
                      0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0,
                      0, 2, 0, 0, 2, 0, 2, 0, 0, 0, 2, 0, 2, 0, 0, 2, 0,
                      0, 2, 2, 2, 2, 0, 2, 2, 0, 2, 2, 0, 2, 2, 2, 2, 0,
                      0, 2, 0, 0, 2, 0, 0, 2, 0, 2, 0, 0, 2, 0, 0, 0, 0,
                      0, 2, 0, 0, 2, 0, 2, 2, 2, 2, 2, 0, 2, 0, 0, 0, 0,
                      0, 2, 2, 2, 2, 2, 2, 0, 0, 0, 2, 2, 2, 2, 2, 2, 0,
                      0, 0, 0, 0, 2, 0, 2, 2, 2, 2, 2, 0, 2, 0, 0, 2, 0,
                      0, 0, 0, 0, 2, 0, 2, 0, 0, 0, 2, 0, 2, 0, 0, 2, 0,
                      0, 2, 2, 2, 2, 2, 2, 2, 0, 2, 2, 2, 2, 2, 2, 2, 0,
                      0, 2, 0, 0, 2, 0, 0, 2, 0, 2, 0, 0, 2, 0, 0, 2, 0,
                      0, 2, 2, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 2, 2, 0,
                      0, 0, 2, 0, 2, 0, 2, 0, 0, 0, 2, 0, 2, 0, 2, 0, 0,
                      0, 2, 2, 2, 2, 0, 2, 2, 0, 2, 2, 0, 2, 2, 2, 2, 0,
                      0, 2, 0, 0, 0, 0, 0, 2, 0, 2, 0, 0, 0, 0, 0, 2, 0,
                      0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0,
                      0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        self.next_dir = 0
        self.pacman = [pygame.Rect(160, 260, 20, 20), 0]
        self.ghosts = [[pygame.Rect(20, 20, 20, 20), 0],
                       [pygame.Rect(300, 20, 20, 20), 2],
                       [pygame.Rect(20, 340, 20, 20), 0],
                       [pygame.Rect(300, 340, 20, 20), 2]]

    def next_pos(self, next_dir, rect):
        """Advance rectangle by given direction."""
        if next_dir == 0: chng = (4, 0)
        if next_dir == 1: chng = (0, -4)
        if next_dir == 2: chng = (-4, 0)
        if next_dir == 3: chng = (0, 4)
        return rect.move(*chng)

    def rect_idx(self, rect):
        """Calculate tile index by rectangle."""
        return (rect.top / 20) * self.tiles_width + (rect.left / 20)

    def valid_pos(self, rect):
        """Return True iff character rectangle is valid on tiles."""
        prev_tile = self.tiles[self.rect_idx(rect)]
        next_tile = self.tiles[self.rect_idx(rect.move(19, 19))]
        on_track = rect.left % 20 == 0 or rect.top % 20 == 0
        return prev_tile != 0 and next_tile != 0 and on_track

    def move_rect(self, next_dir, curr_dir, rect):
        """
        Move character rectangle.
        Returns next character location and direction.
        """
        next_rect = self.next_pos(next_dir, rect)
        if self.valid_pos(next_rect):
            return (next_rect, next_dir)
        else:
            next_rect = self.next_pos(curr_dir, rect)
            if self.valid_pos(next_rect):
                return (next_rect, curr_dir)
        return (rect, curr_dir)

    def move_pacman(self):
        """Move pacman character."""
        rect, curr_dir = self.pacman
        tup = self.move_rect(self.next_dir, curr_dir, rect)
        self.pacman[0], self.pacman[1] = tup

    def move_ghosts(self):
        """Move ghost characters."""
        for tup in self.ghosts:
            rect = tup[0]
            curr_dir = next_dir = tup[1]
            if rect.top % 20 == 0 and rect.left % 20 == 0:
                next_dir = (curr_dir + random.choice((1, 3))) % 4
            tup[0], tup[1] = self.move_rect(next_dir, curr_dir, rect)

    def update(self):
        """Update tiles, score and running based on pacman location."""
        self.next_dir = self.pacman[1]

        idx = self.rect_idx(self.pacman[0])
        if self.tiles[idx] == 2:
            self.score += 1
            self.tiles[idx] = 1

        has_food = any(val == 2 for val in self.tiles)
        ghost_rects = [tup[0] for tup in self.ghosts]
        is_eaten = self.pacman[0].collidelist(ghost_rects) >= 0
        self.running = has_food and not is_eaten

    def draw(self):
        """Draw game on screen."""
        # Draw tiles

        for idx, val in enumerate(self.tiles):
            left = (idx % self.tiles_width) * 20
            top = (idx / self.tiles_width) * 20
            if val == 0:
                color = (0, 0, 128)
                pygame.draw.rect(screen, color, (left, top, 20, 20))
            else:
                color = (0, 0, 0)
                pygame.draw.rect(screen, color, (left, top, 20, 20))
            if val == 2:
                color = (255, 255, 255)
                pygame.draw.circle(screen, color, (left + 10, top + 10), 2)

        # Draw pacman.

        pacman_dir = pygame.transform.rotate(pacman_img, 90 * self.pacman[1])
        screen.blit(pacman_dir, self.pacman[0])

        # Draw ghosts.

        for val in self.ghosts:
            screen.blit(ghost_img, val[0])

        # Draw score.

        pygame.draw.rect(screen, (0, 0, 0), (0, 380, 100, 20))
        msg = 'Score: ' + str(self.score)
        text = font.render(msg , True, (255, 255, 255))
        screen.blit(text, (5, 382))

game = Game()

while True:

    event = pygame.event.poll()

    # Respond to key presses.

    if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()
    elif event.type == KEYDOWN:
        if event.key == K_UP:
            game.next_dir = 1
        elif event.key == K_RIGHT:
            game.next_dir = 0
        elif event.key == K_DOWN:
            game.next_dir = 3
        elif event.key == K_LEFT:
            game.next_dir = 2
        elif event.key == K_r:
            game.reset()
        elif event.key == K_q:
            pygame.event.post(pygame.event.Event(QUIT))

    if game.running:
        game.move_pacman()
        game.move_ghosts()
        game.update()

    game.draw()

    # Display next frame.

    pygame.display.flip()
    clock.tick(12)
