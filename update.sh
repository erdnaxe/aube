#!/bin/sh

# Migrate database
python3 manage.py migrate --noinput

# Collect statics
python3 manage.py collectstatic --noinput

# Compile messages
python3 manage.py compilemessages --noinput

exec "$@"
