# TLDR Setup

At any point once the server is started, see a summary of resource allocations by
pointing a web browser at `http://127.0.0.1:8000/`.

```bash
# Set up a Python environment.
python -m venv .venv
. .venv/bin/activate
pip install -U pip

# Either requirements.txt for production:
pip install -r requirements.txt

# Or requirements-dev.txt for devopment:
pip install -r requirements-dev.txt

# Set up the configured database.
python manage.py makemigrations
python manage.py migrate

# Start a local test server.
python manage.py runserver

# Add some resources.
curl -k -X POST "http://127.0.0.1:8000/add_resource/" -d "name=resource_1"
curl -k -X POST "http://127.0.0.1:8000/add_resource/" -d "name=resource_2"

# Take control.
curl -k -X POST "http://127.0.0.1:8000/take_resource/" \
-d "name=resource_1" -d "owner=${USER}" -d "session_id=session_1" -d "session_name=my_session"
curl -k -X POST "http://127.0.0.1:8000/take_resource/" \
-d "name=resource_2" -d "owner=${USER}" -d "session_id=session_1" -d "session_name=my_session"

# Release one.
curl -k -X POST "http://127.0.0.1:8000/release_resource/" -d "name=resource_1"

# Remove one.
curl -k -X POST "http://127.0.0.1:8000/remove_resource/" -d "name=resource_1"

# Query the other.
curl -k -X POST "http://127.0.0.1:8000/query_resource/" -d "name=resource_2"
```

One can also register a user using the below command, and login by pointing a web at `http://127.0.0.1:8000/accounts/login/`, although this currently doesn't do anything.

``` bash
python manage.py createsuperuser
```
