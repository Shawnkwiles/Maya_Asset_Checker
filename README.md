# Maya Asset Checker

## Overview
This tool allows the detection and cleanup of many common issues with 3D assets.

This is a quality control tool designed to prevent pipeline issues by detecting issues in geometry, naming, and uv's from a quick check by the user. It was written in Python and uses the Maya Python API including maya.cmds. I also leveraged Pyside2/PyQt to make a more attractive UI and to improve readability. 

---

## Features
- **Easy to read UI**: The tool does a series of checks and appropriately colors and adds a checkmark based on the results.
- **Issue detection**: The tool performs a number of checks relating to history, transformations, geometry errors, naming, and uv issues. 
- **Ability to fix or point out several issues**: The Delete History and Freeze Transformations buttons will immediately fix those issues and recheck the results. The select faces with more than 4 sides button will selected Ngons on the selected meshes and display the number found.
- **Allows multiple meshes**: The tool allows the checking of more than one mesh at a time and checks by selection.
---


