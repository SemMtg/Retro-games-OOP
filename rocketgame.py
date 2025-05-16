from retrogamelib import ShapeEntity, Game, get_color
import random
import time

ROCKET = r"""
   __
   \ \_____
###[==_____>
   /_/
"""

ASTEROID1 = r"""
/\
\/
"""

ASTEROID2 = r"""
 /\
<XX>
 \/
"""

BULLET = r"o"

# Define the horizontal speeds and corresponding colors
HORIZONTAL_SPEEDS = [1, 1.3, 1.8]
SPEED_COLORS = ["green", "yellow", "red"]


class RocketGame(Game):
    def __init__(self) -> None:
        super().__init__()
        self.__score = 0
        self.next_asteroid_spawn_time = time.time()

    def increment_score(self, points: int):
        self.__score += points

    def get_score(self):
        return self.__score

    def maybe_spawn_asteroid(self):
        # Check if it's time to spawn a new asteroid
        if time.time() >= self.next_asteroid_spawn_time:
            create_asteroid()
            # Set next spawn time to current time plus desired interval
            self.next_asteroid_spawn_time = time.time() + 0.2  # Delay of 0.2


class Bullet(ShapeEntity):
    def __init__(self, x: float, y: float, color: str, shape: str) -> None:
        super().__init__(x, y, get_color(color), shape)
    
    def update(self, game: Game) -> None:
        # Move the bullet to the right
        self.x += 2  # Speed of the bullet
        # Remove the bullet if it goes off screen
        if self.x >= game.get_terminal_size()[0]:
            game.remove_entity(self)


class Rocket(ShapeEntity):
    def __init__(self, x: float, y: float, color: str, shape: str) -> None:
        super().__init__(x, y, get_color(color), shape)
        self.__last_shot_time = 0
        self.__shooting_cooldown = 0.5

    def update(self, game: Game) -> None:
        move_up = game.was_key_pressed('w')
        move_down = game.was_key_pressed('s')
        fire_bullet = game.was_key_pressed(' ')

        # Check for collision with asteroids
        for asteroid in game.get_entities_of_type(Asteroid):
            if self.collides_with(asteroid):
                game.remove_entity(self)
                game.end_game()
                game.print_message(f"You scored {game.get_score()} points!")
                return

        if move_up:
            self.y -= 1 # Move up
        if move_down:
            self.y += 1  # Move down
        if fire_bullet and (time.time() - self.__last_shot_time) >= self.__shooting_cooldown:
            self.fire_bullet(game)
            self.__last_shot_time = time.time()

        # Ensure the rocket does not move out of the screen boundaries
        max_y = game.get_terminal_size()[1] - self.get_size()[1]
        if self.y < 0:
            self.y = 0
        elif self.y > max_y:
            self.y = max_y

    def fire_bullet(self, game: Game):
        bullet_x = self.x + self.get_size()[0]
        bullet_y = self.y + self.get_size()[1] // 2  # Middle of the rocket
        game.add_entity(Bullet(bullet_x, bullet_y, 'blue', BULLET))


class Asteroid(ShapeEntity):
    def __init__(self, x: float, y: float, color: str, shape: str, horizontal_speed: float, vertical_speed: float, size: str) -> None:
        super().__init__(x, y, get_color(color), shape)
        self.__horizontal_speed = horizontal_speed
        self.__vertical_speed = vertical_speed
        self.__size = size

    def split_asteroid(self, asteroid):
        x, y = asteroid.x, asteroid.y
        speed = random.choice(HORIZONTAL_SPEEDS)
        vertical_speed1 = 0.5
        vertical_speed2 = -0.5
        small_asteroid1 = Asteroid(x, y, "green", ASTEROID1, speed, vertical_speed1, size="small")
        small_asteroid2 = Asteroid(x, y, "green", ASTEROID1, speed, vertical_speed2, size="small")
        game.add_entity(small_asteroid1)
        game.add_entity(small_asteroid2)

    def update(self, game: Game) -> None:
        self.x -= self.__horizontal_speed
        self.y += self.__vertical_speed

        # Ensure the asteroid is removed when of the screen
        if self.x <= 0 or self.y >= game.get_terminal_size()[1]:
            game.remove_entity(self)

        # Check for collision with bullets
        for bullet in game.get_entities_of_type(Bullet):
            if self.collides_with(bullet):
                game.remove_entity(bullet)
                game.increment_score(1)

                if self.__size == "small":
                    game.remove_entity(self)
                else: # Split an asteroid if it is a large sized asteroid
                    game.remove_entity(self)
                    self.split_asteroid(self)

        # Check if enough time has passed to spawn a asteroid
        game.maybe_spawn_asteroid()

    def get_type(self) -> str:
        return self.__size


def create_asteroid():
    size = random.choice(["large", "small"])
    asteroid_type = ASTEROID2 if size == "large" else ASTEROID1
    horizontal_speed = random.choice(HORIZONTAL_SPEEDS)
    color = SPEED_COLORS[HORIZONTAL_SPEEDS.index(horizontal_speed)]
    vertical_speed = random.uniform(0, 0.2)
    asteroid = Asteroid(game.get_terminal_size()[0], random.randint(0, game.get_terminal_size()[1] - 1), color, asteroid_type, horizontal_speed, vertical_speed, size)
    game.add_entity(asteroid)


if __name__ == '__main__':
    # create the entities
    asteroid_types = [ASTEROID1, ASTEROID2]
    game = RocketGame()
    rocket = Rocket(0, game.get_terminal_size()[1]/2, "blue", ROCKET)
    game.add_entity(rocket)

    for _ in range(1):
        create_asteroid()

    game.run()
