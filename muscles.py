class Muscle:
    def __init__(self, id):
        self.id = id
        self.activated_from_id = 0

        self.default_refractory_period = 300
        self.default_conduction_time = 250
        self.default_contraction_time = 150

        self.refractory_period = self.default_refractory_period
        self.conduction_time = self.default_conduction_time
        self.contraction_time = self.default_contraction_time

        self.connected_node_ids = []

        # elapsed time since activation
        self.timer = 0
        self.active = False

        self.has_fired = 0

    def set_individual_defaults(self, rp=None, ct=None, contraction=None):
        if rp is not None:
            self.default_refractory_period = rp
            self.refractory_period = rp
        if ct is not None:
            self.default_conduction_time = ct
            self.conduction_time = ct
        if contraction is not None:
            self.default_contraction_time = contraction
            self.contraction_time = contraction

    @classmethod
    def set_defaults(cls, muscles, rp=None, ct=None, contraction=None):
        for m in muscles:
            m.set_individual_defaults(rp, ct, contraction)

    def set_multiplier(self, rp=None, ct=None, contraction=None):
        if rp is not None:
            self.refractory_period = rp * self.default_refractory_period
        if ct is not None:
            self.conduction_time = ct * self.default_conduction_time
        if contraction is not None:
            self.contraction_time = contraction * self.default_contraction_time

    @classmethod
    def set_multiplier_for_ids(cls, muscles, ids, rp=None, ct=None, contraction=None):
        for mid in ids:
            if 0 <= mid < len(muscles):
                muscles[mid].set_multiplier(rp, ct, contraction)

    def is_conducting(self):
        return self.active and self.timer < self.conduction_time

    def is_contracting(self):
        return self.active and self.timer < self.contraction_time

    def is_refractory(self):
        return (
            self.active and
            self.contraction_time <= self.timer <
            self.contraction_time + self.refractory_period
        )

    def is_ready(self):
        return not self.active

    def print_stats(self):
        print(
            f"muscleid: {self.id}\n"
            f"timer: {self.timer}\n"
            f"ct: {self.conduction_time}\n"
            f"contract: {self.contraction_time}\n"
            f"rp: {self.refractory_period}\n"
            f"conducting: {self.is_conducting()}\n"
            f"contracting: {self.is_contracting()}\n"
            f"refractory: {self.is_refractory()}\n"
            f"ready: {self.is_ready()}"
        )

    def update(self, ext_nodes, ext_muscles):
        fired = False

        if self.active:
            self.timer += 1

            # invisible electrical propagation
            if self.timer == self.conduction_time:
                for nid in self.connected_node_ids:
                    if nid != self.activated_from_id:
                        for ext_node in ext_nodes:
                            if ext_node.id == nid:
                                if ext_node.fire(ext_muscles):
                                    fired = True

            # reset after contraction + refractory
            total_duration = self.contraction_time + self.refractory_period
            if self.timer >= total_duration:
                self.timer = 0
                self.active = False

        return fired

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

    def connect_node(self, id):
        if len(self.connected_node_ids) > 1:
            print("Could not assign node to muscle; already has 2 Nodes.")
            return
        self.connected_node_ids.append(id)
