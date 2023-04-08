Seedtag Codetest 2: Backend Engineer
====================================


## Running local environment

### Build the image
```bash
docker-compose build
```

### Run the container
```bash
docker-compose up
```

### Running the tests
```bash
docker compose  run --rm web python -m pytest
```

## API docs:
```
http://localhost:8888/docs
```


## Notes
All the test cases were added to the `test_main.py`.
I wanted to keep the project as simple as possible:

```
.
├── app                  # "app" is a Python package containing the main application code
│   ├── main.py          # "main" module that defines the '/radar' endpoint for the API
│   ├── schemas.py        # "schemas" module containing all the pydantic models used by the application
│   ├── tests
|   │   ├── test_main.py     # "test_main" module containing integration tests for the '/radar' endpoint
|   │   └── test_services.py    # "test_services" module containing unit tests for the RadarSystem class
│   └── services.py         # "services" module containing the definition of the RadarSystem class
├── docker-compose       # Configuration file, which allows running multiple containers as a service
├── Dockerfile           # Dockerfile used to build the application image
└── requirements.txt     # List of Python dependencies required by the application, used by pip to install them
```

If the project were to be bigger with more endpoints, I would have separated '/radar' into a new app with its own
schemas and routers, and divided the requirements into base, dev, and prod like:

```
.
├── app
│   ├── radar
│   │   ├── constants.py
│   │   ├── router.py
│   │   ├── schemas.py
│   │   └── service.py
│   ├── tests
│   │   ├── radar
│   │   │   ├── test_main.py
│   │   │   └── test_utils.py
│   └── main.py
├── requirements
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt
├── docker-compose
└── Dockerfile
```

In addition, I would explore the option of versioning the API with subdirectories.
