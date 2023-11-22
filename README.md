# Deploying a Django Application to Elastic Beanstalk <!-- omit from toc -->

Up to date as of: **November 2023**

- [Introduction](#introduction)
- [Install Django and Create Project](#install-django-and-create-project)
- [Gitignore](#gitignore)
- [Setting up Pyenv](#setting-up-pyenv)
- [Setting up Poetry](#setting-up-poetry)
- [Testing the Server Locally](#testing-the-server-locally)
- [Login to AWS](#login-to-aws)
- [Create Elastic Beanstalk Application and Environment](#create-elastic-beanstalk-application-and-environment)
- [Creating Elastic Beanstalk Django Config](#creating-elastic-beanstalk-django-config)
- [Setting Environment Variables](#setting-environment-variables)
- [Creating a simple test webpage and ensuring database migrations](#creating-a-simple-test-webpage-and-ensuring-database-migrations)
- [Static Files and Django Compressor](#static-files-and-django-compressor)

## Introduction

This simple project will guide you in building and deploying a Django application to [Amazon Elastic Beanstalk](https://aws.amazon.com/elasticbeanstalk/).

We will use the following:

1. **Django** as a web development framework
2. **Pyenv** to manage our Python version
3. **Poetry** to manage Python libraries
4. A simple **SQLite** database file for now
5. Elastic Beanstalk to host
6. Bootstrap 5.3 (source SCSS)
7. **Django-compressor** and **django-libsass** to compile sass into css

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

## Setting Environment Variables

1. If you visit the environment now, it is likely that you will get a Django error page with the message "DisallowedHost Invalid HTTP_HOST header"
2. This is because we need to amend the `ALLOWED_HOSTS` setting in the Django settings file (`hello_world_django/settings.py`).
3. There are also other settings in the Django settings file that we should extract as environment variables, namely:
    - `DJANGO_SETTINGS_MODULE`
    - `SECRET_KEY`
    - `DEBUG`
    - `ALLOWED_HOSTS`
4. To do this, let's install `python-dotenv` so we can use a `.env` file locally:

    ```sh
    poetry add python-dotenv
    ```

5. Remember that whenever we make changes here, we need to update the `requirements.txt` file:

    ```sh
    poetry export --without-hashes --format=requirements.txt > requirements.txt
    ```

6. Locally, create a `.env.example` file and `.env` (gitignored) file both with contents:

    ```sh
    export DJANGO_SETTINGS_MODULE="hello_world_django.settings"
    export SECRET_KEY="secret-key-123"
    export DEBUG="True"
    export ALLOWED_HOSTS="localhost"
    ```

7. Alter the `hello_world_django/settings.py` file as such:

    ```py
    import os

    import dotenv

    dotenv.load_dotenv()
    from pathlib import Path

    # Build paths inside the project like this: BASE_DIR / 'subdir'.
    BASE_DIR = Path(__file__).resolve().parent.parent


    # Quick-start development settings - unsuitable for production
    # See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

    # SECURITY WARNING: keep the secret key used in production secret!
    SECRET_KEY = os.environ.get("SECRET_KEY", None)

    # SECURITY WARNING: don't run with debug turned on in production!
    DEBUG = os.environ.get("DEBUG", "True") == "True"

    ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")
    ```

8. Get the value to set for ALLOWED_HOSTS by running `eb status` and copying the CNAME record.
9. For the secret key, open up a django shell locally using `python manage.py shell` and run:

    ```py
    from django.core.management.utils import get_random_secret_key

    print(get_random_secret_key())
    ```

10. Set the environment variables either through the AWS Web Console or the CLI (Note it is best to do this as 1 command as opposed to one command per environment variable, as each time they are altered the environment will need to restart):

    ```sh
    eb setenv DEBUG="True" SECRET_KEY="..." ALLOWED_HOSTS="..."
    ```

11. Redeploy to get the changes we made to the settings file: `eb deploy`
12. Also make sure the local server still works: `python manage.py runserver`
13. You should see the Django rocket ship both locally and on Elastic Beanstalk

## Creating a simple test webpage and ensuring database migrations

1. Create a simple django app by running `python manage.py startapp hello_world`.
2. Create a new `View` in `hello_world/views.py`:

    ```py
    # hello_world/views.py`
    from typing import Any, Dict

    from django.contrib.auth.models import User
    from django.views.generic import TemplateView


    class HelloWorldView(TemplateView):
        template_name = "hello_world/hello_world.html"

        def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
            context = super().get_context_data(**kwargs)
            context.update({"user_count": User.objects.count()})
            return context
    ```

3. Add this to the app's `urls.py`:

    ```py
    # hello_world/urls.py
    from django.urls import path

    from hello_world.views import HelloWorldView

    urlpatterns = [
        path("", HelloWorldView.as_view(), name="hello-world"),
    ]
    ```

4. Add the template (note the path here as you will need to create some sub folders):

    ```html
    <!-- hello_world/templates/hello_world/hello_world.html -->
    <h1>Hello World</h1>
    <p>There are {{ user_count }} users on this website</p>
    ```

5. Register the new app in our `INSTALLED_APPS` setting:

    ```py
    # hello_world_django/settings.py

    INSTALLED_APPS = [
        # ... other apps already listed here
        "hello_world"
    ]
    ```

6. Add the URLs to the base site URLs:

    ```py
    # hello_world_django/urls.py

    from django.contrib import admin
    from django.urls import include, path

    urlpatterns = [
        path("admin/", admin.site.urls),
        path("", include("hello_world.urls")),
    ]
    ```

7. Locally, run the server. You will likely get an `OperationalError at / no such table: auth_user`.
8. This is because we have not migrated the database.
9. Do that locally by stopping the server, then running `python manage.py migrate` and then running the server again.
10. You should see "Hello World - There are 0 users on this website"
11. We need to tell Elastic Beanstalk to perform the same database migration command every time we deploy.
12. To do this, add the following to the `.ebextensions/django.config` file:

    ```yml
    packages:
      yum:
        git: []
    option_settings:
      aws:elasticbeanstalk:container:python:
        WSGIPath: hello_world_django.wsgi:application
      aws:elasticbeanstalk:application:environment:
        DJANGO_SETTINGS_MODULE: hello_world_django.settings
    container_commands:
      01_migrate:
        command: |
          export $(cat /opt/elasticbeanstalk/deployment/env | xargs)
          source $PYTHONPATH/activate
          python ./manage.py migrate --noinput
        leader_only: true
    ```

13. Some notes here:
    - We prefix the command name with `01_` because we want it to run before some other commands we will add later
    - The line `export ...` exports the Elastic Beanstalk environment variables to the process running the command
    - We also add `--noinput` to the migration command to prevent it waiting for user input it will never receive
14. Once these changes have been made, redeploy and you should (hopefully) see the same thing on Elastic Beanstalk as locally.

## Static Files and Django Compressor

1. Let's assume that we want to use Bootstrap but apply some overrides like our own colors.
2. To do this, we'll need to download the Bootstrap SCSS and use a tool to compile the SCSS into CSS.
3. First, head over to [this URL](https://getbootstrap.com/docs/5.3/getting-started/download/#source-files) to download the source files of Bootstrap 5.3.2
4. Once downloaded, extract it and copy the entire `scss` folder into a new folder in the project here:
    - `hello_world/static/hello_world/css/bootstrap/scss`
5. Now install `django-bootstrap-v5`, `django-compressor`, `django-libsass` and recreate the requirements.txt file:

    ```sh
    poetry add django-bootstrap-v5
    poetry add django-compressor
    poetry add django-libsass
    poetry export --without-hashes --format=requirements.txt > requirements.txt
    ```

6. Follow the [install instructions for django-bootstrap-v5](https://django-bootstrap-v5.readthedocs.io/en/latest/installation.html)

7. Follow the [install instructions for django-compressor](https://django-compressor.readthedocs.io/en/stable/quickstart.html)
    - Add to `INSTALLED_APPS`
    - Add `STATICFILES_FINDERS`
    - Define `STATIC_URL = "static/"`
    - Define `STATIC_ROOT = "collected_static_files/"`
    - Define `COMPRESS_ROOT = STATIC_ROOT`

8. Follow the install instructions for [django-libsass](https://github.com/torchbox/django-libsass):
    - Add `COMPRESS_PRECOMPILERS`

9. Create a new root theme scss file here: `hello_world/static/hello_world/css/main.scss`
10. Place the following contents in the file to override Bootstrap's primary color with pure blue:

    ```scss
    $blue: #0000ff !default;

    $primary: $blue !default;

    @import "./bootstrap/scss/bootstrap";
    ```

11. Alter `hello_world.html` to contain:

    ```html
    {% load static %}
    {% load compress %}
    {% load bootstrap5 %}
    <!DOCTYPE html>
    <html lang="en-US">
      <head>
        {% compress css %}
          <link rel="stylesheet" type="text/x-scss" href="{% static 'hello_world/css/main.scss' %}" />
        {% endcompress %}
        {% bootstrap_javascript %}
        <title>Hello World Django</title>
      </head>
      <body>
        <h1 class="text-primary">Hello World</h1>
        <a href="#" class="btn btn-primary">There are {{ user_count }} users on this website</a>
      </body>
    </html>
    ```

12. Locally, run the server, and ensure that you see some very blue elements.
13. Redeploy to Elastic Beanstalk: `eb deploy` and check Elastic Beanstalk
14. It is likely you will see an error `*.css was blocked due to MIME type ("text/html") mismatch (X-Content-Type-Options: nosniff)`
