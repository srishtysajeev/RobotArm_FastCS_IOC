#general imports
from __future__ import annotations
from pathlib import Path 
from dataclasses import dataclass
import asyncio

#fastcs imports 
from fastcs.controller import Controller, BaseController
from fastcs.launch import FastCS
#The below represent the different types of attributes representing access modes of the API 
from fastcs.attributes import AttrR, AttrRW, AttrHandlerR
#The below represent fastcs datatypes 
from fastcs.datatypes import Float, Int, String
from fastcs.transport.epics.ca.options import EpicsCAOptions, EpicsGUIOptions
from fastcs.transport.epics.options import EpicsIOCOptions
#from fastcs.connections import IPConnection, IPConnectionSettings

#robot imports
import os
import sys
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from uarm.wrapper import SwiftAPI
from uarm.tools.list_ports import get_ports


# def robot_connection() -> SwiftAPI:
#     ports = get_ports(filters={'hwid': 'USB VID:PID=2341:0042'}) 
#     print("Ports: ",ports)
#     if not ports:
#         raise ConnectionError("The device is not connected")
#     swift = SwiftAPI(port=ports[0]['device'])
#     return swift

# def get_pos() -> list[float]:
#      position_list = robot_connection().get_position(timeout=10)
#      return position_list
# position = get_pos()
# x_pos = position[0]
# print(x_pos)

@dataclass
class PositionUpdater(AttrHandlerR):
    update_period: float | None = 0.2
    _controller: RobotController | None = None

    async def initialise(self, controller: BaseController):
        assert isinstance(controller, RobotController)
        self._controller = controller

    @property
    def controller(self) -> RobotController:
        if self._controller is None:
            raise RuntimeError("Handler not initialised")

        return self._controller

    async def update(self, attr: AttrR):
        
        pos = self.controller.connection.get_position(timeout=5)

        #get_pos()[0] # update this so that get_pos is only called once and then you get the values from it 
        if isinstance(pos, list):
            x_pos = pos[0]
            await attr.set(value=x_pos) 

        else:
            print(f"Update Error: Failed to get position from robot, recieved {pos}")
            
        #print("X position",x_pos)
        #attr.set(self.controller.connection.get_position(timeout=10)[0])
        #self.controller.connection.get_position(timeout=10)
        #response = await self.controller.connection.send_query("ID?\r\n")
        #value = response.strip("\r\n")

class RobotController(Controller):
    device_id = AttrR(String()) # the variable name is important here! make sure you understand why 
 # try and figure out where these things are coming from   you had the variable name as x_position and it didn't work 
 # it does work acc! you need to get rid of underscore and add capitals  
    x_pos = AttrR(Float(), handler=PositionUpdater())

    def __init__(self):
        super().__init__()
        self.description = "A robot controller"
        #
        self.connection = SwiftAPI()
        #self.connection = robot_connection() # this should make a connection as soon as the class is initialized 
        

    async def connect(self):

        ports = get_ports(filters={'hwid': 'USB VID:PID=2341:0042'}) #maybe get rid of this so that  tuser specifies port
        print("Ports: ",ports)
        if not ports:
            raise ConnectionError("The device is not connected")

        self.connection.connect(port=ports[0]['device'])
        await asyncio.sleep(1)


# robot = RobotController()
# robot.connect()
# positions = robot.connection.get_position()
# print(positions)

gui_options = EpicsGUIOptions(
    output_path=Path(".") / "robot.bob", title="My Robot Controller"
)
epics_options = EpicsCAOptions(
    gui=gui_options,
    ca_ioc=EpicsIOCOptions(pv_prefix="ROBOT"),
)
#connection_settings = IPConnectionSettings("localhost", 25565)
fastcs = FastCS(RobotController(), [epics_options])

fastcs.create_gui()

fastcs.run()

