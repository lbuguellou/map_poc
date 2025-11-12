# Docker

## Setup of the environment

**What you need**
* Git and a github account (with an SSH key)
* Docker (Linux / Mac / Windows) and an account
* An IDE or editor of your choice (Cursor, SublimeText, Vim...)

**Gitlab**

You need to create your private and public keys

```bash
cd ~/.ssh
ssh-keygen -t ed25519 -C "<comment>"
```

Go to your gitlab profile and copy/paste your public key

**Source Code**

```bash
cd ~ && mkdir -p lab && cd lab
git clone git@github.com:lbuguellou/map_poc.git
cd map-streamlit && cp .env.example .env
cd map-fastapi && cp .env.example .env
```
notes:
* Configure your .env to use local services like openai, google api...

**Hosts**

Add those entries to your host file

```bash
127.0.0.1 map.solutions
127.0.0.1 api.solutions
```

## Run the container
```bash
cd ~/lab/map-poc/docker-python
docker-compose up
```
notes:
* Use the `-d` option to detach the process, but for the first time, it is a good idea to see the output
* Use the `--build --force-recreate` options to force the re-creation of the containers

if needed:
* Use `docker exec -it web bash` to access the container web (streamlit)
* Use `docker exec -it web bash` to access the container web (fastapi)
* Use `docker exec -it redis bash` to access the container redis


## Check the environment
With your browser, go to `http://map.solutions:80/`
With your browser, go to `http://api.solutions:81/`

Transfer errors to `laetitiabug@gmail.com` or update this doc if needed

