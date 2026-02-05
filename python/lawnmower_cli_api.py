"""
Project: 
Automated Robotic Lawnmower Simulator

File: ./python/lawnmower_cli_api.py

Objectives: 
    CLI and API Entry Point interfaces for execution of Automated Robotic Lawnmower Simulator
    Handles input data. Here Example of a definition file:
        test_name="lawnmower_scenario01_valid"
        height=5
        width=5
        rocks=[[1,1], [2,2], [3,3]]
        start_pos=[0,0]
        path=["Down", "Down", "Down", "Right", "Up", "Left"]
    Creates and execute obj LawnmowerSim
    Handle output in form of Terminal printout and JSON files under ./results folder

Execution:
    CLI 
        Hard Coded Default Scenario: 
            python ./python/lawnmower_cli_api.py --cli
        File Based Test:
            python ./python/lawnmower_cli_api.py --cli ./tests/lawnmower_scenario01_valid.txt
    API
        0. Start Server: python ./python/lawnmower_cli_api.py --api
        1. Navigate to `http://localhost:8000` in a browser.
        2. Click **Load Definition** and select one of the `.txt` files from the `./tests` folder.
        3. Click **Run Simulation** to see the status, path visualization, and crash reports on screen.

    After testing, check terminal messages and ./results folder for output files
    
Author: gustavobaldocarvalho @ yahoo.com

Version: 31.01.2026 - Creation
"""

# Import Definitions
import os
import json
import sys
import ast # Used to safely convert string representations of lists
import uvicorn
from datetime import datetime
from fastapi import FastAPI, UploadFile, File
from typing import List, Dict, Any, Optional
from lawnmower_sim import LawnmowerSim
from fastapi.responses import HTMLResponse
from fastapi.responses import FileResponse

# Prevent "Directory not found" error
os.makedirs("./results", exist_ok=True)

# Initialise FastAPI with UI customizations
app_lawnmower_simulation = FastAPI(
    title="Auto Lawnmower Simulator and Path Verifier MVP",
    description="""
    ## Auto Lawnmower Simulator and Path Verifier MVP
    
    **Quick Start:**
    1. Click the **'Simulator'** section below.
    2. Upload your **.txt** configuration file.
    3. Click **'Run'**.
    """,
    version="1.0.0",
    # This specifically hides the low-level "Schemas" section 
    swagger_ui_parameters={"defaultModelsExpandDepth": -1} 
)

@app_lawnmower_simulation.get("/README.md")
async def serve_readme() -> Any:
    # This points to the file in the parent directory relative to this script
    readme_path = os.path.join(os.path.dirname(__file__), "..", "README.md")
    if os.path.exists(readme_path):
        return FileResponse(readme_path)
    return {"error": "README.md not found at " + readme_path}


# Initialise FastAPI for the Lawnmower Simulator with UI customizations
@app_lawnmower_simulation.get("/", response_class=HTMLResponse)
async def simple_ui() -> Any:
    """
    Reads the UI definition from an external HTML file.
    """
    # get UI definition file
    ui_def = os.path.join(os.path.dirname(__file__), "lawnmower_api.html")
    
    try:
        with open(ui_def, "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Error: lawnmower_api.html not found</h1>", status_code=404)
        
    
def parse_text_file(content: str) -> Dict[str, Any]:
    """
    Function: parse_text_file
    Parses raw text string into simulation arguments.
    
    TODO
        input Error Handling
        params field error handling
        
    Args:
        content: str - string text 
            Expected format in text file:
            test_name - string
            height=3 - grid height (lines)
            width=2 - grid width (columns)
            rocks=[[0,1],[1,1]] - coordinates of the rocks
            start_pos=[0,0] - start position coordinate in the grid
            path=["Down","Down","Right"] - sequence of moves from start position (up,down,left,right). Upper Capital will be converted to lower
            """
    # Split input in lines
    lines = content.splitlines()
    params = {}
    
    # Read and parse the lines in variables and values
    for line in lines:
        if '=' in line:
            key, val = line.split('=')
            params[key.strip()] = ast.literal_eval(val.strip())
            
    # Return parsed information
    return params
    
@app_lawnmower_simulation.post("/simulate", tags=["Simulator"])
async def api_lawnmower_simulation(file: UploadFile = File(..., description="Select the .txt lawn and path definitions file")) -> Dict[str, Any]:
    """
    Funnction: API Endpoint function to execute the Lawnmower simulator
    
    Args:
        file: UploadFile - file with Simulator config and execution parameters

    Output:
    JSON object containing following information
        "test_name": self.test_name,
        "grid_width": self.grid_width,
        "grid_height": self.grid_height,
        "rock_locations": self.rock_locations,
        "valid_rocks": self.valid_rocks,
        "start_pos": self.start_pos,
        "total_grass_squares": self.total_grass_squares,
        "all_grass_cut": self.all_grass_cut,
        "uncut_grass_remaining": self.uncut_remaining,
        "did_mower_crash": self.did_mower_crash,
        "crash_reason": self.crash_reason,
        "pos_history": self.pos_history,
        "visited_cells": self.visited_cells,
        "last_pos": self.last_pos,
        "messages": self.messages  
    """

    # wait for input file and read its content
    content = await file.read()  
    
    # Parse file content
    params = parse_text_file(content.decode("utf-8"))
    
    # Execute and get  results in Dictionary format
    sim_status = execute_and_report(params)
    
    # Return as JSON Object
    # sim_status convertion to JSON object is handled automatically by FastAPI
    return sim_status    
    
def cli_lawnmower_simulation(file_path: str) -> str:
    """
    Funnction: cli_lawnmower_simulation
    Command Line function to ingest a text file and execute the Lawnmower simulator
    if no args, default test scenario is executed
        
    Args:
        file_path - path to file containing Simulator config and execution parameters
            TODO input Error Handling

    Output:
    JSON file and string containing following information
        "test_name": self.test_name,
        "grid_width": self.grid_width,
        "grid_height": self.grid_height,
        "rock_locations": self.rock_locations,
        "valid_rocks": self.valid_rocks,
        "start_pos": self.start_pos,
        "total_grass_squares": self.total_grass_squares,
        "all_grass_cut": self.all_grass_cut,
        "uncut_grass_remaining": self.uncut_remaining,
        "did_mower_crash": self.did_mower_crash,
        "crash_reason": self.crash_reason,
        "pos_history": self.pos_history,
        "visited_cells": self.visited_cells,
        "last_pos": self.last_pos,
        "messages": self.messages          
    """
    params: Dict[str, Any] = {}
    if file_path is "":
        # No File. Use Default scenario 
        params = {
            "test_name": "lawnmower_scenario_def_valid",
            "height": 3,
            "width": 2,
            "rocks": [[0, 1], [1, 1]],
            "start_pos": [0, 0],  
            "path": ["Down", "Down", "Right"]
        }
    else:
        # Fail Safe Read File
        with open(file_path, "r") as f:
            # Parse file
            params = parse_text_file(f.read())  
    # Execute and get results in Dictionary format
    sim_status = execute_and_report(params)
    # Convert Dictionary to JSON
    json_string: str = json.dumps(sim_status, indent=4)        
    # Return JSON Object
    return json_string
    
def execute_and_report(params: Dict[str, Any])-> Dict[str, Any]:
    """
    Funnction: execute_and_report
    Unified core logic: Runs simulation, logs to terminal, and saves local JSON file
         
    TODO
    input Error Handling

    params: Dict[str, Any]:
    Args:
        params: Dict[str, Any]:
            test_name - string
            height=3 - grid height (lines)
            width=2 - grid width (columns)
            rocks=[[0,1],[1,1]] - coordinates of the rocks
            start_pos=[0,0] - start position coordinate in the grid
            path=["Down","Down","Right"] - sequence of moves from start position (up,down,left,right). Upper Capital will be converted to lower
    
    Output:
    JSON file and Dictionary containing following information
        "test_name": self.test_name,
        "grid_width": self.grid_width,
        "grid_height": self.grid_height,
        "rock_locations": self.rock_locations,
        "valid_rocks": self.valid_rocks,
        "start_pos": self.start_pos,
        "total_grass_squares": self.total_grass_squares,
        "all_grass_cut": self.all_grass_cut,
        "uncut_grass_remaining": self.uncut_remaining,
        "did_mower_crash": self.did_mower_crash,
        "crash_reason": self.crash_reason,
        "pos_history": self.pos_history,
        "visited_cells": self.visited_cells,
        "last_pos": self.last_pos,
        "messages": self.messages  
    """

    # Create Simulator Object
    print(f"--- {params['test_name']}: Create Simulator Object ---")
    lm_sim = LawnmowerSim(
        test_name=params['test_name'],
        grid_height=params['height'], 
        grid_width=params['width'], 
        rock_locations=params['rocks'], 
        start_pos=params['start_pos']
    )
    
    # Execute and Get results
    print(f"\n--- {params['test_name']}: Execute and Get results ---")
    sim_status = lm_sim.execute_path(params['path']) 

    # Final Output
    print(f"\n--- {sim_status['test_name']}: List Simulation Results ---")
    
    print(f"--- {sim_status['test_name']}: Pos History ---")
    for step, mh in enumerate(sim_status['pos_history']):
        print(f"--- {sim_status['test_name']}: Pos {step}: {mh}")
        
    print(f"--- {sim_status['test_name']}: Visited Cells (Discovery Order) ---")
    for step, coord in enumerate(sim_status['visited_cells']):
        print(f"--- {sim_status['test_name']}: Cell {step}: {coord}")        
    
    print(f"--- {sim_status['test_name']}: Crash Status: {sim_status['did_mower_crash']}")
    if sim_status['did_mower_crash']:
        print(f"--- {sim_status['test_name']}: Crash Reason: {sim_status['crash_reason']}")
    
    print(f"--- {sim_status['test_name']}: Grass Remaining Uncut: {sim_status['uncut_grass_remaining']}")
    print(f"--- {sim_status['test_name']}: All Grass Cut: {sim_status['all_grass_cut']}")            
    print(f"--- {sim_status['test_name']}: Result: {'CRASH!' if sim_status['did_mower_crash'] else 'NO CRASH'}") 

    # Store output to local file
    # Create a unique filename based on current time
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"./results/{params['test_name']}_{timestamp}.json"
    
    # Save JSON File with results
    with open(filename, "w") as f:
        json.dump(sim_status, f, indent=4)
        
    print(f"\n---  {sim_status['test_name']}: Simulation results saved to: {filename}")
    
    # Output dictionary
    return sim_status
    
if __name__ == "__main__":
    # sys.argv[0] is always the script name (e.g., './python/lawnmower_cli_api.py')
    # sys.argv[1] would be the first argument provided by the user
    # Check if we have at least one argument
    if len(sys.argv) < 2:
        print(f"\n--- Please specify option --api or --cli")
    elif sys.argv[1] == "--api":
        # Call Simulator via API
        print(f"\n--- Starting API Server for Lawnmower Simulator at http://localhost:8000/docs")
        uvicorn.run(
            "lawnmower_cli_api:app_lawnmower_simulation", # String format required for workers
            host="0.0.0.0", 
            port=8000, 
            workers=4,        # For Scalability
            access_log=False, 
            log_level="info"
        )
    elif sys.argv[1] == "--cli":
        # Check if there is an input file
        target_file = "" # No file provided, will use default
        if len(sys.argv) > 2:
            target_file = sys.argv[2]
        # Call Simulator via CLI
        print(f"\n--- Starting CLI Call for Lawnmower Simulator")
        cli_lawnmower_simulation(target_file)  
    else:
        print(f"\n--- Please specify option --api or --cli")