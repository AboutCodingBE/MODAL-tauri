# Plan

This is the execution plan for the simple folder analysis, which has the following features: 
- create new archive
- get archieve overview

Do not deviate from the execution plan. Human verification is necessary between each step. 

## Preferences
- all python code needs to be in `MODAL/python`
- every feature has its own directory containing the necessary python components for that feature. 

## Steps: 

### 1: Create a new archive in memory
In this step, the python components are created that will persist a new archive and start the basic analysis. 
But everything is stored in memory using dictionaries. There is no real database interaction yet

### 2: Link the frontend
In this step, the angular component triggers the python function with Tauri commands via invoke(). 

### 3: get archieve overview
In this step, the python components are created get an overview of all persisted archives. In this step, an overview
comes from in memory dictionaries. 

### 4: Visualise the result of the archive overview
Adjust the angular archive browser so that it correctly shows the result of the get archive overview. Use the `overview-app.png`
screenshot for clear view on how the archive cards should look like. 

### 5: database configuration setup
In this step, we will setup the database, python typesafety and a database migration library. 

### 6: use actual database
In this step, we remove the in memory storage and we use a real database.
