import unittest
import engine
import vector2
import entity
import metagrid
import random



class TestGhost(entity.Entity, entity.Updater): 

    def __init__(self, **kwargs):
        entity.Entity.__init__(self, **kwargs)
        self.updated = False

    def update(self):
        self.updated = True


class TestPosHaver(entity.Entity, entity.Updater):

    def __init__(self, **kwargs):
        kwargs['pos'] = kwargs.get('pos') or vector2.vector2(0,0)
        entity.Entity.__init__(self, **kwargs)
        self.updated = False

    def update(self):
        self.updated = True

class EngineTests(unittest.TestCase):

    def setUp(self):
        self.engine = engine.engine
        self.engine.build_world()
        return
    def tearDown(self):
        return


    def test_add_remove_entities(self):
        test_guy = TestGhost()
        #test guy has no position so it is a ghost 
        self.assertEqual(test_guy.id in self.engine.ghosts, True)
        self.engine.update()
        self.assertEqual(test_guy.updated, True)
        self.assertEqual(self.engine.get_entity(test_guy.id), test_guy)

        self.engine.remove_entity(test_guy)
        self.assertEqual(test_guy.id not in self.engine.ghosts, True)
        test_guy.updated = False
        self.engine.update()
        self.assertEqual(test_guy.updated, False)

        test_guy_2 = TestPosHaver()
        self.assertEqual(self.engine.get_entity(test_guy_2.id), test_guy_2)
        self.engine.update()
        #test guy two should not be updated
        self.assertEqual(test_guy_2.updated, True)
        #and the first guy should STILL not be updated
        self.assertEqual(test_guy.updated, False)


    def test_move_entity(self):

        test_guy = TestPosHaver(pos=vector2.vector2(3,3))
        self.assertEqual(self.engine.get_entities(3,3)[0], test_guy)


        num_cells = metagrid.GRID_SIZE*metagrid.METAGRID_SIZE
        new_pos = None
        for x in range(num_cells):
            while not new_pos or new_pos == test_guy.pos:
                new_pos =   vector2.vector2(random.randint(0,num_cells-1),
                                              random.randint(0,num_cells-1))

            old_pos = test_guy.pos

            test_guy.move(new_pos)
            self.engine.update()

            self.assertEqual(self.engine.get_entities(new_pos.x,new_pos.y)[0], test_guy)
            self.assertEqual(self.engine.get_entities(old_pos.x,old_pos.y),{}) 

        test_guy.die()
        self.engine.update()
        self.assertEqual(self.engine.get_entities(new_pos.x,new_pos.y),{}) 

    def test_entity_die(self):
        test_guy = TestPosHaver()
        self.assertEqual(self.engine.get_entity(test_guy.id), test_guy)
        #now have this guy die and make sure he's not in there
        test_guy.die()
        self.assertEqual(self.engine.get_entity(test_guy.id), None)
        self.engine.update()
        self.assertEqual(test_guy.updated, False)

    def test_find_entities(self):
        test_guy = TestPosHaver(pos=vector2.vector2(0,0))
        test_guy_2 = TestPosHaver(pos=vector2.vector2(3,3))
        test_guy_3 = TestPosHaver(pos=vector2.vector2(7,7))

        def selector(ent):
            return True

        nearest = self.engine.metagrid.find_nearest(3,3,0,max_dist=5,selector=selector)

        self.assertEqual(nearest, test_guy_2)

        







