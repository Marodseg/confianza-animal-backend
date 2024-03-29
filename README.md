# Trabajo de Fin de Grado: *API para la gestión de mascotas en adopción*

***

## Install project dependencies

Run `pip install -r requirements.txt` to install the dependencies and being able to run the application.

Don't forget to set the environment variable `GOOGLE_APPLICATION_CREDENTIALS` as expected in `database.py` and
complete the `.env_template.py` and rename it to `.env`.

## Development server

Run the `main.py` file. Navigate to `http://localhost:8000`. The application will automatically reload if you change any of the source files.

Another option is creating a `venv` with `Python 3.9` to run the server. 

## Documentation

Navigate to `http://localhost:8000/docs` to open the Swagger UI with the API endpoints.

## Code formatting

To check the code format, run `black --check .` or a specific file with `black --check "app/file.py"`.

In order to format all the files, run `black .` or a specific file with `black "app/file.py"`.

## Environment

In order to create the environment, run `conda env create -f conda_environment.yml`.

After that, activate the environment with `conda activate confianza_animal`.

## Test database

To create the test database, run **(only for the first time)** `python app/config/populate_test_database.py`
and it will create the database with the test data to run the tests.


***

## License
This project is published under the [GNU General Public License v3](https://opensource.org/licenses/GPL-3.0) license.
