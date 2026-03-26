# DUNE-DAQ Resource Manager

This package provides a web app and API for interacting with abstract 'resource' objects
in a multi-user software environment. The frontend stack is Django, however any backend
WSGI/ASGI server and database may be configured. When ran in development mode using the
`manage.py` script, a basic Django server and SQLite database are instantiated, and any
code changes will take effect immediately.

Follow the instructions below to quickly set up a development instance.

## TLDR Setup

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
python manage.py migrate

# Start a local test server.
python manage.py runserver
```

Interact with the API using a HTTP client capable of the `POST` method, such as `curl`.

```bash
# Add some resources.
curl -k -X POST "http://127.0.0.1:8000/api/add_resource/" -d "name=resource_1"
curl -k -X POST "http://127.0.0.1:8000/api/add_resource/" -d "name=resource_2"

# Take control.
curl -k -X POST "http://127.0.0.1:8000/api/take_resource/" \
-d "name=resource_1" -d "owner=${USER}" -d "session_id=session_1" -d "session_name=my_session"
curl -k -X POST "http://127.0.0.1:8000/api/take_resource/" \
-d "name=resource_2" -d "owner=${USER}" -d "session_id=session_1" -d "session_name=my_session"

# Release one.
curl -k -X POST "http://127.0.0.1:8000/api/release_resource/" -d "name=resource_1"

# Remove one.
curl -k -X POST "http://127.0.0.1:8000/api/remove_resource/" -d "name=resource_1"

# Query the other.
curl -k -X POST "http://127.0.0.1:8000/api/query_resource/" -d "name=resource_2"
```

One can also register a user using the below command, and login by pointing a web at `http://127.0.0.1:8000/accounts/login/`.

``` bash
python manage.py createsuperuser
```

One may also use this user to modify and administrate the database directly via `http://127.0.0.1:8000/admin/`.
