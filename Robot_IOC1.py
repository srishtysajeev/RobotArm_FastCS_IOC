from pathlib import Path 

#fastcs imports 
from fastcs.controller import Controller
from fastcs.launch import FastCS
#The below represent the different types of attributes representing access modes of the API 
from fastcs.attributes import AttrR, AttrRW
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


def robot_connection() -> SwiftAPI:
    ports = get_ports(filters={'hwid': 'USB VID:PID=2341:0042'}) 
    print("Ports: ",ports)
    if not ports:
        raise ConnectionError("The device is not connected")
    swift = SwiftAPI(port=ports[0]['device'])
    return swift

def get_pos() -> list[float]:
     position_list = robot_connection().get_position(timeout=10)
     return position_list
#position = get_pos()
# x_pos = position[0]
# print(x_pos)


class RobotController(Controller):
    device_id = AttrR(String()) # the variable name is important here! make sure you understand why 
 # try and figure out where these things are coming from   you had the variable name as x_position and it didn't work 
 # it does work acc! you need to get rid of underscore and add capitals  
    x_pos = AttrRW(Int())

    robot_connection()
    
    def __init__(self):
        super().__init__()
        self.description = "A robot controller"
        self.connection = robot_connection() # this should make a connection as soon as the class is initialized 
        

    # async def connect(self):
    #     robot_connection() # for some reason having await before this does not work 


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

