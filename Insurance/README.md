## ABBOUT the assignment
The DIS_insurrance applikation is built on the Bank applikation given for the course DIS. It has been transformed to a Insurrance site were as an customer you can see the claims already in the database, the same with your policies. As a employee you can see the polices the insurrance company offers. In general the focus has been on the customer part of the applikation. The data base is an artifficial one, we have created for this task, so it resembelse the bank data base to some deegree, but now it have all the neccesary features to work and act as an insurrance application. 
The Regex match that was mandatory, is in the schema.sql and is used to make sure that when a customer is created, that their email adress is on a correct form.    

    git repository:  https://github.com/esbenkloster/DIS

## Setting up: 
To run the program you have to follow the same steps as when setting up the banking applikation. The steps are below and are the same. When logging in as either an user og an employee, you can find the password and CPR/ID in the schema.sql. but examples could be the following: 
Customer: 
CPR: 1001
password: password123

Employee: 
ID: 601
password: admin123 

## Requirements:
Run the code below to install the necessary modules.

    pip install -r requirements.txt


#### notes. When solving codepage problems 
For WINDOWS: Loading data into postgres using psql needs a codepage set. Invoking a cmd shell like this set the codepage: 

    cmd /c chcp 65001   

This makes a subshell with the codepage set to UTF8. 'cmd /c chcp 1252' makes a subshell with the codepage set to 1252. The requirements may have to be run again in the subshell. And you might also have to run the requirements again when invoking a virtual environment (see below). 

## Database init
1. set the database in __init__.py file.
2. run schema.sql, schema_ins.sql, schema_upd.sql in your database
3. run sql_ddl/ddl-customers-001-add.sql in your database.

Example: 

    psql -d{database} -U{user} -W -f schema.sql
   
#### notes
For Ubuntu add host (-h127.0.0.1) to psql: 

    psql -d{database} -U{user} -h127.0.0.1 -W -f schema.sql

## Running flask
### The python way

    python3 run.py

### The flask way.

    export FLASK_APP=run.py
    export FLASK_DEBUG=1           (Replaces export FLASK_ENV=development)
    export FLASK_RUN_PORT=5004     (Optional if you want to change port numbe4. Default port is port 5000.)
    flask run

#### notes
For Windows you may have to use the SET command instead of EXPORT. Ex set FLASK_APP=run.py; set FLASK_DEBUG=1; flask run. This worked for me. Also remeber to add the path to your postgres bin-directory in order to run (SQL interpreter) and other postgres programs in any shell.


### The flask way with a virual environment.

Set up virtual environment as specified in https://flask.palletsprojects.com/en/1.1.x/installation/ (OSX/WINDOWS)
vitualenv may be bundled with python.

#### OSX: 

    mkdir myproject
    cd myproject

Create virtual environment in folder

    python3 -m venv .venv

Activate virtual environment in folder

    . .venv/bin/activate

Install flask

    pip install Flask

Set environment variables and start flask

    export FLASK_APP=run.py
    export FLASK_DEBUG=1           (Replaces export FLASK_ENV=development)
    export FLASK_RUN_PORT=5000     (Optional if you want to change port number. Default port is port 5000.)
    flask run
 

#### WINDOWS:

Create virtual environment in folder

    mkdir myproject
    cd myproject
    py -3 -m venv .venv

Activate virtual environment in folder

    .venv\Script\activate
    pip install Flask

Set environment variables and start flask

    set FLASK_APP=run.py
    set FLASK_DEBUG=1           (Replaces export FLASK_ENV=development)
    set FLASK_RUN_PORT=5000     (Optional if you want to change port number. Default port is port 5000.)
    flask run



