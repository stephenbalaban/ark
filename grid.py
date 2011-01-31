

class GameGrid:

    def __init__(self, num_layers, size):

        self.cells =  [[ GridCell(num_layers)
                         for  y in range(size)]
                            for x in range(size)]
        self.size = size

    def get_entities(self, x, y):

        if x < 0 or x >= self.size or \
           y < 0 or y >= self.size:
                return {}
        else:
                return self.cells[x][y].get_entities()


    def add_entity(self, ent):
        if ent.pos.x < 0 or ent.pos.x >= self.size or \
           ent.pos.y < 0 or ent.pos.y >= self.size:
            return False
        else:
            return self.cells[ent.pos.x][ent.pos.y].add_entity(ent)

    def remove_entity(self, ent):
        if ent.pos.x < 0 or ent.pos.x >= self.size or \
           ent.pos.y < 0 or ent.pos.y >= self.size:
            return False
        else:
            return self.cells[ent.pos.x][ent.pos.y].remove_entity(ent)

    def get_free_position(self, layer, tries=10):
        placed = False
        
        while not placed and tries:
            tries = tries - 1
            x = random.randint(0, GRID_SIZE-1)
            y = random.randint(0, GRID_SIZE-1)
            if not layer in self.get_entities(x,y):
                return vector2(x,y)
        return None

    def get_neighbors(self, pos):
        neighbors = {}
        if pos.x >= 0:
            neighbors[LEFT] = self.get_entities(pos.x-1, pos.y)
        if pos.x < GRID_SIZE:
            neighbors[RIGHT] = self.get_entities(pos.x+1, pos.y)
        if pos.y >= 0:
            neighbors[UP] = self.get_entities(pos.x, pos.y-1)
        if pos.y < GRID_SIZE:
            neighbors[DOWN] =self.get_entities(pos.x, pos.y+1)  

        return neighbors

