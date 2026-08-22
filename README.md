# reputation-based-marketplace

Reputation based marketplace. The process for trades is shown here:

![Trade Process](./seller%20%26%20buyer%20sequence.svg)

## Technologies used

Python & Django

## Getting Started
    
Activate the virtualenv for your project.
    
Install project dependencies:

    $ pip install -r requirements.txt
    
    
Then simply apply the migrations:

    $ python manage.py migrate
    $ python manage.py makemigrations


Also collect the static files into the static root folder:

    $ python manage.py collectstatic


You can now run the development server:

    $ python manage.py runserver


You can now also run the tests with:

    $ python manage.py test
