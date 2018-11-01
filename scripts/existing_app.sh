#!/usr/bin/env bash
heroku git:remote -a $app_name
git push heroku master
