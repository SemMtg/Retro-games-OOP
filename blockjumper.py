from __future__ import annotations
import time
import random
from retrogamelib import ShapeEntity, RectangleEntity, Game, get_color


JUMPER_NORMAL_SHAPE = r"""
 /---\
| o o |
 \---/
"""

JUMPER_JUMP_SHAPE = r"""
 /|||\
| O O |
 \---/
"""

JUMPER_RECOVER_SHAPE = r"""
 /---\
| - - |
 \---/
"""

JUMPER_DEAD_SHAPE = r"""
 /---\
| x x |
 \---/
"""

JUMPER_STATES = { # state_name: (shape, color,)
    'normal': (JUMPER_NORMAL_SHAPE, 'steelblue'),
    'jump': (JUMPER_JUMP_SHAPE, 'steelblue1'),
    'recover': (JUMPER_RECOVER_SHAPE, 'steelblue4'),
    'dead': (JUMPER_DEAD_SHAPE, 'firebrick2'),
}


class BlockJumperGame(Game):
    def __init__(self) -> None:
        super().__init__()
        self.__start_time = time.time()
        self.__game_duration = 90
        self.__score = 0


    def get_score(self):
        return self.__score

    def calculate_progress(self):
        elapsed_time = time.time() - self.__start_time
        progress = elapsed_time / self.__game_duration * 100
        if progress >= 100:
            self.end_game()
            self.print_message("Congratulations! You've completed the game.")
        return progress

    def increment_score(self):
        self.__score += 1

    def create_block(self):
        # Randomly decide block size and speed and symbol
        color = random.choice(['red', 'green', 'yellow', ' magenta', 'blue'])
        symbol = random.choice(['@', '#', '$', '&', '0', 'X'])
        width = random.randint(1, 25)
        height = random.randint(1, 25)
        speed = 1

        direction = random.choice(['left', 'right', 'top', 'bottom'])

        if direction == 'left':
            x = -width
            y = random.randint(0, game.get_terminal_size()[1] - height)
        elif direction == 'right':
            x = game.get_terminal_size()[0]
            y = random.randint(0, game.get_terminal_size()[1] - height)
        elif direction == 'top':
            x = random.randint(0, game.get_terminal_size()[0] - width)
            y = -height
        elif direction == 'bottom':
            x = random.randint(0, game.get_terminal_size()[0] - width)
            y = game.get_terminal_size()[1]

        block = Block(x, y, color, width, height, symbol, speed, direction)
        self.add_entity(block)


class Jumper(ShapeEntity):
    def __init__(self, x: float, y: float, initial_state):
        self.__state = initial_state
        self.__shape, self.__color = JUMPER_STATES[initial_state]
        super().__init__(x, y, get_color(self.__color), self.__shape)
        self.__state_time = time.time()
        self.__speed = 1

    def update(self, game: Game):
        current_time = time.time()

        for block in game.get_entities_of_type(Block):
            if self.collides_with(block) and self.__state != 'jump':
                game.remove_entity(self)
                game.end_game()
                game.print_message(f"You scored {game.get_score()} points!")
                return

        # Handle state transitions based on time and current state
        if self.__state == 'jump' and (current_time - self.__state_time) >= 1:
            self.change_state('recover', current_time, game)
        elif self.__state == 'recover' and (current_time - self.__state_time) >= 2:
            self.change_state('normal', current_time, game)

        # Handle movement (keyboard input)
        self.handle_movement(game)
        # Check if space is pressed for jumping
        if game.was_key_pressed(' ') and self.__state == 'normal':
            self.jump(game)

    def handle_movement(self, game: Game):
        if game.was_key_pressed('w'):
            self.y = max(0, self.y - self.__speed)
        if game.was_key_pressed('s'):
            self.y = min(game.get_terminal_size()[1] - self.get_size()[1], self.y + self.__speed)
        if game.was_key_pressed('a'):
            self.x = max(0, self.x - self.__speed)
        if game.was_key_pressed('d'):
            self.x = min(game.get_terminal_size()[0] - self.get_size()[0], self.x + self.__speed)

    def change_state(self, new_state: str, current_time: float, game: Game):
        self.__state = new_state
        self.__state_time = current_time
        self.__shape, self.__color = JUMPER_STATES[new_state]
        self.set_shape(self.__shape)
        self.color = get_color(self.__color)

    def jump(self, game: Game):
        self.change_state('jump', time.time(), game)


class Block(RectangleEntity):
    def __init__(self, x: float, y: float, color: str, width: int, height: int, character: str, speed: int, direction: str) -> None:
        super().__init__(x, y, get_color(color), width, height, character)
        self.__speed = speed
        self.__direction = direction

    def update(self, game: Game) -> None:
        if self.__direction == 'left':
            self.x += self.__speed
        elif self.__direction == 'right':
            self.x -= self.__speed
        elif self.__direction == 'top':
            self.y += self.__speed
        elif self.__direction == 'bottom':
            self.y -= self.__speed

        term_width, term_height = game.get_terminal_size()
        width, height = self.get_size()

        # Decrease size if moving off the screen
        if self.__direction in {'left', 'right'} and (self.x < 0 or self.x + width > term_width):
            if width > 0:
                self.set_size(width - 1, height)
        elif self.__direction in {'top', 'bottom'} and (self.y < 0 or self.y + height > term_height) and height > 0:
            self.set_size(width, height - 1)

        # Remove block if it is completely out of the screen
        if self.get_size() == (0, 0):
            game.remove_entity(self)


class ProgressBar(RectangleEntity):
    def __init__(self, x: float, y: float, width: int, height: int) -> None:
        super().__init__(x, y, get_color("red"), width, height, '#')
        self.__last_update_time = time.time()

    def update(self, game: Game) -> None:
        current_time = time.time()
        if current_time - self.__last_update_time >= 1:
            game.increment_score()
            self.__last_update_time = current_time
        
        progress = game.calculate_progress()
        term_width, _ = game.get_terminal_size()
        filled_length = int(term_width * (progress / 100))
        self.set_size(filled_length, self.get_size()[1])
        

if __name__ == '__main__':
    game = BlockJumperGame()
    jumper = Jumper(10, 10, 'normal')
    progress_bar = ProgressBar(0, game.get_terminal_size()[1] - 1, 0, 1)
    for _ in range(10):
        game.create_block()
    game.add_entity(progress_bar)
    game.add_entity(jumper)
    game.run()
