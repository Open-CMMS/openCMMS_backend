# OpenCMMS_backend

![example workflow name](https://github.com/Open-CMMS/openCMMS_backend/workflows/master/badge.svg) ![example workflow branch](https://github.com/Open-CMMS/openCMMS_backend/workflows/dev/badge.svg) ![GitHub license](https://img.shields.io/github/license/Open-CMMS/openCMMS_backend) ![GitHub contributors](https://img.shields.io/github/contributors/Open-CMMS/openCMMS_backend)

The aim of this project is to enable any company to manage the maintenance of its equipment in a simple way.

We thus propose a management of users with different levels of rights as well as the possibility to create new groups with specific rights.

In addition, we offer the possibility of creating equipment types as well as equipments with attributes such as brand, capacity, etc...

Then, we also offer the possibility of adding DataProviders that will allow you to automatically retrieve values from your equipment in order to update its attributes in the database.

Finally, we offer a front end interface that can be coupled to this project and which is located here:

# Creating a cmms user

To prevent security breaches, we have created a cmms user. To do so follow theese lines :

- Create user cmms : `adduser cmms`
- Add sudo package : `apt install sudo`
- Add user to the sudoers group : `adduser cmms sudo`
- Connect as cmms user : `su cmms`

# Installing the project

In this part we will explain how to install this project in development and production mode. The installation process has been tested with Debian 10 container.

First, you have to download the project and put it in a specific directory, in our example we put the project in `/home/cmms/backend/`

Make sure that you have all your packages up to date : `sudo apt-get update`

# Production Mode

## Install the dependencies - With a virtual environment

- Install required package : `sudo apt install -y python3-venv`
- Create a virtual environment : `python3 -m venv cmms_env`
- Activate the environment : `. cmms_env/bin/activate`
- Move to the project repository : `cd /home/cmms/backend/`
- Install the dependencies using the requirements.txt which comes with the project : `pip install -r requirements.txt`
- Install gunicorn : `pip install gunicorn`
- Install gunicorn dependencies : `pip install gevent==1.4.0 greenlet==0.4.14`
- Create the gunicorn service : `sudo nano /etc/systemd/system/gunicorn.service` and put this in it

  ```
  [Unit]
  Description=The gunicorn server for openCMMS
  After = network.target

  [Service]
  PermissionsStartOnly = true
  WorkingDirectory=/home/cmms/backend
  User=cmms
  ExecStart=/home/cmms/cmms_env/bin/gunicorn openCMMS.wsgi:application -b 127.0.0.1:8000 -w 3 --preload --worker-class=gevent --worker-connections=1000
  ExecReload=/bin/kill -s HUP $MAINPID
  ExecStop=/bin/kill -s TERM $MAINPID
  KillMode=process
  Restart=on-failure
  RestartSec=1s

  [Install]
  WantedBy=multi-user.target
  ```

  Make sure that the working directory is correct

- Reload all the services : `sudo systemctl daemon-reload`
- Start the gunicorn service : `sudo systemctl start gunicorn.service`

## Install the database

For this project we used a Postgresql database.

- Install PostgreSQL : `sudo apt install -y postgresql-11`
- Do this command only if you are using a separate container from the one where the project is : `sudo nano /etc/postgresql/11/main/postgresql.conf` and modify the line `listen_addresses` with `listen_addresses='0.0.0.0'`
- Modify this file only if you are using a separate container from the one where the project is : `sudo nano /etc/postgresql/11/main/pg_hba.conf` by adding this line to the end of the file : `host all all all md5`
- We will now add a django user and it's database. If you want to change the name of the user, the password and the name of the database, you also have to change it in the `base_settings.py` file :
  - `sudo su - postgres`
  - `createuser django`
  - `createdb django -O django`
  - `psql`
  - `alter user django with password 'django';`
  - `alter user django with createdb;`
  - `ctrl+d` x2
  - `sudo service postgresql restart`
  - Migrate django's database (with the virtual environment activated) : `python manage.py migrate`

# Nginx configuration

As we serve both back and front end, we have set up Nginx in order to distribute the requests according to their destination. In this part we will explain how to install and setup Nginx.

- Install nginx : `sudo apt install -y nginx`
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
          client_max_body_size 20M;

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
                  alias /home/cmms/backend/staticfiles;
          }

          location /media {
                  autoindex on;
                  alias /home/cmms/backend/media;
          }

  }
  ```

  Make sure that the alias match your root folder for the project

- Change the user in the nginx configuration : `sudo nano /etc/nginx/nginx.conf` and change `user www-data;` to `user cmss;`
- Reload nginx : `sudo service nginx restart`

# Configure the project

## Setup email fonctionnality

If you want the email part to be effective you have to change a few things in the `base_settings.py` file located in the `openCMMS` folder:

- Modify the `EMAIL_BACKEND` varibale to : `'django.core.mail.backends.smtp.EmailBackend'`
- Setup your email configuration according to your email server, for example :
  - EMAIL_HOST = 'localhost'
  - EMAIL_PORT = 25
  - EMAIL_USE_TLS = False
  - EMAIL_HOST_USER = ''
  - EMAIL_HOST_PASSWORD = ''
  - DEFAULT_FROM_EMAIL = `'No-Reply <no-reply@your-domain.fr>'`
- Modify your `BASE_URL` so it matches your website

## Others

If you setup the project to be accessed from the internet, you may have to had your site address to the `CSRF_TRUSTED_ORIGINS` variable, like for example :

```
  CSRF_TRUSTED_ORIGINS = [
  'your.website.com'
  ]
```
