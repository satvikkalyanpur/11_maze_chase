
import pygame
from game.maze import generate_maze, CELL
from game.entities import Player, Enemy

COLS, ROWS = 13, 11
WIDTH = COLS * CELL
HEIGHT = ROWS * CELL + 50
FPS = 60


class GameEngine:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Maze Chase")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace", 22)
        self.big_font = pygame.font.SysFont("monospace", 38, bold=True)
        self.reset()

    def reset(self):
        self.walls = generate_maze(COLS, ROWS)
        self.player = Player(0, 0)

        # Task 1: Three independent enemies.
        self.enemies = [
            Enemy(ROWS - 1, COLS - 1),  # bottom-right
            Enemy(0, COLS - 1),         # top-right
            Enemy(ROWS - 1, 0),         # bottom-left
        ]

        # Task 2: All enemies start with interval 20.
        for enemy in self.enemies:
            enemy.move_interval = 20
            enemy.frozen = False

        # Task 2: Speed progression timer.
        self.speed_start_time = pygame.time.get_ticks()

        # Task 3: Power pellet.
        # Pellet is placed at a valid maze cell.
        pellet_row = ROWS // 2
        pellet_col = 1

        pellet_x = pellet_col * CELL + CELL // 2
        pellet_y = pellet_row * CELL + CELL // 2

        self.power_pellet = pygame.Rect(
            pellet_x - 8,
            pellet_y - 8,
            16,
            16
        )

        self.pellet_collected = False

        # Task 3: 300 frames = 5 seconds at 60 FPS.
        self.freeze_frames_remaining = 0

        self.exit_rect = pygame.Rect(
            (COLS // 2) * CELL + 5,
            (ROWS // 2) * CELL + 5,
            CELL - 10,
            CELL - 10
        )

        self.caught = False
        self.won = False

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.reset()

        return True

    def update(self):
        if self.caught or self.won:
            return

        keys = pygame.key.get_pressed()
        self.player.move(keys, self.walls, ROWS, COLS)

        # ---------------------------------------------------------
        # Task 2: Speed Up Over Time
        # ---------------------------------------------------------

        elapsed_time = (
            pygame.time.get_ticks() - self.speed_start_time
        )

        speed_steps = elapsed_time // 15000

        current_interval = max(
            5,
            20 - (speed_steps * 2)
        )

        # All three enemies use the same current movement interval.
        for enemy in self.enemies:
            enemy.move_interval = current_interval

        # ---------------------------------------------------------
        # Task 3: Power Pellet / Freeze Enemies
        # ---------------------------------------------------------

        # Check whether the player collected the pellet.
        if (
            not self.pellet_collected
            and self.player.rect.colliderect(self.power_pellet)
        ):
            self.pellet_collected = True

            # Freeze all three enemies for exactly 300 frames.
            self.freeze_frames_remaining = 300

            for enemy in self.enemies:
                enemy.frozen = True

        # Handle the active freeze countdown.
        if self.freeze_frames_remaining > 0:
            self.freeze_frames_remaining -= 1

            if self.freeze_frames_remaining == 0:
                for enemy in self.enemies:
                    enemy.frozen = False

        # ---------------------------------------------------------
        # Task 1: Independently update all three enemies.
        # Enemy.update() performs the existing BFS pathfinding.
        # Frozen enemies immediately return from Enemy.update().
        # ---------------------------------------------------------

        for enemy in self.enemies:
            enemy.update(
                self.walls,
                self.player,
                ROWS,
                COLS
            )

        # Check collision with every enemy.
        for enemy in self.enemies:
            if self.player.rect.colliderect(enemy.rect):
                self.caught = True
                break

        # Existing EXIT behavior.
        if self.player.rect.colliderect(self.exit_rect):
            self.won = True

    def draw(self):
        self.screen.fill((230, 220, 210))

        wc = (50, 40, 60)

        for r in range(ROWS):
            for c in range(COLS):
                x, y = c * CELL, r * CELL
                w = self.walls[r][c]

                if w[0]:
                    pygame.draw.line(
                        self.screen,
                        wc,
                        (x, y),
                        (x + CELL, y),
                        3
                    )

                if w[1]:
                    pygame.draw.line(
                        self.screen,
                        wc,
                        (x, y + CELL),
                        (x + CELL, y + CELL),
                        3
                    )

                if w[2]:
                    pygame.draw.line(
                        self.screen,
                        wc,
                        (x + CELL, y),
                        (x + CELL, y + CELL),
                        3
                    )

                if w[3]:
                    pygame.draw.line(
                        self.screen,
                        wc,
                        (x, y),
                        (x, y + CELL),
                        3
                    )

        # Existing EXIT.
        pygame.draw.rect(
            self.screen,
            (80, 200, 80),
            self.exit_rect,
            border_radius=4
        )

        lbl = self.font.render(
            "EXIT",
            True,
            (20, 80, 20)
        )

        self.screen.blit(
            lbl,
            (
                self.exit_rect.x + 2,
                self.exit_rect.y + 6
            )
        )

        # Task 3: Draw the power pellet while it has not been collected.
        if not self.pellet_collected:
            pygame.draw.circle(
                self.screen,
                (255, 220, 0),
                self.power_pellet.center,
                8
            )

            pygame.draw.circle(
                self.screen,
                (255, 245, 120),
                self.power_pellet.center,
                4
            )

        self.player.draw(self.screen)

        # Task 1: Draw all three enemies.
        # Frozen enemies display their frozen indicator.
        for enemy in self.enemies:
            enemy.draw(self.screen)

        # HUD.
        hud = pygame.Rect(
            0,
            ROWS * CELL,
            WIDTH,
            50
        )

        pygame.draw.rect(
            self.screen,
            (30, 30, 50),
            hud
        )

        # Task 2: Display current enemy movement interval.
        info = self.font.render(
            f"Enemy interval: {self.enemies[0].move_interval}    R=Restart",
            True,
            (200, 200, 200)
        )

        self.screen.blit(
            info,
            (
                8,
                ROWS * CELL + 14
            )
        )

        # Task 3: Display remaining freeze time when active.
        if self.freeze_frames_remaining > 0:
            freeze_seconds = (
                self.freeze_frames_remaining + 59
            ) // 60

            freeze_text = self.font.render(
                f"FROZEN: {freeze_seconds}s",
                True,
                (100, 220, 255)
            )

            self.screen.blit(
                freeze_text,
                (
                    WIDTH - freeze_text.get_width() - 8,
                    ROWS * CELL + 14
                )
            )

        if self.caught:
            self._overlay(
                "CAUGHT!",
                (220, 60, 60)
            )

        if self.won:
            self._overlay(
                "ESCAPED!",
                (80, 220, 80)
            )

        pygame.display.flip()

    def _overlay(self, text, color):
        surf = pygame.Surface(
            (WIDTH, ROWS * CELL),
            pygame.SRCALPHA
        )

        surf.fill((0, 0, 0, 140))
        self.screen.blit(
            surf,
            (0, 0)
        )

        msg = self.big_font.render(
            text,
            True,
            color
        )

        sub = self.font.render(
            "Press R to Restart",
            True,
            (200, 200, 200)
        )

        self.screen.blit(
            msg,
            (
                WIDTH // 2 - msg.get_width() // 2,
                ROWS * CELL // 2 - 30
            )
        )

        self.screen.blit(
            sub,
            (
                WIDTH // 2 - sub.get_width() // 2,
                ROWS * CELL // 2 + 20
            )
        )

    def run(self):
        running = True

        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()

