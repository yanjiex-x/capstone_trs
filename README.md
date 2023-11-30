# Capstone Project (TRS Forensics)

**Description:** Capstone Project done in TRS Forensics - A simple Flask app to ease the vulnerability assessment report writing process!

## Building the Flask app (Ubuntu)

In case the web app needs to be ported to another virtual machine... if so, please refer to the handover document on necessary items to have before executing the web app

### Pre-Requisites

- Python 3.9 (tested and originally deployed in this version)
- pip
- virtual environment (recommended)

### (Recommended) Activating the virtual environment - Ubuntu

> python -m venv env
> 
> source env/bin/activate

### Installing the necessary packages

> pip install -r requirements.txt

### Installing wkhtmltopdf

> sudo apt-get -y install wkhtmltopdf

## Executing the Flask app

Activate the virtual environment before running the program!

Then

> python app.py
