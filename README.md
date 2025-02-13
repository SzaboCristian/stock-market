# Stock market

### Set of APIs for stocks research and portfolio backtesting. Unauthenticated users have limited access to APIs. Authentication implemented using JWT.

## Local deployment

### Requirements:

* Linux based OS (ex. Ubuntu)
* Python >= 3.8
* Docker + docker-compose
* (For MacOS only) chipmk/tap/docker-mac-net-connect

### Install steps:

1. Install Python3.8 + pip + poetry
    1. sudo apt-get update
    2. sudo apt-get install python3.8
    3. python3.8 --version
    4. sudo apt install python3-pip
    5. pip3 --version
    6. pip3 install poetry

2. Install dependencies
    1. poetry lock
    2. poetry install

3. Install docker and docker-compose
    1. https://docs.docker.com/engine/install/ubuntu/
    2. https://docs.docker.com/compose/install/

4. Create .env file following .env\_template (default FLASK\_SECRET=thisissecret)

5. Update docker-compose.yml volume mappings (set project path on local pc)

6. Start elasticsearch (from src)
    1. docker-compose up elasticsearch

7. Start kibana (from src)
    1. docker-compose up kibana

8. Import datasets (from src, with project root set to src)
    1. python3.8 scripts/init_es_database/main.py
    2. python3.8 scripts/populate_es_database/main.py

9. Start webserver
   1. (For Mac OS only, this allows connecting from host network to docker)
      - brew install chipmk/tap/docker-mac-net-connect
      - sudo brew services start chipmk/tap/docker-mac-net-connect
   2. docker-compose up --build webserver

10. APIs available at http://localhost:8080
    1. Test admin/user credentials - admin:admin | user:user (log-in)
    2. Returned JWT (x-access-token apiKey) must be set in order to be able to use all APIs

![](auth.png)
    
![](apis.png)
