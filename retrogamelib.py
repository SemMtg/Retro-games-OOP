from __future__ import annotations # This allows you to use circular dependencies in type hints.
from abc import ABC, abstractmethod
import blessed
import time

FPS = 30 # Frames per second.

terminal = blessed.Terminal()


class Entity(ABC):
    def __init__(self, x: float, y: float, color: str) -> None:
        self.x = x
        self.y = y
        self.color = color
    
    @abstractmethod
    def update(self, game: Game) -> None:
        pass

    @abstractmethod
    def draw(self, terminal: blessed.Terminal):
        pass

    # Checks if the Entity has collided with another entity.
    def collides_with(self, other: Entity) -> bool:
        other_x, other_y = other.x, other.y
        other_width, other_height = other.get_size()
        self_width, self_height = self.get_size()

        return (
            self.x < other_x + other_width and
            self.x + self_width > other_x and
            self.y < other_y + other_height and
            self.y + self_height > other_y
        )

    @abstractmethod
    def get_size(self) -> tuple:
        pass


class ShapeEntity(Entity):
    def __init__(self, x: float, y: float, color: str, shape: str) -> None:
        super().__init__(x, y, color)
        self.__shape = shape
    
    @abstractmethod
    def update(self, game: Game) -> None:
        pass

    # Draws the shape of the entity in the terminal on its set position.
    def draw(self, terminal: blessed.Terminal):
        lines = self.__shape.strip("\n").split("\n")

        for y_offset, line in enumerate(lines):
            y = int(self.y) + y_offset
            if 0 <= y < terminal.height:
                x = int(self.x)
                visible_line = line
                if x < 0:
                    visible_line = line[-x:]
                    x = 0
                if x + len(visible_line) > terminal.width:
                    visible_line = visible_line[:terminal.width - x]
                if visible_line:
                    print(terminal.move_xy(x, y) + self.color + visible_line, end="")

    def get_size(self) -> tuple:
        """Return the width[0], and the height[1] of the ShapeEntity
        Height is calculated by the amount of lines the shape has
        Width is calculated by the longest line the shape has

        Returns:
            tuple: self.width, self.height
        """
        lines = self.__shape.strip().split('\n')
        height = len(lines)
        width = max(len(line) for line in lines)
        return width, height
    
    def set_shape(self, shape: str):
        self.__shape = shape


class RectangleEntity(Entity):
    def __init__(self, x: float, y: float, color: str, width: int, height: int, character: str) -> None:
        super().__init__(x, y, color)
        self.__width = width
        self.__height = height
        self.__character = character

    def update(self, game: Game) -> None:
        return None

    # Draws the rectangle entity on its set position.
    def draw(self, terminal: blessed.Terminal):
        for dy in range(self.__height):
            y = int(self.y) + dy
            if 0 <= y < terminal.height:
                line = (self.color + self.__character * self.__width)[:terminal.width - int(self.x)]
                print(terminal.move_xy(int(self.x), y) + line, end="")
    
    
    def get_size(self) -> tuple:
        """Return the width[0], and the height[1] of the rectangle entity

        Returns:
            tuple: self.width, self.height
        """
        return self.__width, self.__height
    
    def set_size(self, width: int, height: int):
        self.__width = width
        self.__height = height

    def set_character(self, character: str):
        self.__character = character


class Game:
    def __init__(self) -> None:
        self.__entities: list[Entity] = []
        self.__pressed_keys = []
        self.__game_over = False

    def run(self):
        # Implementation of the game loop
        with terminal.fullscreen(), terminal.cbreak(), terminal.hidden_cursor():
            while True:
                self.collect_keys()

                if self.__game_over or self.was_key_pressed('q'):
                    self.end_game()
                    break

                for entity in self.__entities:
                    entity.update(self)

                self.clear_screen()
                self.draw_entities()
                self.print_score()
                print(end="", flush=True)

    def collect_keys(self):
        """Collect all keys pressed during the frame duration."""
        self.__pressed_keys.clear()
        frame_end = time.time() + (1 / FPS)
        while time.time() < frame_end:
            key = terminal.inkey(timeout=frame_end - time.time())
            if key:
                self.__pressed_keys.append(key.name or str(key).lower())

    def clear_screen(self):
        print(terminal.home + terminal.clear, end="")

    def draw_entities(self):
        for entity in self.__entities:
            entity.draw(terminal)

    def get_entities_of_type(self, type_: type) -> list[Entity]:
        return [entity for entity in self.__entities if isinstance(entity, type_)]

    def was_key_pressed(self, key: str) -> bool:
        """Check if a specific key was pressed during the frame."""
        return key in self.__pressed_keys

    @abstractmethod
    def get_score(self):
        pass

    def print_score(self):
        score_str = f"Score: {self.get_score()}"
        score_x = terminal.width - len(score_str) - 1
        score_y = 0
        print(terminal.move_xy(score_x, score_y) + terminal.white + score_str, end='')

    def add_entity(self, entity: Entity):
        self.__entities.append(entity)

    def remove_entity(self, entity: Entity):
        self.__entities.remove(entity)

    def get_terminal_size(self):
        """Return the width[0] and height[1] of the blessed terminal in integers

        Returns:
            width: the width of the blessed terminal
            height: the height of the blessed terminal
        """
        return terminal.width, terminal.height

    def end_game(self):
        self.__game_over = True

    def print_message(self, message: str):
        self.clear_screen()
        print(terminal.move_xy(0, 0) + message)
        time.sleep(3)
        print(terminal.clear)


def get_color(color_name: str):
    """Retrieve the color attribute from the terminal based on a color name string."""
    color_map = {
        "black": terminal.black,
        "red": terminal.red,
        "green": terminal.green,
        "yellow": terminal.yellow,
        "blue": terminal.blue,
        "magenta": terminal.magenta,
        "cyan": terminal.cyan,
        "white": terminal.white,
        "steelblue": terminal.steelblue,
        "steelblue1": terminal.steelblue1,
        "steelblue4": terminal.steelblue4,
        "firebrick2": terminal.firebrick2
    }
    return color_map.get(color_name.lower(), terminal.white)
