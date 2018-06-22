# README

## If app is set up
- Ensure virtual environment is live, and run using:
```sh
$ python manage.py runserver
```

## To use the barebones-flask-postgresql app as a starting point:
- Create new repo on GitHub. In Quick Setup, copy URL (do not initialize the new reop with README, license, or gitignore file)
- In a local shell:
```sh
$ cd ~/gitRepos
$ git clone https://github.com/jjocemac/barebones-flask-postgresql.git
$ mv barebones-flask-postgresql <new-app-name>
$ cd new-app-name
$ rm -rf .git
$ git init
$ git add .
$ git commit -m "First commit"
$ git remote add origin <remote-repository-URL-copied-from-GitHub>
$ git push -u origin master
```
- Set up pipenv:
```sh
$ pipenv --three install
$ pipenv shell
```
- Use pipenv to install new dependencies when needed, and commit new Pipfile/Pipfile.lock to the git repo each time
- Setup local (development) environment. Make sure pipenv shell is disabled first (exit), autoenv is installed (pip install autoenv), and "source <path-to-activate.sh>" is in your bashrc file:
```sh
$ echo "pipenv shell; " > .env
$ echo 'export APP_SETTINGS="config.DevelopmentConfig"' >> .env
```
- Setup postgresql:
- If on foe-linux, do the following:
```sh
$ initdb -D ~/postgres/data/
$ postgres -D ~/postgres/data/
```
- Then (on all systems):
```sh
$ psql
# create database <database_name>;
# \q
$ export DATABASE_URL="postgresql://localhost/<database_name>"
$ echo 'export DATABASE_URL="postgresql://localhost/<database_name>"' >> .env
$ python manage.py db init
$ python manage.py db migrate
$ python manage.py db upgrade
```

- Create heroku app:
```sh
$ heroku create <unique-app-name>
$ heroku config:set APP_SETTINGS=config.ProductionConfig
$ git push heroku master
$ heroku addons:create heroku-postgresql:hobby-dev
$ heroku run python manage.py db upgrade
```
