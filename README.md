# IPDR-app

## Project description
- A IPDR-app has functionality to upload IPDR file, execute using general or dynamic parser, analysis through visuals and numbers, search, download processed IPDR files of different ISP.

- Parser parse the IPDR files and remove unnecessary columns from files. where general parser remove columns base on predefined columns and dynamic parser remove columns base on userdefined columns.

- Used flask, sqlite3, pandas, ipinfo, flasgger library for backend.

- Used jquery, express, axios, tailwind, chart.js for frontend.


## Setup project using Docker

1. Download [Docker](https://docs.docker.com/get-docker/) from internet.

2. Download `docker-compose.yml` file from root directory of project.

3. Run the following command to start the containers using Docker Compose:

    ```bash
    docker-compose up
    ```
4. If `docker-compose.yml`'s defined port already used then change from files and rerun above command.

5. Run following command to stop and remove the containers:

    ```bash
    docker-compose down
    ```
