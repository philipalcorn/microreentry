class Muscle:
    def __init__(self, id):
        self.id = id
        self.activated_from_id = 0

        self.default_refractory_period = 300
        self.default_conduction_time = 10 

        self.refractory_period = self.default_refractory_period
        self.conduction_time = self.default_conduction_time

        self.connected_node_ids = []

        # elapsed time since activation
        self.timer = 0
        self.active = False

        self.has_fired = 0

    def set_individual_defaults(self, rp=None, ct=None):
        if rp is not None:
            self.default_refractory_period = rp
            self.refractory_period = rp
        if ct is not None:
            self.default_conduction_time = ct
            self.conduction_time = ct

        if self.refractory_period <= self.conduction_time:
            raise ValueError(
                f"Muscle {self.id}: conduction time ({self.conduction_time}) must be "
                f"less than refractory period ({self.refractory_period})."
            )

    @classmethod
    def set_defaults(cls, muscles, rp=None, ct=None):
        for m in muscles:
            m.set_individual_defaults(rp, ct)

    def set_multiplier(self, rp=None, ct=None):
        if rp is not None:
            self.refractory_period = rp * self.default_refractory_period
        if ct is not None:
            self.conduction_time = ct * self.default_conduction_time

        # Enforce a valid physiology rule: refractory period must exceed conduction time.
        # This avoids short RP that terminates the activation before conduction happens.
        if self.refractory_period <= self.conduction_time:
            self.refractory_period = self.conduction_time + 1


    @classmethod
    def set_multiplier_for_ids(cls, muscles, ids, rp=None, ct=None):
        for mid in ids:
            if 0 <= mid < len(muscles):
                muscles[mid].set_multiplier(rp, ct)

    def is_conducting(self):
        return self.active and self.timer < self.conduction_time

    def is_refractory(self):
        return (
            self.active and self.timer < self.refractory_period
        )

    def is_ready(self):
        return not self.active

    def print_stats(self):
        print(
            f"muscleid: {self.id}\n"
            f"timer: {self.timer}\n"
            f"ct: {self.conduction_time}\n"
            f"rp: {self.refractory_period}\n"
            f"conducting: {self.is_conducting()}\n"
            f"refractory: {self.is_refractory()}\n"
            f"ready: {self.is_ready()}"
        )
    #TODO: Fix the logic here as it has leftover garbage from implementing conduciton//contraction
    # Need to fix timing of resetting to inactive.
    def update(self, ext_nodes):
        fired_node_ids = []

        if self.active:
            self.timer += 1

            # invisible electrical propagation at conduction point
            if self.timer - 1 < self.conduction_time <= self.timer:
                for nid in self.connected_node_ids:
                    if nid != self.activated_from_id:
                        fired_node_ids.append(nid)
                        if 0 <= nid < len(ext_nodes):
                            ext_nodes[nid].activated_from_id = self.id

            # reset after conduction + refractory
            #total_duration = self.conduction_time + self.refractory_period
            if self.timer >= self.refractory_period:
                self.timer = 0
                self.active = False

        return fired_node_ids

    def activate(self, node_id):
        if len(self.connected_node_ids) < 2:
            print(f"Muscle {self.id} is not fully connected.")
            return False

        if node_id not in self.connected_node_ids:
            print(
                f"Muscle activation attempt from a node not connected, "
                f"activation ignored. Node id: {node_id}, Muscle id: {self.id}"
            )
            print(f"Nodes connected to this muscle: {self.connected_node_ids}")
            return False

        if not self.active:
            self.active = True
            self.timer = 0
            self.activated_from_id = node_id
            self.has_fired += 1
            return True

        return False

    def reset(self, rp=None, ct=None):
        self.timer = 0
        self.active = False
        self.has_fired = 0
        self.activated_from_id = 0
        if rp is not None:
            self.refractory_period = rp
        if ct is not None:
            self.conduction_time = ct

    def connect_node(self, id):
        if len(self.connected_node_ids) > 1:
            print("Could not assign node to muscle; already has 2 Nodes.")
            return
        self.connected_node_ids.append(id)
