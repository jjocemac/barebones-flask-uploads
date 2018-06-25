# README

## If app is set up
- Ensure virtual environment is live, and run using:
```sh
$ python manage.py runserver
```

## To use the barebones-flask-uploads app as a starting point:
- Create new repo on GitHub. In Quick Setup, copy URL (do not initialize the new reop with README, license, or gitignore file)
- In a local shell:
```sh
$ cd ~/gitRepos
$ git clone https://github.com/jjocemac/barebones-flask-uploads.git <new-app-name>
$ cd <new-app-name>
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
```
- Use pipenv to install new dependencies when needed, and commit new Pipfile/Pipfile.lock to the git repo each time
- Setup postgresql database:
- If on foe-linux, do the following:
```sh
$ initdb -D ~/postgres/data/
$ postgres -D ~/postgres/data/
```
- Then (on all systems):
```sh
$ createdb <database_name>
```
- Setup local (development) environment. Make sure pipenv shell is disabled first (exit), autoenv is installed (pip install autoenv), and "source <path-to-activate.sh>" is in your bashrc file:
```sh
$ echo "pipenv shell" > .env
$ echo 'export APP_SETTINGS="config.DevelopmentConfig"' >> .env
$ echo 'export DATABASE_URL="postgresql://localhost/<database_name>"' >> .env
$ echo 'export AWS_ACCESS_KEY_ID=<xxx>' >> .env
$ echo 'export AWS_SECRET_ACCESS_KEY=<yyy>' >> .env
$ cd ../<new-app-name>
```
- Replace "postgresql://localhost/<database_name>" above with "postgresql:///<database_name>" if on personal laptop
- If changes are made to the database schema (through models.py), create a new database migration:
```sh
$ python manage.py db migrate
```
- (In all cases) Apply the upgrades to the database:
```sh
$ python manage.py db upgrade
```
- Should then be able to run locally using:
```sh
$ python manage.py runserver
```
- Create heroku app:
```sh
$ heroku create <unique-app-name>
$ heroku config:set APP_SETTINGS=config.ProductionConfig
$ heroku config:set AWS_ACCESS_KEY_ID=<xxx> AWS_SECRET_ACCESS_KEY=<yyy>
$ heroku addons:create heroku-postgresql:hobby-dev
$ git push heroku master
$ heroku run python manage.py db upgrade
```
- Create an AWS S3 [bucket](https://devcenter.heroku.com/articles/s3)
