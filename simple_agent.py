import time


class ActionList():
    def __init__(self, *actions):
        self.actions = actions
    def __call__(self):
        for action in self.actions:
            yield action

class ElementaryAction():
    def __call__(self):
        pass

class Hotbar(ElementaryAction):
    def __init__(self, num, num1):
        self.num = num
        self.num1 = num1

    def __call__(self, agent_host):
        agent_host.sendCommand("hotbar.{0} {1}".format(self.num, self.num1))


class Pitch:
    def __init__(self, ang):
        self.ang = ang

    def __call__(self, agent_host):
        return agent_host.sendCommand("pitch {0}".format(self.ang))

class Jump:
    def __init__(self, arg):
        self.arg = arg
    def __call__(self, agent_host):
        return agent_host.sendCommand("jump {0}".format(self.arg))


class Use:
    def __call__(self, agent_host):
        return agent_host.sendCommand("use 1") or agent_host.sendCommand("use 0")


class State:
    def __call__(self, observation):
        """
        return an action to do
        """
        raise NotImplementedError("not implemented")
    def next_state(self):
        """
        return new state
        """
        return self


class PitchState:
    def __init__(self, next_state):
        self._next_state = self
        self.future_state = next_state

    def __call__(self, observation):
        if observation['Pitch'] < 90:
            return Pitch(0.1)
        self._next_state = self.future_state
        return Pitch(0)

    def next_state(self):
        return self._next_state


class HotBarState:
    def __init__(self, next_state):
        self.count = 0
        self.future_state = next_state

    def __call__(self, obs):
        if self.count == 0:
            self.count += 1
            return Hotbar(5, 1)
        if self.count == 1:
            self.count += 1
            return Hotbar(5, 0)
        self.count += 1
        return None

    def next_state(self):
        if self.count <= 1:
            return self
        return self.future_state


class JumpState:
    def __init__(self, next_state):
        self.in_jump = False
        self.time = time.time()
        self.height = -1
        self._next_state = self
        self.future_state = next_state
        
    def __call__(self, obs):
        print(obs['XPos'], obs['YPos'], obs['ZPos'])
        if self.in_jump:
            if time.time() - self.time < 0.5:
                return Jump(1)
            else:
                self._next_state = self.future_state 
                self.time = time.time()
                return Jump(0)
        else:
            self.time = time.time()
            self.in_jump = True
            return Jump(1)

    def next_state(self):
        return self._next_state


class UseState(State):
    def __init__(self, next_state, limit=50):
        self.future_state = next_state
        self._next_state = self
        self.count = limit 

    def __call__(self, observation):
        self._next_state = self.future_state
        self.count -= 1
        if self.count <= 0:
            self._next_state = None
        return Use()

    def next_state(self):
        return self._next_state
    


class ClimbingAgent(State):
    def __init__(self):
        self.slot_wool = 0
        jump = JumpState(None)
        use = UseState(jump) 
        jump.future_state = use
        pitch = PitchState(jump)
        self.state = HotBarState(pitch) 

    def __call__(self, observation):
        if self.state is None:
            return None
        action = self.state(observation)
        self.state = self.state.next_state()
        return action


