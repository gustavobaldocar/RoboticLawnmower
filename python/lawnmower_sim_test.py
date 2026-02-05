"""
Project: 
Automated Robotic Lawnmower Simulator

File: ./python/lawnmower_sim_test.py

Objectives: 
    Auto Test for Automated Robotic Lawnmower Simulator

Author: gustavobaldocarvalho @ yahoo.com

Version: 31.01.2026 - Creation
"""

import pytest
from python.lawnmower_sim import LawnmowerSim

def test_scenario_01_valid_path() -> None:
    """Verifies that a valid path cuts all grass and doesn't crash."""
    print(f"\n---  Auto Test test_scenario_01_valid_path - valid path cuts all grass and doesn't crash")
    lm_sim = LawnmowerSim("ValidTest", 3, 2, [[1,1], [0,1]], [0,0])
    # path: [down, down, right] as per example 
    status = lm_sim.execute_path(["down", "down", "right"])
    assert status["all_grass_cut"] is True
    assert status["did_mower_crash"] is False
    assert status["uncut_grass_remaining"] == 0

def test_scenario_02_fence_crash() -> None:
    """Verifies crash detection when going off-grid."""
    print(f"\n---  Auto Test test_scenario_02_fence_crash - crash detection when going off-grid")
    lm_sim = LawnmowerSim("FenceTest", 5, 5, [], [0,0])
    status = lm_sim.execute_path(["up"]) # Off-grid 
    assert status["did_mower_crash"] is True
    assert status["crash_reason"] == "Crashed into Fence"

def test_scenario_03_rock_crash() -> None:
    """Verifies crash detection when hitting a rock."""
    print(f"\n---  Auto Test test_scenario_03_rock_crash - crash detection when hitting a rock")
    lm_sim = LawnmowerSim("RockTest", 5, 5, [[1,1]], [0,0])
    status = lm_sim.execute_path(["down", "right"]) # Hits rock 
    assert status["did_mower_crash"] is True
    assert status["crash_reason"] == "Crashed into Rock"

def test_scenario_04_incomplete_cut() -> None:
    """Verifies logic for uncut grass remaining."""
    print(f"\n---  Auto Test test_scenario_04_incomplete_cut - logic for uncut grass remaining")
    lm_sim = LawnmowerSim("IncompleteTest", 3, 2, [[1,1], [0,1]], [0,0])
    status = lm_sim.execute_path(["down"]) # Only 1 move 
    assert status["all_grass_cut"] is False
    assert status["uncut_grass_remaining"] == 2 # 4 total grass squares - 2 cut 