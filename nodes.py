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
        micro_triggers = [] # List of muscle ids that triggered this node to fire, used to detect micro reentry

        for m in external_muscles:
            for cid in self.connected_muscle_ids:
                if m.id == cid:
                    # activate muscle in this step, and detect if it has now fired twice
                    if m.activate(self.id):
                        activated = True
                        if m.has_fired > 1:
                            micro_triggers.append(m.id) # Add the muscle id to the micro triggers list if this muscle has fired more than once

        return activated, micro_triggers # Return whether this node was activated, and any micro triggers that were detected

    def connect_muscle(self, id):
        self.connected_muscle_ids.append(id)


