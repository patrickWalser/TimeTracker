# Refactoring plan: MVC-Architecture

## Goal
- Split businesslogic and presentation
- use a controller for the communication between GUI and model

## Layers
1. **Model:** Processes and stores data (Study, Semester, Module, Entry).
2. **Controller:** Communicates betweeen view and model (TimeTracker).
3. **View:** Presents data and handles user input (TimeTrackerGUI, Charts).

## Todo
- [] move businesslogic from GUI to controller
- [] handle data and calculations in the model
- [] delegate GUI logic to controller
- [] create tests for new structure