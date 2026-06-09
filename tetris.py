#!/usr/bin/env python3
"""俄罗斯方块 - 使用 pygame 实现"""

from __future__ import annotations

import random
import sys

import pygame

# 游戏常量
COLS = 10
ROWS = 20
CELL_SIZE = 30
SIDEBAR_WIDTH = 180
WIDTH = COLS * CELL_SIZE + SIDEBAR_WIDTH
HEIGHT = ROWS * CELL_SIZE
FPS = 60

# 颜色
BLACK = (15, 15, 25)
GRID_COLOR = (35, 35, 50)
WHITE = (240, 240, 245)
GRAY = (120, 120, 140)
RED = (220, 60, 60)

# 七种方块形状（旋转状态）
SHAPES = {
    "I": [
        [[0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0]],
        [[0, 0, 1, 0], [0, 0, 1, 0], [0, 0, 1, 0], [0, 0, 1, 0]],
    ],
    "O": [
        [[1, 1], [1, 1]],
    ],
    "T": [
        [[0, 1, 0], [1, 1, 1], [0, 0, 0]],
        [[0, 1, 0], [0, 1, 1], [0, 1, 0]],
        [[0, 0, 0], [1, 1, 1], [0, 1, 0]],
        [[0, 1, 0], [1, 1, 0], [0, 1, 0]],
    ],
    "S": [
        [[0, 1, 1], [1, 1, 0], [0, 0, 0]],
        [[0, 1, 0], [0, 1, 1], [0, 0, 1]],
    ],
    "Z": [
        [[1, 1, 0], [0, 1, 1], [0, 0, 0]],
        [[0, 0, 1], [0, 1, 1], [0, 1, 0]],
    ],
    "J": [
        [[1, 0, 0], [1, 1, 1], [0, 0, 0]],
        [[0, 1, 1], [0, 1, 0], [0, 1, 0]],
        [[0, 0, 0], [1, 1, 1], [0, 0, 1]],
        [[0, 1, 0], [0, 1, 0], [1, 1, 0]],
    ],
    "L": [
        [[0, 0, 1], [1, 1, 1], [0, 0, 0]],
        [[0, 1, 0], [0, 1, 0], [0, 1, 1]],
        [[0, 0, 0], [1, 1, 1], [1, 0, 0]],
        [[1, 1, 0], [0, 1, 0], [0, 1, 0]],
    ],
}

SHAPE_COLORS = {
    "I": (0, 240, 240),
    "O": (240, 240, 0),
    "T": (180, 0, 240),
    "S": (0, 240, 0),
    "Z": (240, 0, 0),
    "J": (0, 0, 240),
    "L": (240, 160, 0),
}


class Piece:
    def __init__(self, shape_name: str | None = None):
        self.name = shape_name or random.choice(list(SHAPES.keys()))
        self.rotations = SHAPES[self.name]
        self.rotation_index = 0
        self.color = SHAPE_COLORS[self.name]
        self.x = COLS // 2 - len(self.shape[0]) // 2
        self.y = 0

    @property
    def shape(self) -> list[list[int]]:
        return self.rotations[self.rotation_index]

    def rotated_shape(self) -> list[list[int]]:
        return self.rotations[(self.rotation_index + 1) % len(self.rotations)]


class TetrisGame:
    def __init__(self):
        self.board: list[list[str | None]] = [
            [None for _ in range(COLS)] for _ in range(ROWS)
        ]
        self.current = Piece()
        self.next_piece = Piece()
        self.score = 0
        self.lines_cleared = 0
        self.level = 1
        self.game_over = False
        self.fall_time = 0
        self.fall_speed = 500  # 毫秒

        if not self.is_valid(self.current.shape, self.current.x, self.current.y):
            self.game_over = True

    def is_valid(self, shape: list[list[int]], x: int, y: int) -> bool:
        for row_idx, row in enumerate(shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    board_x = x + col_idx
                    board_y = y + row_idx
                    if board_x < 0 or board_x >= COLS or board_y >= ROWS:
                        return False
                    if board_y >= 0 and self.board[board_y][board_x] is not None:
                        return False
        return True

    def lock_piece(self):
        for row_idx, row in enumerate(self.current.shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    board_y = self.current.y + row_idx
                    board_x = self.current.x + col_idx
                    if board_y >= 0:
                        self.board[board_y][board_x] = self.current.name

        cleared = self.clear_lines()
        if cleared:
            points = [0, 100, 300, 500, 800]
            self.score += points[min(cleared, 4)] * self.level
            self.lines_cleared += cleared
            self.level = self.lines_cleared // 10 + 1
            self.fall_speed = max(100, 500 - (self.level - 1) * 40)

        self.current = self.next_piece
        self.next_piece = Piece()
        if not self.is_valid(self.current.shape, self.current.x, self.current.y):
            self.game_over = True

    def clear_lines(self) -> int:
        new_board = [row for row in self.board if any(cell is None for cell in row)]
        cleared = ROWS - len(new_board)
        while len(new_board) < ROWS:
            new_board.insert(0, [None for _ in range(COLS)])
        self.board = new_board
        return cleared

    def move(self, dx: int, dy: int) -> bool:
        if self.game_over:
            return False
        new_x = self.current.x + dx
        new_y = self.current.y + dy
        if self.is_valid(self.current.shape, new_x, new_y):
            self.current.x = new_x
            self.current.y = new_y
            return True
        return False

    def rotate(self):
        if self.game_over:
            return
        new_shape = self.current.rotated_shape()
        # 简单踢墙：尝试左右偏移
        for kick in (0, -1, 1, -2, 2):
            if self.is_valid(new_shape, self.current.x + kick, self.current.y):
                self.current.rotation_index = (
                    self.current.rotation_index + 1
                ) % len(self.current.rotations)
                self.current.x += kick
                return

    def hard_drop(self):
        if self.game_over:
            return
        while self.move(0, 1):
            self.score += 2
        self.lock_piece()

    def update(self, dt: int):
        if self.game_over:
            return
        self.fall_time += dt
        if self.fall_time >= self.fall_speed:
            self.fall_time = 0
            if not self.move(0, 1):
                self.lock_piece()

    def reset(self):
        self.__init__()


def draw_cell(
    surface: pygame.Surface,
    x: int,
    y: int,
    color: tuple[int, int, int],
    offset_x: int = 0,
    cell_size: int = CELL_SIZE,
):
    rect = pygame.Rect(
        offset_x + x * cell_size + 1,
        y * cell_size + 1,
        cell_size - 2,
        cell_size - 2,
    )
    pygame.draw.rect(surface, color, rect, border_radius=3)
    highlight = tuple(min(c + 40, 255) for c in color)
    pygame.draw.line(surface, highlight, rect.topleft, rect.topright, 2)
    shadow = tuple(max(c - 40, 0) for c in color)
    pygame.draw.line(surface, shadow, rect.bottomleft, rect.bottomright, 2)


def draw_board(surface: pygame.Surface, game: TetrisGame, font: pygame.font.Font):
    # 游戏区域背景
    board_rect = pygame.Rect(0, 0, COLS * CELL_SIZE, HEIGHT)
    pygame.draw.rect(surface, (20, 20, 35), board_rect)

    # 网格线
    for x in range(COLS + 1):
        pygame.draw.line(
            surface, GRID_COLOR, (x * CELL_SIZE, 0), (x * CELL_SIZE, HEIGHT)
        )
    for y in range(ROWS + 1):
        pygame.draw.line(
            surface, GRID_COLOR, (0, y * CELL_SIZE), (COLS * CELL_SIZE, y * CELL_SIZE)
        )

    # 已固定的方块
    for row_idx, row in enumerate(game.board):
        for col_idx, cell in enumerate(row):
            if cell:
                draw_cell(surface, col_idx, row_idx, SHAPE_COLORS[cell])

    # 当前下落方块
    if not game.game_over:
        for row_idx, row in enumerate(game.current.shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    draw_cell(
                        surface,
                        game.current.x + col_idx,
                        game.current.y + row_idx,
                        game.current.color,
                    )

    # 侧边栏
    sidebar_x = COLS * CELL_SIZE + 15
    title = font.render("俄罗斯方块", True, WHITE)
    surface.blit(title, (sidebar_x, 20))

    labels = [
        f"分数: {game.score}",
        f"消除行: {game.lines_cleared}",
        f"等级: {game.level}",
    ]
    for i, text in enumerate(labels):
        surface.blit(font.render(text, True, WHITE), (sidebar_x, 70 + i * 30))

    # 下一个方块预览
    surface.blit(font.render("下一个:", True, GRAY), (sidebar_x, 180))
    preview_x = sidebar_x + 10
    preview_y = 210
    for row_idx, row in enumerate(game.next_piece.shape):
        for col_idx, cell in enumerate(row):
            if cell:
                draw_cell(
                    surface,
                    col_idx,
                    row_idx,
                    game.next_piece.color,
                    offset_x=preview_x,
                    cell_size=20,
                )

    # 操作说明
    help_lines = [
        "操作说明:",
        "← → 移动",
        "↑ 旋转",
        "↓ 加速下落",
        "空格 硬降",
        "R 重新开始",
        "ESC 退出",
    ]
    for i, line in enumerate(help_lines):
        color = GRAY if i == 0 else (160, 160, 180)
        surface.blit(
            font.render(line, True, color),
            (sidebar_x, 320 + i * 22),
        )

    if game.game_over:
        overlay = pygame.Surface((COLS * CELL_SIZE, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))
        over_font = pygame.font.SysFont("pingfang sc, microsoft yahei, sans-serif", 36)
        msg = over_font.render("游戏结束!", True, RED)
        surface.blit(msg, msg.get_rect(center=(COLS * CELL_SIZE // 2, HEIGHT // 2 - 20)))
        hint = font.render("按 R 重新开始", True, WHITE)
        surface.blit(
            hint, hint.get_rect(center=(COLS * CELL_SIZE // 2, HEIGHT // 2 + 20))
        )


def main():
    pygame.init()
    pygame.display.set_caption("俄罗斯方块")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("pingfang sc, microsoft yahei, sans-serif", 18)

    game = TetrisGame()

    running = True
    while running:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    game.reset()
                elif not game.game_over:
                    if event.key == pygame.K_LEFT:
                        game.move(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        game.move(1, 0)
                    elif event.key == pygame.K_DOWN:
                        if game.move(0, 1):
                            game.score += 1
                    elif event.key == pygame.K_UP:
                        game.rotate()
                    elif event.key == pygame.K_SPACE:
                        game.hard_drop()

        game.update(dt)
        screen.fill(BLACK)
        draw_board(screen, game, font)
        pygame.display.flip()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
