# Abstract User Subscriptions

An API for tracking user's Api subscriptions and allows for different users to be on different subscriptions and plans.

## Overview

A user's billing subscriptions are tracked through 4 models which are Api, Subscription, SubscriptionPlan, and UserSubscription.
- **Api**: The Api model tracks the different Apis available on the platform. All users can read the different Apis but only admins can create. Users see their subscription plans on the detailed route `/apis/{id}/subscription_plans/`.
- **Subscription**: A Subscription belongs to an Api and consists of many plans. Users get assigned to a Subscription when they signup. This is only available to admins and users do not know that different subscriptions with different plans exist.
- **SubscriptionPlan**: A SubscriptionPlan is one of many plans that belong to a subscription. It tracks the calls allowed and pricing for each plan. It is only available to admins.
- **UserSubscription**: A UserSubscription tracks the current Subscription and the active SubscriptionPlan for a user. If a free tier exists in their Subscription, a user is automatically signed up to it. It is only available to admins.

## Common tasks

### Signup a user

Signup can be done at: `/users/signup/`

### View a users subscription plans for an api

`/apis/{id}/subscription_plans/`

### Add a new subscription and plans (admin only)

If it is a brand new API (`/api/`) you will need to first add the Api but if the API already exists you can go straight to adding the subscription (`/subscriptions/`). You will probably want to hold off on having the new subscription being available to new users until after you have added the plans. With the SubscriptionPlan (`/subscription_plans/`) model you can add the new plans and their details to the subscription you just created.

### Setting a users subscription or plan (admin only)

You can do this by updating the UserSubscription (`/user_subscriptions/`) object for your user.

## Local Setup

### Install

In a fresh pip env:

```pip install -r requirements.txt```

### Postgres config

Create a new postgres table/user with the defaults below or set environment variables with correct information. The defaults and environment variables defined in settings.py are:
```
    'default': {
        'NAME': os.environ.get('DB_NAME', 'abstractapi'),
        'USER': os.environ.get('DB_USER', 'abstractapi'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
```

### Load Data

The basic data includes one admin user with a username and password of `admin` and one normal user with username and password `user`. Load the data with the following:
```
python manage.py migrate
python manage.py loaddata basicdata
```

### Run

```
python manage.py runserver
```

### Test

```
python manage.py test
```

### Docker

Start docker and postgres inside of docker with docker compose using the command:
```
docker-compose up --build
```

Migrate the database and add the test data with:
```
docker-compose exec web python manage.py flush --no-input
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py loaddata basicdata
```

# Further thoughts on the challenge

The challenge definition left a lot up to be decided. I tried to cover all of the explict cases requested while also thinking about how the API would operate in daily use. Here are some additional thoughts for why things were made the way they were.

## Django rest framework

I chose to use django rest framework as it is built for data only APIs such as this one. It has great abstractions and can do so much with so little code.

## Explicit Subscription model

I first tinkered with not having an explicit subscription model, but ended up coming back to add it. It felt very error prone and not as extendable to not have it. I like that the Subscription model can explicitly say if it is the default model for new users as it could allow you to easily switch or A/B test different subscriptions without being locked in to only taking the highest version. It also means that specific enterprise subscriptions can be easily handled as they will never be the default for all users.

## Could users not be assigned to a Subscription until they view or use it?

Right now I assign users to their subscription and possible free tier plan when they register. It could also be interesting to not assign users until they view the plans or use the API, but the challenge asked for them to be assigned at create time so that's what I did. Services like Firebase require you to activate the individual services you'd like even if they are free so this could be another entry point for users to be assigned to a subscription.

## Handling new API creation

Users will be left hanging without a subscription to an API when the API is created after the user. I added a check to add users to the current default subscription if they didn't have one when trying to view their plans. This check would probably have to exist when using the API or anywhere else the user needs to know their subscription. As said above, it could make sense to require users to activate an API so their subscription is locked in then.

## TODOs before production ready

Since this is just a coding challenge, obviously this project is lacking some key things to be production ready. I tried to focus my time on the things explicitly asked for and add as much as I could to get it as close as I could. More tests and a production ready docker setup with gunicorn are the first two things that come to mind. It would probably also make sense to have a single endpoint where you can create a new subscription with plans in one step. I would also add django-filter so that you can filter the endpoints with query parameters. This would make finding the data you need easier and would allow an admin frontend to filter for the data you need.