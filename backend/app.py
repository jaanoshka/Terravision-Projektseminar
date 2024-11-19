from flask import Flask
from blueprints.mesh_blueprint import mesh_bp
from blueprints.image_blueprint import image_bp
from flask_cors import CORS

app = Flask(__name__)

app.register_blueprint(mesh_bp)
app.register_blueprint(image_bp)

CORS(app,origins="*")
#CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
#CORS(app)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000, debug=True)

