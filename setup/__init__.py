from flask import Flask, request, current_app
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os


# Initialize the SQLAlchemy and Migrate objects
db = SQLAlchemy()
migrate = Migrate()
# Init. the  Mail object
mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    migrate.init_app(app, db, compare_type=True, render_as_batch=True)
    mail.init_app(app)

    from setup.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from setup.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    # Code below is for logging errors
    if not app.debug and not app.testing:
        # Logging errors by mail:
        # If app not in debug mode, and there is a mail server
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            secure = None
            # If encrypted connections are enabled(secure protocols are used)
            if app.config['MAIL_USE_TLS']:
                secure =()
            mailport = (app.config['MAIL_SERVER'], app.config['MAIL_PORT'])
            mail_handler = SMTPHandler(
                mailhost= mailport,
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs= app.config['ADMINS'], subject='Microblog Failure',
                credentials=auth, secure = secure
            )
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        if app.config['LOG_TO_STDOUT']:
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.INFO)
            app.logger.addHandler(stream_handler)
        else:
            # Logging errors to log file:
            # If the path doesn't exist, create it
            if not os.path.exists('logs'):
                os.mkdir('logs')
            # Create the RotatingFileHandler object, 
            # set its custom formatting and logging level
            file_handler = RotatingFileHandler(
                filename='logs/microblog.log',
                maxBytes=10240,
                backupCount=10
            )
            file_handler.setFormatter(
                logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:line%(lineno)d]')
            )
            file_handler.setLevel(logging.INFO)
            # Add the handler to app.logger, set logging level and info
            app.logger.addHandler(file_handler)
            
        app.logger.setLevel(logging.INFO)
        app.logger.info('Microblog startup')

    return app


from setup import models
        
