# reputation-based-marketplace

Reputation based marketplace. The game that this site was created for did not at the time have a trade feature. Players were only able to gift items to each other. Therefore trading with other users was risky. In order to facilitate trading this site was created for sellers to list their items and services for sale and to keep track of the strustworthiness of sellers and buyers. The process for trades is shown here:

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
