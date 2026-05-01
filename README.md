# DUNE-DAQ Resource Manager

This package provides a web app and API for interacting with abstract 'resource' objects
in a multi-user software environment. The frontend stack is Django, however any backend
WSGI/ASGI server and database may be used. A few helper scripts are provided:

- `resource-manager-manage`: an interface to manage the database and run a test server
- `resource-manager-run-gunicorn`: run a production server with gunicorn

Follow the instructions below to quickly set up a development instance.

## TLDR Setup

At any point once the server is started, see a summary of resource allocations by
pointing a web browser at `http://127.0.0.1:8000/`.

```bash
# Set up a Python environment:
python -m venv .venv
. .venv/bin/activate
pip install -U pip

# Either install for production:
pip install .

# Or install for devopment:
pip install -e .[dev]

# Set up the database:
resource-manager-manage migrate

# Either start a local test server:
resource-manager-manage runserver

# Or start a gunicorn server:
resource-manager-run-gunicorn
```

Interact with the API using a HTTP client capable of the `POST` method, such as `curl`.
One can either access the latest API version at `http://127.0.0.1:8000/api/`, or access
e.g. API version `v1` at `http://127.0.0.1:8000/api/v1/`.

```bash
# Add some resources.
curl -k -X POST "http://127.0.0.1:8000/api/add_resource/" \
-d "names=resource_1,resource_2"

# Request control.
curl -k -X POST "http://127.0.0.1:8000/api/request_resource/" \
-d "names=resource_1,resource_2" -d "user_name=${USER}" \
-d "session_id=session_1" -d "session_name=my_session"

# Release one.
curl -k -X POST "http://127.0.0.1:8000/api/release_resource/" \
-d "names=resource_1" -d "user_name=${USER}"

# Remove one.
curl -k -X POST "http://127.0.0.1:8000/api/remove_resource/" \
-d "names=resource_1"

# Query the other.
curl -k -X POST "http://127.0.0.1:8000/api/query_resource/" \
-d "names=resource_2"
```

One can also register a user using the below command, and login by pointing a web at
`http://127.0.0.1:8000/accounts/login/`.

``` bash
resource-manager-manage createsuperuser
```

One may also use this user to modify and administrate the database directly via
`http://127.0.0.1:8000/admin/`.
