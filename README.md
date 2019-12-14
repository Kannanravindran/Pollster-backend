# Pollster-backend

This project is the code for API server build using Flask. This serverless framework is lightweight and<br/>
perfectly suits the use-case. 


## Setting up environment

The prerequisites for running this application is [Python3](https://www.python.org/downloads/). 

or can be done using command-line

```
sudo apt-get update
sudo apt-install python3-pip
sudo apt install python3-venv
```

Clone the repository to a local directory.
Navigate into the project folder

The following command creates a virtual sandbox environment of python 
```
python3 -m venv venv
source venv/bin/activate
```
To exit from the environment 
```
deactivate
```

## Running code locally

Activating the environment
```
cd Pollster-backend/
source venv/bin/activate
```

Installing the dependencies
```
pip install -r requirements.txt
```

Using gunicorn to the Flask application with concurrent workers
```
gunicorn --workers=20 --threads=2 --bind 127.0.0.1:5000 app:app
```

Once the server is up and running, the APIs should be exposed and accessible from the frontend.
Check this [link](https://github.com/Kannanravindran/Pollster) out for setting up the frontend part of the application
