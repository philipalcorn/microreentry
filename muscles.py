class Muscle:   
    def __init__(self, id):
        self.id = id
        self.activated_from_id =0
        self.refractory_period = 9 
        self.conduction_time = 10
        self.connected_node_ids =[] 
        # When we activate the muscle, the timer increments until it reaches 
        # the conduction time

        # if the timer == 0, it can be activated
        # if the timer > 0, it's in refractory
        self.conduction_timer = 0
        self.refractory_timer = 0
        self.activated = False
        return

    def print_stats(self):
        print(f"muscleid: {self.id}\n c_timer: {self.conduction_timer} \n r_timer: {self.refractory_timer}")


    def update(self, ext_nodes, ext_muscles):
        if (self.activated):
            self.conduction_timer = self.conduction_timer + 1
            self.refractory_timer = self.refractory_timer + 1

        # Once the signal has travel across the muscle
        if (self.conduction_timer > self.conduction_time):
            # Use > becuase it immediately increments the first 
            # frame it gets activated
            for id in self.connected_node_ids:
                if (id != self.activated_from_id):
                    for ext_node in ext_nodes:
                        if (ext_node.id == id):
                            ext_node.fire(ext_muscles)

        # Considered "activated" until it's fullly done with refractory,
        # Even if conduction has already reached the next nodes.
        if (self.refractory_timer > self.refractory_period
            and self.conduction_timer > self.conduction_time):
            self.refractory_timer=0
            self.conduction_timer=0
            self.activated = False
        return

    def activate(self, node_id):
        #Checks in the node is actually connected
        if(self.connected_node_ids[0] != node_id and  
           self.connected_node_ids[1] != node_id):
            print(f"Muscle activation attempt from a node not conected, activation ignored. Node id: {self.activated_from_id}, Muscle id: {self.id}")
            print(f"Nodes connected to this muscle: {self.connected_node_ids}")
            return 
        
        # if out of rp, print node info and activate
        if (self.refractory_timer == 0 or self.refractory_timer > self.refractory_period ):
            print(f"Activating node id: {node_id}")
            #print(f"Node 1: {self.connected_node_ids[0]}")
            #print(f"Node 2: {self.connected_node_ids[1]}")
            print(f"Muscle {self.id} Activated!!!\n\n\n")
            self.activated = True
            self.activated_from_id = node_id

    def connect_node(self, id):
        if (len(self.connected_node_ids) > 1):
            print("Could not assign node to muscle; already has 2 Nodes.")
            return
        self.connected_node_ids.append(id)
        return
