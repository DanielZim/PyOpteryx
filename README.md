# PyOpteryx

Authors: Frederic Born (frederic.born@student.kit.edu) and Ewald Rode (ewald.rode@student.kit.edu)

## Technology
 
* Python 3.6.7 
> **Note**
>
> Tested with python 3.6.7. No guarantee for older versions

 
 
## Getting Started
 
These instructions will help you to run this project.
 
 
### Installing
 
A step by step series of examples that tell you have to get a venv running
 
- install virtualenv via cmd line
 
```
pip install virtualenv
```
 
 
- Create and activate virtual environment
    * If python version 3.6.7+ is normaly used:
        ```
        cd /Path/to/Project
        virtualenv --python=Path\to\Python36\python.exe venv
        venv/Scripts/activate
        ```
    * If python version 3.6.7 is installed globally
         ```
        cd /Path/to/Project
        virtualenv venv
        venv/Scripts/activate
        ```
> **Note:**
> 
> source venv/bin/activate (Linux)
 
 
- Install requirements 
```
pip install -r requirements.txt
```
- alternatively
```
pip install -e path\to\pyopteryx\
````

### Usage

Simply take a look at the files pyopteryx/tests/test_lqn_solver.py and pyopteryx/tests/test_lqn_builder.py for usage examples

### Folder structure

- pyopteryx: Source code Folder
    - factories: Factories used in the software
    - tests: usageexamples used for testing the lqn_builder
    - utils: utility functions used throughout the project
- documentation: contains presentations, reports, etc.
- html: pydoc browsable code structure
- pcms: folder containing PCM models
    - BusinessReportingSystem 
    - SimpleHeuristicsExample
- peropteryx_import: subfolders contain PCM model specific allCandidates.csv's
    - BusinessReportingSystem 
    - SimpleHeuristicsExample
