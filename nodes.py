class Node:
    def __init__(self, id):
        # array of ids of connected muscles, muscles will be in external array
        self.id = id 
        self.connected_muscle_ids = []
        self.has_fired=0


    # check all the external muscles, if there is an in the external muscles
    # that is also in the list of connected muslces, 
    # fire that muscle (the muscle firing checks internaly if its in
    # refractory or not)
                        
    def fire(self, external_muscles):
        self.has_fired += 1
        activated = False

        for m in external_muscles:
            for cid in self.connected_muscle_ids:
                if m.id == cid:
                    if m.activate(self.id):
                        activated = True

        return activated

    def connect_muscle(self, id):
        self.connected_muscle_ids.append(id)


