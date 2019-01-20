from typing import List, Tuple, Iterable


class Alphanumeric:
    width: float
    height: float
    waypoints: List[Tuple[float, float]]

    # Simple constructor
    def __init__(self, waypoints: List[Iterable[float]]):
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


def get_letter(l):
    # Will eventually return an appropriate alphanumeric for the given letter
    method_name = 'character_' + str(l).upper()
    # Get the method from 'self'. Default to a lambda.
    method = getattr(Factories, method_name, None)
    if method is None:
        return Factories.character_Space()
    else:
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


class Factories:
    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def character_C() -> Alphanumeric:
        points = [[0.0, 0.0],
                  [0.0, 2.0],
                  [1.0, 2.0],
                  [0.0, 2.0],
                  [0.0, 0.0],
                  [1.0, 0.0]]
        return Alphanumeric(points)

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def character_H() -> Alphanumeric:
        points = [[0.0, 0.0],
                  [0.0, 2.0],
                  [0.0, 1.0],
                  [1.0, 1.0],
                  [1.0, 2.0],
                  [1.0, 0.0]]
        return Alphanumeric(points)

    @staticmethod
    def character_I() -> Alphanumeric:
        points = [[0.5, 0.0],
                  [0.5, 2.0],
                  [0.0, 2.0],
                  [1.0, 2.0],
                  [0.5, 2.0],
                  [0.5, 0.0],
                  [1.0, 0.0]]
        return Alphanumeric(points)

    @staticmethod
    def character_J() -> Alphanumeric:
        points = [[0.0, 0.0],
                  [0.0, 1.0],
                  [0.0, 0.0],
                  [1.0, 0.0],
                  [1.0, 2.0],
                  [1.0, 0.0]]
        return Alphanumeric(points)

    @staticmethod
    def character_K() -> Alphanumeric:
        points = [[0.0, 0.0],
                  [0.0, 2.0],
                  [0.0, 1.0],
                  [0.5, 1.0],
                  [1.0, 2.0],
                  [0.5, 1.0],
                  [1.0, 0.0]]
        return Alphanumeric(points)

    @staticmethod
    def character_L() -> Alphanumeric:
        points = [[0.0, 0.0],
                  [0.0, 2.0],
                  [1.0, 0.0]]
        return Alphanumeric(points)

    @staticmethod
    def character_M() -> Alphanumeric:
        points = [[0.0, 0.0],
                  [0.0, 2.0],
                  [0.5, 1.0],
                  [1.0, 2.0],
                  [1.0, 0.0]]
        return Alphanumeric(points)

    @staticmethod
    def character_O() -> Alphanumeric:
        points = [[0.0, 0.0],
                  [0.0, 2.0],
                  [1.0, 2.0],
                  [1.0, 0.0],
                  [0.0, 0.0],
                  [1.0, 0.0]]
        return Alphanumeric(points)

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def character_R() -> Alphanumeric:
        points = [[0.0, 0.0],
                  [0.0, 2.0],
                  [1.0, 2.0],
                  [1.0, 1.0],
                  [0.0, 1.0],
                  [0.5, 1.0],
                  [1.0, 0.0]]
        return Alphanumeric(points)

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def character_U() -> Alphanumeric:
        points = [[0.0, 0.0],
                  [0.0, 2.0],
                  [0.0, 0.0],
                  [1.0, 0.0],
                  [1.0, 2.0],
                  [1.0, 0.0]]
        return Alphanumeric(points)

    @staticmethod
    def character_V() -> Alphanumeric:
        points = [[0.0, 0.0],
                  [0.0, 2.0],
                  [1.0, 2.0],
                  [0.0, 0.0],
                  [0.0, -.5],
                  [1.0, -.5],
                  [1.0, 0.0]]
        return Alphanumeric(points)

    @staticmethod
    def character_W() -> Alphanumeric:
        points = [[0.0, 0.0],
                  [0.0, 2.0],
                  [0.0, 0.0],
                  [0.5, 1.0],
                  [1.0, 0.0],
                  [1.0, 2.0],
                  [1.0, 0.0]]
        return Alphanumeric(points)

    @staticmethod
    def character_X() -> Alphanumeric:
        points = [[0.0, 0.0],
                  [0.5, 1.0],
                  [0.0, 2.0],
                  [0.5, 1.0],
                  [1.0, 2.0],
                  [0.5, 1.0],
                  [1.0, 0.0]]
        return Alphanumeric(points)

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def character_1() -> Alphanumeric:
        points = [[0.0, 0.0],
                  [1.0, 0.0],
                  [1.0, 2.0],
                  [0.5, 1.0],
                  [1.0, 2.0],
                  [1.0, 0.0]]
        return Alphanumeric(points)

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def character_0() -> Alphanumeric:
        points = character_O()
        return Alphanumeric(points)

    @staticmethod
    def character_Space() -> Alphanumeric:
        points = [(0.0, 0.0),
                  (1.0, 0.0)]
        return Alphanumeric(points)

    @staticmethod
    def character_Separator() -> Alphanumeric:
        points = [(0.0, 0.0),
                  (0.2, 0.0)]
        return Alphanumeric(points)
