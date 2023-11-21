# Hello World Django <!-- omit from toc -->

- [Install Django and Create Project](#install-django-and-create-project)
- [Gitignore](#gitignore)
- [Setting up Pyenv](#setting-up-pyenv)
- [Setting up Poetry](#setting-up-poetry)
- [Testing the Server Locally](#testing-the-server-locally)
- [Login to AWS](#login-to-aws)
- [Create Elastic Beanstalk Application and Environment](#create-elastic-beanstalk-application-and-environment)
- [Creating Elastic Beanstalk Django Config](#creating-elastic-beanstalk-django-config)

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

## Testing the Server Locally

1. Let's test the server locally to see that everything's functional:

    ```sh
    poetry shell
    python manage.py runserver
    ```

2. Navigate to <http://localhost:8000/> and you should see a default Django page.
3. You can stop the local server with CTRL-C

## Login to AWS

1. [Install the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
2. Configure SSO, choosing whatever details like default region, etc. you want:

    ```sh
    aws configure sso
    ```

3. Take note of the profile name that is returned. Example: `--profile AdministratorAccessManaged-2**********6`
4. Login:

    ```sh
    aws sso login
    ```

## Create Elastic Beanstalk Application and Environment

1. We need to create both an "application" as well as an "environment" on Elastic Beanstalk.
2. Start by creating the application:

    ```sh
    eb init -p python-3.11 <app_name> --profile <profile_name> --region <region>
    ```

3. Creating the application is fairly quick and you can confirm via the AWS Management Console that it's been created.
4. Run this once more to setup your local computer to communicate with this application:

    ```sh
    eb init --profile <profile_name> --region <region>
    ```

    Answer the following:
      - Do you wish to continue with CodeCommit? No
      - Do you want to set up SSH for your instances? Yes

5. Now create the Elastic Beanstalk environment:

    ```sh
    eb create <environment_name> --profile <profile_name> --region <region>
    ```

6. Creating the environment can take a while, and it will likely fail as there is more configuration we need to do.

## Creating Elastic Beanstalk Django Config

1. In the root of the project, create a new folder called `.ebextensions`, and in it a file called `django.config`.
2. These files should be committed into version control
3. In the `django.config` file, place the following contents:

    ```yml
    packages:
      yum:
        git: []
    option_settings:
      aws:elasticbeanstalk:container:python:
        WSGIPath: hello_world_django.wsgi:application
      aws:elasticbeanstalk:application:environment:
        DJANGO_SETTINGS_MODULE: hello_world_django.settings
    ```

4. We tell Elastic Beanstalk to install Git, as well as where to find the Django WSGI (Web Server Gateway Interface) and the Django settings module to use.
5. Now, redeploy by simply running:

    ```sh
    eb deploy
    ```

6. You can always monitor the status by running:

    ```sh
    eb status
    ```
