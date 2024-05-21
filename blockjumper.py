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
