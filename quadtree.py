class QuadTreeNode:

    def __init__(self, pos, level):
        self.children = {}
        self.parent = None
        self.level = level
        self.pos =  pos
        self.size = 2**level
        self.entities = {}

        if level > 0:
            self._add_children() 
        else:
            self.cell =  GridCell()
        
    def add_children(self):
        for dir in DIAGONALS:
            self.children[dir] = QuadTreeNode(self.pos + dir*self.size,
                                              self.level -1)











from engine import GridCell
