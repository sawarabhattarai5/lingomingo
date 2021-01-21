# Application Folder

## Purpose

The purpose of this folder is to store all the source code and related files for your team's application. Source code MUST NOT be in any of folder. <strong>YOU HAVE BEEN WARNED</strong>

You are free to organize the contents of the folder as you see fit. But remember your team is graded on how you use Git. This does include the structure of your application. Points will be deducted from poorly structured application folders.

## Please use the rest of the README.md to store important information for your team's application.



# Application Folder Structure:

django/ : our backend framework

django/lingomingo: our Django project

django/mainapp : the main Django app, all site related backend files shall reside here

django/mainapp/static/: static files such as js/css resides here, can be collected for deployment by running ```./manage.py collectstatic``` in production set up

django/tempaltes/mainapp : template html files for our front end team





# Setting Up For Development:

#### Prerequisites:

[Python 3.8](https://www.python.org/downloads/)

[pip3](https://pip.pypa.io/en/stable/installing/)

[virtualenv](https://virtualenv.pypa.io/en/latest/)

### Linux/MacOS:

clone this GitHub repo

``` git clone https://github.com/CSC-648-SFSU/csc648-04-sp20-team02.git ```

go to django folder

``` cd application/django```

create venv

```python3 -m venv venv```

activate venv

```source venv/bin/activate```

make sure everything is installed on requirement.txt

```pip install -r requirement.txt```

[make]() manage.py executable

``` chmod +x manage.py```

migrate database

```./manage.py migrate```

populate the language table

```python3 scripts\populate_language_table.py```

**If you are having issue with the script, i've put it into one of the views so that you can run the script by accessing a page.**

**Solution:**

startup the webserver **before** creating a superuser below

``` ./manage.py runserver```

visit [localhost:8000/setup](localhost:8000/setup)

and check console output, if you see languages being added you can proceed to the next step



create super user to use the django admin panel

```./manage.py createsuperuser```



once those steps are done you can open django folder with your favorite python editor (personally i prefer [PyCharm](https://www.jetbrains.com/pycharm/))

once you have the project open you can either run the project in PyCharm or run the local server in terminal

```./manage.py runserver```



### Windows 

clone this GitHub repo

``` git clone https://github.com/CSC-648-SFSU/csc648-04-sp20-team02.git ```

go to django folder

``` cd application\django```

After cloning the repo , create a virtual environment

```virtualenv venv```

activate your venv

```venv\Scripts\activate```

install the the required dependency

```pip install -r requirement.txt```

migrate database

```manage.py migrate```

populate the language table

```python3 scripts\populate_language_table.py```

create super user to use the django admin panel

```manage.py createsuperuser```



once those steps are done you can open django folder with your favorite python editor (personally i prefer [PyCharm](https://www.jetbrains.com/pycharm/))

once you have the project open you can either run the project in PyCharm or run the local server in terminal

```manage.py runserver```





**Happy Coding! :)**
