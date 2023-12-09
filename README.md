# Installation Guide

This readme goes over how to run the website portion of our project. Some features, like pairing and controlling matter devices, may not be available, as these functionalities require additional hardware to work correctly.

You can follow these steps to set up your Python environment and run the application.

## Step 1: Install Python

Before setting up the virtual environment, ensure that you have Python installed:

- Download and install Python 3.10.12 from [Python Downloads](https://www.python.org/downloads/).

## Step 2: Set up a Virtual Environment

Create and activate a virtual environment in the directory where your 'app.py' file is located.

### Create a virtual environment:

Run the command on your corresponding operating system to create your virtual environment

- **Windows:** python -m venv virtualenv
	
- **Mac/Linux:** python3 -m venv virtualenv


### Activate your created virtual environment

Activate the virtual environment you just created.

- **Windows:** virtualenv\Scripts\activate
	
- **Mac/Linux:** source virtualenv/bin/activate


### Step 3: Install Requirements

Install the required packages with the virtual environment active by running the following command.

- **Windows/Mac:** pip install -r requirements.txt

### Step 4: Run the app.py 

- **Run in development mode:** flask run --host=0.0.0.0 --debug

If you're running in the development environment, you can browse to 127.0.0.1:5000 to visit the site.
