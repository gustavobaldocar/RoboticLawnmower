"""
Project: 
Automated Robotic Lawnmower Simulator

File: ./python/lawnmower_sim.py

Objectives: 
    Class definiton for Automated Robotic Lawnmower Simulator
    Handles the movement rules
    Handles grid boundaries
    Handles crash detection
    Log simulation steps

Author: gustavobaldocarvalho @ yahoo.com

Version: 31.01.2026 - Creation
"""

# Import Definitions
from typing import List, Tuple, Dict, Any, Set

class LawnmowerSim:
    """
    Automated Robotic Lawnmower Simulator Class Definition
    
    Handles the movement rules
    Handles grid boundaries
    Handles crash detection
    Log simulation steps
    The simulator uses a "Coordinate-First, Validate-Second" approach 
    This ensure the crash location is recorded in the audit messages under pos_history
    while visited_cells only contain valid cells (not crashed)        
    """

    def __init__(
        self, 
        test_name: str, 
        grid_height: int, 
        grid_width: int, 
        rock_locations: List[List[int]], 
        start_pos: List[int]) -> None:
        """
        Method: __init__ (Object Creation)
        Initializes the lawnmower simulator with grid dimensions and obstacles.

        Obs: For sake of simplicity, the input error Handling was descoped from this first version in both 
        Core Engine and App Logic.

        Args:
            test_name (str): test name
            grid_height (int): The total number of rows in the lawn.
            grid_width (int): The total number of columns in the lawn.
            rock_locations (List[List[int]]): Y,X coordinates of rocks within the grid.
            start_pos (List[int]): The starting coordinate [Y, X] for the mower.
        """
        # Initialise Test NameError
        self.test_name: str = test_name
        
        # Initialise Messages
        self.messages: List[str] = []
        self.log(f"--- {self.test_name}: Simulator Config start")
        
        # Initialise Grid
        self.grid_height: int = grid_height
        self.grid_width: int = grid_width
        self.log(f"--- {self.test_name}: Initialise Grid {self.grid_height} x {self.grid_width}")
        
        # Initialize Rock Position
        self.rock_locations: List[List[int]] = rock_locations
        # Filter Out Rock Locations outside Grid dimensions and Warn user
        self.valid_rocks: Dict[Tuple[int, int], bool] = {}
        for r in self.rock_locations:
                row, col = r[0], r[1]
                if 0 <= row < self.grid_height and 0 <= col < self.grid_width:
                    self.valid_rocks[r[0],r[1]] = True
                else:
                    self.log(f"--- {self.test_name}: warning: Rock at {r} is outside the {self.grid_height} x {self.grid_width} lawn. Ignoring.")
        self.log(f"--- {self.test_name}: {len(self.valid_rocks)} valid Rock positions defined inside grid. {len(self.rock_locations)-len(self.valid_rocks)} Rocks outside grid disregarded")
        
        # Initialize Grass Cut status
        self.total_grass_squares: int = (self.grid_width * self.grid_height) - len(self.valid_rocks)
        self.log(f"--- {self.test_name}: Initialize Total Grass squares {self.total_grass_squares}")
        self.uncut_remaining: int = self.total_grass_squares-1 # start pos is always cut
        self.log(f"--- {self.test_name}: Initialize Remaining Uncut {self.uncut_remaining}")
        self.all_grass_cut: bool = False
        self.log(f"--- {self.test_name}: Initialize All Grass Cut status {self.all_grass_cut}")
        
        # Initialise start position
        self.start_pos: Tuple[int, int]  
        if 0 <= start_pos[0] < self.grid_height and 0 <= start_pos[1] < self.grid_width:
            self.start_pos = (start_pos[0], start_pos[1])
        else:
            self.start_pos = (0,0) # reset to top left corner
            self.log(f"--- {self.test_name}: WARNING: start pos at {start_pos} is outside the {self.grid_height} x {self.grid_width} lawn. Resetting to top left [0,0]")
        self.last_pos: List[int] = [self.start_pos[0], self.start_pos[1]]
        self.log(f"--- {self.test_name}: Initialise start position at {start_pos}")    
                
        # Initialise pos_history 
        self.visited_cells: Dict[Tuple[int, int], bool] = {(start_pos[0], start_pos[1]): True} # record cells visited in order of discover. Multiple visits count only once       
        self.number_visited_cells: int = 1 # start pos is a cell
        self.log(f"--- {self.test_name}: Initialise Number of Cells Visited {self.number_visited_cells} (start position counts 1 already)")
        self.pos_history: List[Tuple[int, int]] = [self.start_pos] # record of all moves
        self.log(f"--- {self.test_name}: Initialise Number of Moves 0")
        
        # Initialise Crash Status
        self.did_mower_crash: bool = False
        self.crash_reason: str = "None"
        self.log(f"--- {self.test_name}: Initialise Crash Status {self.did_mower_crash} for Reason {self.crash_reason}") 

    def log(self, message: str) -> None:
        """
        Method: log
        Log messages on display and store for result retrieval

        Args:
            message: (str) - Message to be logged
        """    
        self.messages.append(message)
        print(message)

    def move(self, move: str) -> bool:
        """
        Method: move
        execute sigle moves within defined grid

        Obs: For sake of simplicity, the input error Handling was descoped from this first version in both 
        Core Engine and App Logic.

        Args:
            move (str) - move to be executed (up,down,left,right)
        """
        # Execute Move
        self.log(f"--- {self.test_name}: Current Position {self.last_pos}")
        self.log(f"--- {self.test_name}: execute move {move}")
        if   move == "up":    self.last_pos[0] -= 1 # decrease row number
        elif move == "down":  self.last_pos[0] += 1 # increase row number
        elif move == "left":  self.last_pos[1] -= 1 # decrease column number
        elif move == "right": self.last_pos[1] += 1 # increase column number
        self.log(f"--- {self.test_name}: Last Position {self.last_pos}")
        self.pos_history.append((self.last_pos[0], self.last_pos[1])) # record move in pos_history. Crashes will also be recorded as last entry

        # Check if crashed
        # crashing coordinate is recorded in pos_history and visited_cells because the update happens at the start of the move method
        self.log(f"--- {self.test_name}: check if crashed")
        # Check Rock crash
        if tuple(self.last_pos) in self.valid_rocks:
            # If hitting a rock, Cause a crash
            self.log(f"--- {self.test_name}: rock crash!")
            self.did_mower_crash = True
            self.crash_reason = "Crashed into Rock"
            self.log(f"--- {self.test_name}: Termination: {self.crash_reason}")
        # Check Fence crash
        elif not (0 <= self.last_pos[0] < self.grid_height and 
                0 <= self.last_pos[1] < self.grid_width):
            # If Grid limits invaded, Cause a crash
            self.log(f"--- {self.test_name}: fence crash!")
            self.did_mower_crash = True 
            self.crash_reason = "Crashed into Fence"
            self.log(f"--- {self.test_name}: Termination: {self.crash_reason}")
        else:
            self.log(f"--- {self.test_name}: no crash")
            self.visited_cells[(self.last_pos[0], self.last_pos[1])] = True# record visited cells. repeated visits are ignored
            self.number_visited_cells = len(self.visited_cells)
            self.log(f"--- {self.test_name}: number_visited_cells: {self.number_visited_cells}")
            self.uncut_remaining = self.total_grass_squares - self.number_visited_cells
            self.log(f"--- {self.test_name}: remaining uncut: {self.uncut_remaining}")
            self.all_grass_cut = self.uncut_remaining == 0
            if self.all_grass_cut:
                self.log(f"--- {self.test_name}: All Gras Cut")
            else:
                self.log(f"--- {self.test_name}: Still Gras to Cut")
            
        if self.did_mower_crash:
            self.log(f"--- {self.test_name}: Move Failed due crash")
            return False
            
        self.log(f"--- {self.test_name}: Move OK")
        return True    

    def execute_path(self, path: List[str]) -> Dict[str, Any]:
        """
        Method: execute_path
        execute path as sequence of moves

        Obs: For sake of simplicity, the input error Handling was descoped from this first version in both 
        Core Engine and App Logic.

        Args:
            path: List[str] - sequence of moves from start position (up,down,left,right). Upper Capital will be converted to lower
            
        Output:
        sim_status = {
            "test_name": self.test_name,
            "grid_width": self.grid_width,
            "grid_height": self.grid_height,
            "rock_locations": self.rock_locations,
            "valid_rocks": list(self.valid_rocks.keys()),  
            "start_pos": self.start_pos,
            "total_grass_squares": self.total_grass_squares,
            "all_grass_cut": self.all_grass_cut,
            "uncut_grass_remaining": self.uncut_remaining,
            "did_mower_crash": self.did_mower_crash,
            "crash_reason": self.crash_reason,
            "pos_history": self.pos_history,
            "visited_cells": list(self.visited_cells.keys()), 
            "last_pos": self.last_pos,
            "messages": self.messages
        }
        """    
        # Execute Step by step move on required path sequence
        for step, move in enumerate(path):
            # Move and Update Position 
            self.log(f"\n--- {self.test_name}: Move index {step}") 
            if not self.move(move.lower()):
                break

        # Output results
        if not self.did_mower_crash:
            self.log(f"\n--- {self.test_name}: Simulator Success. All Moves done")
        else:
            self.log(f"\n--- {self.test_name}: Simulator Fail due Crash. Move abort")
                   
        # Output Sim Status Structure
        self.log(f"--- {self.test_name}: Output Sim Status Structure")
        sim_status: Dict[str, Any] = {
            "test_name": self.test_name,
            "grid_width": self.grid_width,
            "grid_height": self.grid_height,
            "rock_locations": self.rock_locations,
            "valid_rocks": list(self.valid_rocks.keys()),  
            "start_pos": self.start_pos,
            "total_grass_squares": self.total_grass_squares,
            "all_grass_cut": self.all_grass_cut,
            "uncut_grass_remaining": self.uncut_remaining,
            "did_mower_crash": self.did_mower_crash,
            "crash_reason": self.crash_reason,
            "pos_history": self.pos_history,
            "visited_cells": list(self.visited_cells.keys()), 
            "last_pos": self.last_pos,
            "messages": self.messages
        }
        
        return sim_status