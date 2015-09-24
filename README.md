SportEasy breaking Django mvc
=============================

> Breaking Django MVC for a better scalability


Please refer to presentation available on [speakerdeck](https://speakerdeck.com/charlesvdulac)

License
=======

This code is distributed under the terms of the MIT license. See the
``LICENSE.txt`` file.

Installation
============

Let’s create a virtual environment called ``se_b_mvc``:

    mkvirtualenv se_b_mvc
    workon se_b_mvc
    pip install --requirement=requirements.txt
    python manage.py syncdb --noinput

Usage
=====

Via local import
----------------


In project  ``settings.py``:

    SERVICES = {
        'championship': {
            'PROXY': {
                'CLASS': 'LocalServiceProxy',
                'OPTIONS': {}
            }
        }
    }

Then, run ``python manage.py runserver``

Via RPyC lib
------------

In project  ``settings.py``:

    SERVICES = {
        'championship': {
            'CLASS': 'RpycServiceProxy',
            'OPTIONS': {
                'url': '127.0.0.1:4444'
            }
        }
    }

Open 2 terminals:

* In the first one, run ``python manage.py serviced``
* In the second one, run ``python manage.py runsever``
