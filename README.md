Aflutter
========

Aflutter is a minimalist, Amazon S3 backed file host.

Requirements
============
You'll need the following:

* A [Heroku](https://www.heroku.com/) account, if you want to deploy to Heroku.
* An [Amazon AWS](http://aws.amazon.com/) account, including your AWS Access Key and Secret Key
* An [Amazon S3](http://aws.amazon.com/s3/) bucket, for storing the images

Setup
=====
Amazon S3
* Create a bucket in S3
* Right click on the bucket, and select Properties
* Under Permissions, click Edit CORS Configuration
* Change the domain name(s) below to match your configuration:
```xml
<CORSConfiguration>
    <CORSRule>
        <AllowedOrigin>http://aflutter.example.com</AllowedOrigin>
        <AllowedOrigin>https://aflutter.example.com</AllowedOrigin>
        <AllowedMethod>GET</AllowedMethod>
        <AllowedMethod>POST</AllowedMethod>
        <AllowedMethod>PUT</AllowedMethod>
        <AllowedMethod>HEAD</AllowedMethod>
        <AllowedHeader>*</AllowedHeader>
    </CORSRule>
    <CORSRule>
        <AllowedOrigin>*</AllowedOrigin>
        <AllowedMethod>GET</AllowedMethod>
        <MaxAgeSeconds>3000</MaxAgeSeconds>
        <AllowedHeader>Authorization</AllowedHeader>
    </CORSRule>
</CORSConfiguration>
```

Local development setup:
```bash
    # Clone the repo
    git clone https://github.com/taeram/aflutter.git
    cd ./aflutter

    # Setup and activate virtualenv
    virtualenv .venv
    source ./.venv/bin/activate

    # Install the pip requirements
    pip install -r requirements.txt

    # Create the development database (SQLite by default)
    python manage.py database migrate upgrade
    python manage.py database setup

    # Install less.js for on the fly compilation of .less files
    npm install -g less

    # Export the config variables
    export AWS_ACCESS_KEY_ID=secret \
           AWS_SECRET_ACCESS_KEY=secret \
           AWS_REGION=us-east-1 \
           AWS_S3_BUCKET=aflutter-bucket \
           MAX_UPLOAD_SIZE=5368709120 \
           SECRET_KEY=secret_key

    # Note that SECRET_KEY is a hash used by the Flask application to secure cookies, and should be randomized
    
    # Start the application, prefixing with the required environment variables
    python server.py
```

Heroku setup:
```bash
    # Clone the repo
    git clone https://github.com/taeram/aflutter.git
    cd ./aflutter

    # Create your Heroku app, and the addons
    heroku apps:create
    heroku addons:add heroku-postgresql

    # Promote your postgres database (your URL name may differ)
    heroku pg:promote HEROKU_POSTGRESQL_RED_URL

    # Tell Heroku we need a custom buildpack (for python + nodejs)
    heroku config:add BUILDPACK_URL=https://github.com/ddollar/heroku-buildpack-multi.git

    # Set the flask environment
    heroku config:set FLASK_ENV=production

    # Set the application config
    heroku config:set AWS_ACCESS_KEY_ID=secret \
                      AWS_SECRET_ACCESS_KEY=secret \
                      AWS_REGION=us-east-1 \
                      AWS_S3_BUCKET=aflutter-bucket \
                      MAX_UPLOAD_SIZE=5368709120 \
                      SECRET_KEY=secret_key

    # Note that SECRET_KEY is a hash used by the Flask application to secure cookies, and should be randomized

    # Add a Google Analytics ID if you want to track visitors
    heroku config:set GOOGLE_ANALYTICS_ID=<your Google Analytics id>

    # Push to Heroku
    git push heroku master
    
    # Create the production database
    heroku run python manage.py database migrate upgrade
    heroku run python manage.py database setup

```

Upgrading to a new Release
==========================

When upgrading to a new release, simply pull down the new copy, and migrate the
database:

```
python manage.py database migrate upgrade
```

If you're migrating a Heroku app, just prefix the above command with `heroku run`.
