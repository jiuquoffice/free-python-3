"""
Cannon - hitting a target with a cannon.

Written by Grant Jenks
http://www.grantjenks.com/

Copyright (c) 2012 Grant Jenks

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to
deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
sell copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.

Exercises
1. Make the target smaller.
2. Make the ball larger.
3. Move the target off the ground.
"""

import sys, pygame
from pygame.locals import *
from random import randrange
from itertools import count

pygame.init()

font = pygame.font.Font(None, 14)
clock = pygame.time.Clock()
screen = pygame.display.set_mode((480, 480))

# Define colors.

white, black, purple = (255, 255, 255), (0, 0, 0), (200, 0, 200)

def reset():
    """Reset game settings."""
    global score, target
    score, target = 0, randrange(200, 450)

def redraw():
    """Redraw screen and settings."""
    global ball, xforce, yforce
    ball, xforce, yforce = None, 1.5, -6.0

    screen.fill(black)
    pygame.draw.line(screen, white, (0, 475), (480, 475), 11)
    pygame.draw.rect(screen, white, (20, 460, 10, 10))
    pygame.draw.line(screen, white, (25, 465), (35, 455), 3)
    pygame.draw.rect(screen, purple, (target, 450, 20, 20))

# Initialize start of game play.

reset()
redraw()

for counter in count():
    if counter % 5 == 0:
        clock.tick(24)

    event = pygame.event.poll()

    # Handle pygame events.

    if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()
    elif event.type == KEYDOWN:

        # Handle user input.

        if event.key == K_SPACE:
            ball = (30.0, 460.0, xforce, yforce)
        elif event.key == K_UP:
            yforce -= 0.1
        elif event.key == K_DOWN:
            yforce += 0.1
        elif event.key == K_RIGHT:
            xforce += 0.1
        elif event.key == K_LEFT:
            xforce -= 0.1
        elif event.key == K_r:
            redraw();
        elif event.key == K_q:
            pygame.event.post(pygame.event.Event(QUIT))

    if ball is not None:

        # Update the ball's position.

        east, south, right, down = ball

        down += 0.05
        east += right
        south += down

        ball = (east, south, right, down)

        # Draw the ball.

        ballrect = pygame.Rect(ball[0], ball[1], 3, 3)
        pygame.draw.rect(screen, white, ballrect)

        # Detect ball out of screen boundary.

        if not (0 < south < 480 and 0 < east < 480):
            ball = None

        # Detect ball hitting target.

        targetrect = pygame.Rect(target, 450, 20, 20)

        if targetrect.colliderect(ballrect):
            score += 1
            target = randrange(200, 450)
            redraw()

    # Draw text to the screen.

    pygame.draw.rect(screen, black, (0, 0, 120, 30))
    scoredisplay = font.render('score: ' + str(score), True, white)
    xdisplay = font.render('xforce: ' + str(xforce), True, white)
    ydisplay = font.render('yforce: ' + str(yforce), True, white)
    screen.blit(scoredisplay, (0, 0))
    screen.blit(xdisplay, (0, 10))
    screen.blit(ydisplay, (0, 20))

    pygame.display.flip()
