=============================
django-profile-repo
=============================

Django-profile-repo is a simple application that allows you to manage multi-model user 
profiles in a unified manner. Without needing to add a Foreign key to each model.


    
Requirements
-------------

* Django 1.7+
* Django contenttypes framework enabled (included in INSTALLED_APPS)


Installation
------------

To install just type::

    pip install django-profile-repo

After installation is complete add app to INSTALLED_APPS::
    
    INSTALLED_APPS = [
        ...
        'profile_repo'
    ]

And migrate db::

    ./manage.py makemigrations 
    ./manage.py migrate



Usage
-----

For example on an app containinig this two models::

    class PrintConfig(models.Model):
        dpi = models.PositiveIntegerField(default=300)
        color = models.BooleanField(default=False)
        ...

    class DeliveryAddress(models.Model):
        name = models.CharField()
        address_line1 = models.CharField()
        address_line2 = models.CharField()
        ...

You can associate them with an user profile using **set_profile**::
    
    from django_profile.models import *

    >> user = request.user
    >> default_print_config = PrintConfig.objects.create(dpi=200)
    >> default_dispatch_address = DispatchAddress.object.create(
        name = 'John Smith',
        address_line1 = 'Main St 1')

    >> set_profile(user, default_print_config)
    >> set_profile(user, default_dispatch_address)

To retrieve them later with **get_profile** and the class of the model::

    >> print_config = get_profile(user, PrintConfig)

When the model you tried access wasn't associated an exception is raised::

    from django.core.exceptions import ObjectDoesNotExist

    try:
        print_defaults = get_profile(user, PrintConfig)
    except ObjectDoesNotExist:
        print_defaults = PrintConfig()

For convenience the function **get_or_create_profile** is provided, with the
expected meaning::

    >> profile = get_or_create_profile(user, PringConfig, defaults={dpi: 340})

To remove a profile use **del_profile**::

    >> del_profile(user, PrintConfig)

Or if you also want the referenced model deleted::

    >> del_profile(user, PrintConfig, delete_model=True)
    
You can also retrieve all the models associated with an user with **get_all_profiles**::

    >> get_all_profiles(user)
    [<PrintConfig: PrintConfig object>, <DeliveryAddress: DeliveryAddress object>]

Lastly this associations are unique in the sense that only one model of each class 
can be associated with an user at a time. If you try to add to a user profile two
models of the same class the older one will be discarded.


Running Tests
--------------

To run tests::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install -r requirements_test.txt
    (myenv) $ python runtests.py



Credits
---------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
