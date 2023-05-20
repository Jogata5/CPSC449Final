# CPSC449Final Project

# Description
This project is to demonstrate the capabilities of FastAPI and MongoDB with an example of a bookstore API. This bookstore will contain books that have an Id, Title, Description, Price, Stock, and Number of Sales as it's variables/key-value pairs. 


# Team Members
Julian Ogata
Lori Cha

# Installation
## Create a virtual environment and activate (Linux)
python -m venv venv
source venv/bin/activate

## Install requirements
pip install requirements.txt

# Run MongoDB
Ensure that mongoDB is installed, if not: pip install mongo

sudo service mongodb start

# Run Webpage
uvicorn main:app --reload

Go to browser and enter url: http://127.0.0.1:8000/

# Run Test Webpage
uvicorn main:app --reload

Go to browser and enter url: http://127.0.0.1:8000/docs

# Run Postman
Fork from our project here: https://www.postman.com/orbital-module-specialist-58395705/workspace/cpsc449/overview