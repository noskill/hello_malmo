import json
from builtins import range
import MalmoPython
import os
import sys
import time

if sys.version_info[0] == 2:
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)  # flush print output immediately
else:
    import functools
    print = functools.partial(print, flush=True)

# More interesting generator string: "3;7,44*49,73,35:1,159:4,95:13,35:13,159:11,95:10,159:14,159:6,35:6,95:6;12;"

missionXML='''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
            <Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            
              <About>
                <Summary>Hello world!</Summary>
              </About>
              <ServerSection>
                <ServerHandlers>
                  <FlatWorldGenerator />
                  <DrawingDecorator>
                    <DrawSphere x="-27" y="35" z="0" radius="30" type="wool"/>
                  </DrawingDecorator>

                  <ServerQuitFromTimeUp timeLimitMs="30000"/>
                  <ServerQuitWhenAnyAgentFinishes/>
                </ServerHandlers>
              </ServerSection>
              
                <AgentSection mode="Survival">
                <Name>MalmoTutorialBot</Name>
                <AgentStart>
                    <Placement x="-55" y="5.0" z="0.5" yaw="0"/>
            <Inventory>
                    <InventoryItem slot="0" type="torch"/>
                    <InventoryItem slot="1" type="diamond_pickaxe"/>
                    <InventoryItem slot="3" type="wool" quantity="64"/>
                    <InventoryItem slot="4" type="wool" quantity="64"/>
                    <InventoryItem slot="5" type="wool" quantity="64"/>
                </Inventory>

                </AgentStart>

                <AgentHandlers>
                  <ObservationFromFullStats/>
                  <InventoryCommands/>
                  <ObservationFromHotBar/> 
                  <ContinuousMovementCommands turnSpeedDegs="180"/>
                </AgentHandlers>
              </AgentSection>
            </Mission>'''

# Create default Malmo objects:

agent_host = MalmoPython.AgentHost()
try:
    agent_host.parse( sys.argv )
except RuntimeError as e:
    print('ERROR:',e)
    print(agent_host.getUsage())
    exit(1)
if agent_host.receivedArgument("help"):
    print(agent_host.getUsage())
    exit(0)

my_mission = MalmoPython.MissionSpec(missionXML, True)
my_mission_record = MalmoPython.MissionRecordSpec()

# Attempt to start a mission:
max_retries = 3
for retry in range(max_retries):
    try:
        agent_host.startMission( my_mission, my_mission_record )
        break
    except RuntimeError as e:
        if retry == max_retries - 1:
            print("Error starting mission:",e)
            exit(1)
        else:
            time.sleep(2)

# Loop until mission starts:
print("Waiting for the mission to start ", end=' ')
world_state = agent_host.getWorldState()
while not world_state.has_mission_begun:
    print(".", end="")
    time.sleep(0.1)
    world_state = agent_host.getWorldState()
    for error in world_state.errors:
        print("Error:",error.text)

print()
print("Mission running ", end=' ')

from simple_agent import ClimbingAgent
cl = ClimbingAgent()
# Loop until mission ends:
while world_state.is_mission_running:
    print(".", end="")
    time.sleep(0.1)
    world_state = agent_host.getWorldState()
    for error in world_state.errors:
        print("Error:",error.text)

    msg = world_state.observations[-1].text                 # Yes, so get the text
    observations = json.loads(msg)
    a = cl(observations)
    if a is not None:
        a(agent_host)
    else:
        break
 
print()
print("Mission ended")
# Mission has ended.



