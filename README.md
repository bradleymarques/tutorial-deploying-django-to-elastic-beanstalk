# Hello World Django

This simple project will guide you in building and deploying a Django application
to [Amazon Elastic Beanstalk](https://aws.amazon.com/elasticbeanstalk/).

We will use the following:

1. Django
2. Pyenv
3. Poetry
4. A simple SQLite database file
5. Elastic Beanstalk

## Install Django and Create Project

1. First, download django:

    ```sh
    pip install django
    ```

2. Then, start a boilerplate Django project:

    ```sh
    django-admin startproject hello_world_django
    cd hello_world_django
    ```

## Gitignore

Setup a reasonable gitignore file.

1. First, create it:

    ```sh
    touch .gitignore
    ```

2. Then ensure it has the following content:

    ```conf
    .DS_Store
    .env
    .venv
    *.sqlite3
    __pycache__
    **/__pycache__/**
    __pycache__/
    .pytest_cache
    static/
    ```

## Setting up Pyenv

1. [Install pyenv](https://github.com/pyenv/pyenv?tab=readme-ov-file#installation)
2. At the time of writing, the latest Python version Elastic Beanstalk supports is `Python 3.11 running on 64bit Amazon Linux 2023`
3. Install that version using pyenv:

    ```sh
    pyenv install 3.11.2
    ```

4. Set that locally:

    ```sh
    pyenv local 3.11.2
    ```

## Setting up Poetry

1. If you haven't already, [install poetry](https://python-poetry.org/docs/#installation).
2. Configure it as such:

    ```sh
    poetry config virtualenvs.create true
    poetry config virtualenvs.in-project true
    ```

3. Now initialize the poetry project:

    ```sh
    poetry init
    ```

    1. For `Compatible Python versions` enter `3.11.2`
    2. Add the following dependencies:
       1. `Django` (use latest version)

4. Now install:

    ```sh
    poetry install
    ```

5. Elastic Beanstalk requires a `requirements.txt` file. We can freeze the current requirements from Poetry like this:

    ```sh
    poetry export --without-hashes --format=requirements.txt > requirements.txt
    ```

6. **NOTE**: Every time we change requirements like adding new libraries via `poetry add`, we will need to recreate the above `requirements.txt` file.
