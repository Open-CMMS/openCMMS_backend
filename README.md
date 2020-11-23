# OpenCMMS_backend

![example workflow name](https://github.com/Open-CMMS/openCMMS_backend/workflows/master/badge.svg)   ![example workflow branch](https://github.com/Open-CMMS/openCMMS_backend/workflows/dev/badge.svg)    ![GitHub license](https://img.shields.io/github/license/Open-CMMS/openCMMS_backend)  ![GitHub contributors](https://img.shields.io/github/contributors/Open-CMMS/openCMMS_backend)

The aim of this project is to enable any company to manage the maintenance of its equipment in a simple way.

We thus propose a management of users with different levels of rights as well as the possibility to create new groups with specific rights.

In addition, we offer the possibility of creating equipment types as well as equipment with attributes such as brand, capacity, etc...

Then, we also offer the possibility of adding DataProviders that will allow you to automatically retrieve values from your equipment in order to update its attributes in the database.

Finally, we offer a front end interface that can be coupled to this project and which is located here: 



# Installing the project 

In this part we will explain how to install this project locally or globally. The installation process has been tested with Debian 10 container.
First, you have to download the project and put it in a specific directory, in our example we put the project in `/root/backend/`

Make sure that you have all your packages up to date : `apt-get update`

# Locally

## Install the dependencies

### With a virtual environment
- Install required package : `apt install -y python3-venv`
- Create a virtual environment : `python3 -m venv env`
- Activate the environment : `. env/bin/activate`
- Install the dependencies using the requirements.txt which comes with re project : `pip install -r requirements.txt` 

### With Pipenv
A FAIRE

## Install the database

For this project we used a Postgresql database.

- Install PostgreSQL : `apt install -y postgresql-11`
- Do this command only if you are using a separate container from the one where the project is : `nano /etc/postgresql/11/main/postgresql.conf` and modify the line `listen_addresses` with `listen_addresses='0.0.0.0'`
- Modify this file : `nano /etc/postgresql/11/main/pg_hba.conf` by adding this line to the end of the file : `host all all all md5`
- We will now add a django user and it's database. If you want to change the name of the user, the password and the name of the database, you also have to change it in the `base_settings.py` file :
    - `su - postgres`
    - `createuser django`
    - `createdb django -O django`
    - `psql`
    - `alter user django with password 'django';`
    - `alter user django with createdb;`
    - `exit()` x2
    - `service postgresql restart`


## Launch the server

Move to the root folder of the project, in our case `/root/backend`, and execute `python manage.py migrate` and then `python manage.py runserver`
If you are executing the project in your computer you can access it at http://127.0.0.1:8000/api/admin (make sure you have created a superuser with `python manage.py createsuperuser`)
Else, you can go to the nginx configuration section



# Globally

To install this project globally, thus in production mode, we have used gunicorn. There are a few steps to follow to make this work.

## Install the database

For this project we used a Postgresql database.

- Install PostgreSQL : `apt install -y postgresql-11`
- Do this command only if you are using a separate container from the one where the project is : `nano /etc/postgresql/11/main/postgresql.conf` and modify the line `listen_addresses` with `listen_addresses='0.0.0.0'`
- Modify this file : `nano /etc/postgresql/11/main/pg_hba.conf` by adding this line to the end of the file : `host all all all md5`
- We will now add a django user and it's database. If you want to change the name of the user, the password and the name of the database, you also have to change it in the `base_settings.py` file :
    - `su - postgres`
    - `createuser django`
    - `createdb django -O django`
    - `psql`
    - `alter user django with password 'django';`
    - `alter user django with createdb;`
    - `exit()` x2
    - `service postgresql restart`


## Install the dependencies

To make gunicorn work, we have to install the packages globally with pip3
- Install pip3 : `apt install -y python3-pip`
- Install the dependencies using the requirements.txt which comes with re project : `pip3 install -r requirements.txt`
- Install gunicorn and dependencies :
    - `apt install -y gunicorn3`
    - `pip3 install gevent`
- Migrate the modifications to the database from /root/backend: `python3 manage.py migrate`
- Create the environment file : `nano /root/env_file` and put this in it : 
    ```
    PYTHONUNBUFFERED=TRUE
    ```
    This file enables you to pass environment variables to gunicorn
- Create the gunicorn service : `nano /etc/systemd/system/gunicorn.service` and put this in it
    ```
    [Unit]
    Description=The gunicorn server for openCMMS
    After = network.target

    [Service]
    PermissionsStartOnly = true
    WorkingDirectory=/root/backend
    User=root
    EnvironmentFile=/root/env_file
    ExecStart=/usr/bin/gunicorn3 openCMMS.wsgi:application -b 127.0.0.1:8000 -w 3 --pid /run/gunicorn.pid --access-logfile=/var/log/gunicorn/server_access.log --error-logfile=/var/log/gunicorn/error.log --capture-output --worker-class=gevent --worker-connections=1000 --log-level debug
    ExecReload=/bin/kill -s HUP $MAINPID
    ExecStop=/bin/kill -s TERM $MAINPID
    KillMode=process
    Restart=on-failure
    RestartSec=1s

    [Install]
    WantedBy=multi-user.target
    ```
    Make sure that the working directory and the environment file are correct
- Create the folder for gunicorn logs : `mkdir /var/log/gunicorn`
- Reload all the services : `systemctl daemon-reload`
- Start the gunicorn service : `systemctl start gunicorn.service`


# Nginx configuration

As we serve both back and front end, we have set up Nginx in order to distribute the requests according to their destination. In this part we will explain how to install and setup Nginx.

- Install nginx : `apt install -y nginx`
- Setup the default site : `nano /etc/nginx/sites-available/default` and put this in it :
    ```
    ##
    # You should look at the following URL's in order to grasp a solid understanding
    # of Nginx configuration files in order to fully unleash the power of Nginx.
    # https://www.nginx.com/resources/wiki/start/
    # https://www.nginx.com/resources/wiki/start/topics/tutorials/config_pitfalls/
    # https://wiki.debian.org/Nginx/DirectoryStructure
    ##

    # Default server configuration
    #
    server {
            listen 80 default_server;
            listen [::]:80 default_server;

            # SSL configuration
            #
            listen 443 ssl default_server;
            listen [::]:443 ssl default_server;
            #
            # Note: You should disable gzip for SSL traffic.
            # See: https://bugs.debian.org/773332
            #
            # Read up on ssl_ciphers to ensure a secure configuration.
            # See: https://bugs.debian.org/765782
            #
            # Self signed certs generated by the ssl-cert package
            # Don't use them in a production server!
            #
            # include snippets/snakeoil.conf;

            root /var/www/openCMMS/;

            # Add index.php to the list if you are using PHP
            index index.html index.htm index.nginx-debian.html;

            server_name _;

            location / {
                    if ($uri ~ ^/api/){
                            proxy_pass http://127.0.0.1:8000$uri$is_args$args;
                            add_header    'Access-Control-Allow-Origin' '*' always;
                            add_header    'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
                            add_header    'Access-Control-Allow-Headers' 'Accept,Authorization,Cache-Control,Content-Type,DNT,If-Modified-Since,Keep-Alive,Origin,User-Agent,X-Requested-With' always;
                            add_header    'Access-Control-Allow-Credentials' 'true' always;
                    }
                    # First attempt to serve request as file, then
                    # as directory, then fall back to displaying a 404.
                    try_files $uri $uri/ /index.html =404;
            }

            location /static {
                    autoindex on;
                    alias /root/backend/staticfiles;
            }

            location /media {
                    autoindex on;
                    alias /root/media;
            }
            
    }
    ```
    Make sure that the alias match your root folder for the project
- Change the user in the nginx configuration : `nginx /etc/nginx/nginx.conf` and change `user www-data;` to `user root;`
- Reload nginx : `service nginx restart`



