class Node:
    def __init__(self, id):
        # array of ids of connected muscles, muscles will be in external array
        self.id = id 
        self.connected_muscle_ids = []


    # check all the external muscles, if there is an in the external muscles
    # that is also in the list of connected muslces, 
    # fire that muscle (the muscle firing checks internaly if its in
    # refractory or not)
    def fire(self, external_muscles):
        for m in external_muscles: # loop through the muscles
            for cid in self.connected_muscle_ids: # loop through the connected muscle
                if (m.id == cid): # if muscle id matches a connected muscle id 
                    m.activate(self.id) # avtivate the muscle with the firing node 
        return


    def connect_muscle(self, id):
        self.connected_muscle_ids.append(id)


