import math


class Alphanumeric:
    width: float
    height: float
    waypoints: List[Tuple[float, float]]

    # Simple constructor
    def __init__(self, waypoints: List[Tuple[int, int]]):
        # Get bounds
        leftmost = min(coord[0] for coord in waypoints)
        rightmost = max(coord[0] for coord in waypoints)
        botmost = min(coord[1] for coord in waypoints)
        topmost = max(coord[1] for coord in waypoints)

        # Compute dimensions by bounds
        self.width = float(rightmost - leftmost)
        self.height = float(topmost - botmost)

        # Extra stuff to force each item to be float if it wasn't already explicitly so
        self.waypoints = [tuple(float(v) for v in coord) for coord in waypoints]

    # Return a copy of this letter, scaled about (0,0) by the given amount
    def scale(self, scale: float):
        return Alphanumeric([tuple(v * scale for v in coord) for coord in self.waypoints])

    def offset(self, offset: Tuple[float, float]):
        return Alphanumeric([tuple(v + o for v, o in zip(coord, offset)) for coord in self.waypoints])

    def get_points(self, argument):
        """Dispatch method"""
        method_name = 'character' + str(argument)
        # Get the method from 'self'. Default to a lambda.
        method = getattr(self, method_name, lambda: "Invalid")
        # Call the method as we return it
        return method()


def get_letter(l):
    # Will eventually return an appropriate alphanumeric for the given letter
    method_name = 'character' + str(l)
    # Get the method from 'self'. Default to a lambda.
    method = getattr(method_name, lambda: "Invalid")
    # Call the method as we return it
    return method()


# Convert a string to a sequence of alphanumeric letters
def write(string: str, scale: float) -> List[Tuple(float, float)]:
    # This tracks where we are currently writing
    cursor = (0, 0)

    # Initialize waypoint list
    waypoints = [cursor]

    # Iterate over letters
    for letter in string:
        # Get the appropriate letter
        alpha = get_letter(letter)

        # Scale it
        alpha = alpha.scale(scale)

        # Find its width
        w = alpha.width

        # Offset it by cursor
        alpha = alpha.offset(cursor)

        # Append its waypoints to the list
        waypoints = waypoints + alpha.waypoints

        # Finally, we update the cursor to be to the right of the letter
        cursor = (cursor[0] + w, 0)

    # Return the full list of waypoints
    return waypoints


def character_A() -> Alphanumeric:
    points = [[0.0, 0.0],
              [0.0, 1.0],
              [1.0, 1.0],
              [0.0, 1.0],
              [0.0, 2.0],
              [1.0, 2.0],
              [1.0, 1.0],
              [1.0, 0.0]]
    return Alphanumeric(points)


def character_B() -> Alphanumeric:
    points = [[0.0, 0.0],
              [0.5, 0.0],
              [0.5, 1.0],
              [0.5, 2.0],
              [0.0, 2.0],
              [1.0, 2.0],
              [0.5, 1.0],
              [1.0, 1.0],
              [1.0, 0.0],
              [0.5, 1.0]]
    return Alphanumeric(points)


def character_C() -> Alphanumeric:
    points = [[0.0, 0.0],
              [0.0, 2.0],
              [1.0, 2.0],
              [0.0, 2.0],
              [0.0, 0.0],
              [1.0, 0.0]]
    return Alphanumeric(points)


def character_D() -> Alphanumeric:
    points = [[0.0, 0.0],
              [0.5, 0.0],
              [0.5, 2.0],
              [0.0, 2.0],
              [1.0, 2.0],
              [1.0, 0.0],
              [0.5, 0.0],
              [1.0, 0.0]]
    return Alphanumeric(points)


def character_E() -> Alphanumeric:
    points = [[0.0, 0.0],
              [0.0, 2.0],
              [1.0, 2.0],
              [0.0, 2.0],
              [0.0, 1.0],
              [1.0, 1.0],
              [0.0, 1.0],
              [0.0, 0.0],
              [1.0, 0.0]]
    return Alphanumeric(points)


def character_F() -> Alphanumeric:
    points = [[0.0, 0.0],
              [0.0, 2.0],
              [1.0, 2.0],
              [0.0, 2.0],
              [0.0, 1.0],
              [1.0, 1.0],
              [0.0, 1.0],
              [0.0, 0.0],
              [0.0, -.5],  # RIP
              [1.0, -.5],
              [1.0, 0.0]]
    return Alphanumeric(points)


def character_G() -> Alphanumeric:
    points = [[0.0, 0.0],
              [0.0, 2.0],
              [1.0, 2.0],
              [0.0, 2.0],
              [0.0, 0.0],
              [1.0, 0.0],
              [1.0, 1.0],
              [0.5, 1.0],
              [1.0, 1.0],
              [1.0, 0.0]]
    return Alphanumeric(points)


def character_H() -> Alphanumeric:
    points = [[0.0, 0.0],
              [0.0, 2.0],
              [0.0, 1.0],
              [1.0, 1.0],
              [1.0, 2.0],
              [1.0, 0.0]]
    return Alphanumeric(points)


def character_I() -> Alphanumeric:
    points = [[0.5, 0.0],
              [0.5, 2.0],
              [0.0, 2.0],
              [1.0, 2.0],
              [0.5, 2.0],
              [0.5, 0.0],
              [1.0, 0.0]]
    return Alphanumeric(points)


def character_J() -> Alphanumeric:
    points = [[0.0, 0.0],
              [0.0, 1.0],
              [0.0, 0.0],
              [1.0, 0.0],
              [1.0, 2.0],
              [1.0, 0.0]]
    return Alphanumeric(points)


def character_K() -> Alphanumeric:
    points = [[0.0, 0.0],
              [0.0, 2.0],
              [0.0, 1.0],
              [0.5, 1.0],
              [1.0, 2.0],
              [0.5, 1.0],
              [1.0, 0.0]]
    return Alphanumeric(points)


def character_L() -> Alphanumeric:
    points = [[0.0, 0.0],
              [0.0, 2.0],
              [1.0, 0.0]]
    return Alphanumeric(points)


def character_M() -> Alphanumeric:
    points = [[0.0, 0.0],
              [0.0, 2.0],
              [0.5, 1.0],
              [1.0, 2.0],
              [1.0, 0.0]]
    return Alphanumeric(points)


def character_O() -> Alphanumeric:
    points = [[0.0, 0.0],
              [0.0, 2.0],
              [1.0, 2.0],
              [1.0, 0.0],
              [0.0, 0.0],
              [1.0, 0.0]]
    return Alphanumeric(points)


def character_P() -> Alphanumeric:
    points = [[0.0, 2.0],
              [1.0, 2.0],
              [1.0, 1.0],
              [0.0, 1.0],
              [0.0, 0.0],
              [0.0, -.5],  # RIP
              [1.0, -.5],
              [1.0, 0.0]]
    return Alphanumeric(points)


def character_Q() -> Alphanumeric:
    points = [[0.0, 0.0],
              [0.0, 2.0],
              [1.0, 2.0],
              [1.0, 0.0],
              [0.0, 0.0],
              [1.0, 0.0],
              [0.5, 1.0],
              [1.0, 0.0]]
    return Alphanumeric(points)


def character_R() -> Alphanumeric:
    points = [[0.0, 0.0],
              [0.0, 2.0],
              [1.0, 2.0],
              [1.0, 1.0],
              [0.0, 1.0],
              [0.5, 1.0],
              [1.0, 0.0]]
    return Alphanumeric(points)


def character_S() -> Alphanumeric:
    points = [[0.0, 0.0],
              [1.0, 0.0],
              [1.0, 1.0],
              [0.5, 1.0],
              [0.0, 2.0],
              [1.0, 2.0],
              [0.0, 2.0],
              [0.5, 1.0],
              [1.0, 1.0],
              [1.0, 0.0]]
    return Alphanumeric(points)


def character_T() -> Alphanumeric:
    points = [[0.0, 0.0],
              [0.5, 0.0],
              [0.5, 2.0],
              [0.0, 2.0],
              [1.0, 2.0],
              [0.5, 2.0],
              [0.5, 0.0],
              [1.0, 0.0]]
    return Alphanumeric(points)


def character_U() -> Alphanumeric:
    points = [[0.0, 0.0],
              [0.0, 2.0],
              [0.0, 0.0],
              [1.0, 0.0],
              [1.0, 2.0],
              [1.0, 0.0]]
    return Alphanumeric(points)


def character_V() -> Alphanumeric:
    points = [[0.0, 0.0],
              [0.0, 2.0],
              [1.0, 2.0],
              [0.0, 0.0],
              [0.0, -.5],
              [1.0, -.5],
              [1.0, 0.0]]
    return Alphanumeric(points)


def character_W() -> Alphanumeric:
    points = [[0.0, 0.0],
              [0.0, 2.0],
              [0.0, 0.0],
              [0.5, 1.0],
              [1.0, 0.0],
              [1.0, 2.0],
              [1.0, 0.0]]
    return Alphanumeric(points)


def character_X() -> Alphanumeric:
    points = [[0.0, 0.0],
              [0.5, 1.0],
              [0.0, 2.0],
              [0.5, 1.0],
              [1.0, 2.0],
              [0.5, 1.0],
              [1.0, 0.0]]
    return Alphanumeric(points)


def character_Y() -> Alphanumeric:
    points = [[0.0, 0.0],
              [0.5, 0.0],
              [0.5, 1.0],
              [0.0, 2.0],
              [0.5, 1.0],
              [1.0, 2.0],
              [0.5, 1.0],
              [0.5, 0.0],
              [1.0, 0.0]]
    return Alphanumeric(points)


def character_Z() -> Alphanumeric:
    points = [[0.0, 0.0],
              [0.5, 1.0],
              [1.0, 2.0],
              [0.0, 2.0],
              [1.0, 2.0],
              [0.5, 1.0],
              [0.0, 0.0],
              [1.0, 0.0]]
    return Alphanumeric(points)


def character_1() -> Alphanumeric:
    points = [[0.0, 0.0],
              [1.0, 0.0],
              [1.0, 2.0],
              [0.5, 1.0],
              [1.0, 2.0],
              [1.0, 0.0]]
    return Alphanumeric(points)


def character_2() -> Alphanumeric:
    points = [[0.0, 0.0],
              [0.0, 1.0],
              [1.0, 1.0],
              [1.0, 2.0],
              [0.0, 2.0],
              [1.0, 2.0],
              [1.0, 1.0],
              [0.0, 1.0],
              [0.0, 0.0],
              [1.0, 0.0]]
    return Alphanumeric(points)


def character_3() -> Alphanumeric:
    points = [[0.0, 0.0],
              [1.0, 0.0],
              [1.0, 1.0],
              [0.5, 1.0],
              [1.0, 1.0],
              [1.0, 2.0],
              [0.0, 2.0],
              [1.0, 2.0],
              [1.0, 0.0]]
    return Alphanumeric(points)


def character_4() -> Alphanumeric:
    points = [[0.0, 0.0],
              [0.0, -.5],
              [1.0, -.5],
              [1.0, 0.0],
              [1.0, 1.0],
              [0.0, 1.0],
              [0.0, 2.0],
              [0.0, 1.0],
              [1.0, 1.0],
              [1.0, 2.0],
              [1.0, 0.0]]
    return Alphanumeric(points)


def character_5() -> Alphanumeric:
    points = [[0.0, 0.0],
              [1.0, 0.0],
              [1.0, 1.0],
              [0.0, 1.0],
              [0.0, 2.0],
              [0.0, 1.0],
              [1.0, 1.0],
              [1.0, 0.0]]
    return Alphanumeric(points)


def character_6() -> Alphanumeric:
    points = [[0.0, 0.0],
              [0.0, 2.0],
              [1.0, 2.0],
              [0.0, 2.0],
              [0.0, 1.0],
              [1.0, 1.0],
              [1.0, 0.0],
              [0.0, 0.0],
              [1.0, 0.0]]
    return Alphanumeric(points)


def character_7() -> Alphanumeric:
    points = [[0.0, 0.0],
              [0.5, 1.0],
              [1.0, 2.0],
              [0.0, 2.0],
              [1.0, 2.0],
              [0.5, 1.0],
              [0.0, 0.0],
              [0.0, -.5],
              [1.0, -.5],
              [1.0, 0.0]]
    return Alphanumeric(points)


def character_8() -> Alphanumeric:
    points = [[0.0, 0.0],
              [0.0, 2.0],
              [1.0, 2.0],
              [1.0, 1.0],
              [0.0, 1.0],
              [1.0, 1.0],
              [1.0, 0.0],
              [0.0, 0.0],
              [1.0, 0.0]]
    return Alphanumeric(points)


def character_9() -> Alphanumeric:
    points = [[0.0, 0.0],
              [0.0, -.5],
              [1.0, -.5],
              [1.0, 0.0],
              [1.0, 2.0],
              [0.0, 2.0],
              [0.0, 1.0],
              [1.0, 1.0],
              [1.0, 0.0]]
    return Alphanumeric(points)


def character_0() -> Alphanumeric:
    points = character_O()
    return Alphanumeric(points)


def character_Space() -> Alphanumeric:
    points = [(0, 0), (1, 0)]
    return Alphanumeric(points)
