# Docker NGINX FLASK POSTGRES stack

This docker environment will run a bare bones setup for an NGINX server, flask app, and postgres server, all running in their own containers.

## How to start

1. Have docker installed

2. Pull down this repo

3. CD into the base directory for this repo.

4. Execute the following terminal command: ```docker-compose up```

5. Point your browser to ```0.0.0.0:8080```

6. Take the wheel from here, it's your website!

### NOTE

Nothing in this example repo actually does anything with the PostgreSQL database. This docker environment just sets it up to run alongside the other containers. Do with it what you will!

## License

I don't provide a license for this, for it's just a compilation of other open source software. Use at your own risk, as is, I'm not repsonsible for anything you do with this. 

## Acknowledgments

* Python
* Docker
* NGINX
* uWSGI
* Flask
