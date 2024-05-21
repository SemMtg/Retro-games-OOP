import blessed
import time

FPS = 30 # Frames per second.
COLOR = "blue"
PENGUIN = r"""
          _____
        ,888888b.
      .d888888888b
  _..-'.`*'_,88888b
,'..-..`"ad88888888b.
       ``-. `*Y888888b.
           \   `Y888888b.
           :     Y8888888b.
           :      Y88888888b.
           |    _,8ad88888888.
           : .d88888888888888b.
           \d888888888888888888
           8888;'''`88888888888
           888'     Y8888888888
           `Y8      :8888888888
            |`      '8888888888
            |        8888888888
            |        8888888888
            |        8888888888
            |       ,888888888P
            :       ;888888888'
             \      d88888888'
            _.>,    888888P'
          <,--''`.._>8888(
           `>__...--' `''`
"""

# This function should help you get started drawing shapes (that can be partially
# outside of the viewport). It is *NOT* object-oriented yet.

def draw_shape(term: blessed.Terminal, shape: str, left: int, top: int):
    # Split the shape into lines, ignoring extra newline chars at the start and at the end
    lines = shape.strip("\n").split("\n")
    # Iterate the lines
    for y_offset, line in enumerate(lines):
        if 0 <= top+y_offset < term.height: # Only draw lines that are within the terminal window
            x = left
            visible_line = line
            if x < 0: # Truncate the part of the line left of the viewport
                visible_line = line[-x:]
                x = 0
            if x+len(line) > term.width: # Truncate the part of the line right of viewport
                visible_line = line[:term.width-x]
            print(term.move_xy(x, top+y_offset) + visible_line, end="")

# What follows is an example to help you get started with the main loop.
# It is *NOT* object-oriented yet.

term = blessed.Terminal()

with term.fullscreen(), term.cbreak(), term.hidden_cursor():
    pressed_keys = []
    while True:
        # Clear the screen.
        print(term.clear, end="")
        print(getattr(term, COLOR), end="")
        draw_shape(term, PENGUIN, -10, 10)
        draw_shape(term, PENGUIN, term.width-20, 10)
        draw_shape(term, PENGUIN, term.width//2, -5)
        draw_shape(term, PENGUIN, term.width//2, term.height-15)

        # Draw whatever you want to draw.
        # It usually a good idea to use end="" to prevent printing a new line.
        print(term.move(9, 10) + term.cyan("Hi mom!"), end="")
        print(term.move(10, 10) + term.yellow("Pressed keys: ") + " ".join(pressed_keys), end="")

        # After everything has been printed, make sure to flush the print
        # output buffer. This may not happen automatically if your last
        # print didn't end in a new line character.
        print(end="", flush=True)

        # Wait for 1/FPS seconds, and append all keys that were
        # pressed within that time as strings in pressed_keys.
        pressed_keys.clear()
        until_time = time.time() + 1/FPS
        while True:
            remaining_time = until_time - time.time()
            if remaining_time <= 0:
                break
            key = term.inkey(remaining_time)
            if key:
                pressed_keys.append(key.name or str(key))
