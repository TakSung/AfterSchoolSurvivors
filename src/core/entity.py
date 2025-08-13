import itertools

class Entity:
    """A unique identifier for an object in the game world."""
    _id_counter = itertools.count()

    def __init__(self):
        self.id: int = next(self._id_counter)
