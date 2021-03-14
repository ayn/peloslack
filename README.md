# PeloSlack 🚴‍♂️💬


## Local installation and running

```sh
pip install -r requirements.txt
```

Copy over `.env.example` to `.env` or run `heroku config -s -a peloslack > .env` and change `REDIS_URL` to local.

```sh
heroku local
```

which will run the webserver, clock process, and worker as defined in `Procfile`.

OR

### To run the script

```sh
cd peloslack
python peloslack.py
```

### To run the server

```sh
python server.py
```