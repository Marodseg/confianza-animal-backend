# Confianza Animal backend

## Install project dependencies

Run `pip install -r requirements.txt` to install the dependencies and being able to run the application.

## Development server

Run the `main.py` file. Navigate to `http://localhost:8000`. The application will automatically reload if you change any of the source files.

Another option is creating a `venv` with `Python 3.9` to run the server. 

## Documentation

Navigate to `http://localhost:8000/docs` to open the Swagger UI with the API endpoints.

## Code formatting

To check the code format, run `black --check .` or a specific file with `black --check "app/file.py"`.

In order to format all the files, run `black .` or a specific file with `black "app/file.py"`.