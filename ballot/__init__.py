from flask import Flask
from flask_pyoidc.flask_pyoidc import OIDCAuthentication
import config

app = Flask(__name__)

app.config.from_object(config)

auth = OIDCAuthentication(
    app,
    issuer=app.config['OIDC_ISSUER'],
    client_registration_info=app.config['OIDC_CLIENT_CONFIG']
)

from ballot import routes
