from flask import Flask, jsonify
from flask_cors import CORS
from config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    CORS(app, supports_credentials=True, origins=["*"])

    from routes.auth_routes import auth_bp
    from routes.product_routes import product_bp
    from routes.sale_routes import sale_bp
    from routes.purchase_routes import purchase_bp
    from routes.analytics_routes import analytics_bp
    from routes.catalog_routes import category_bp, supplier_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(sale_bp)
    app.register_blueprint(purchase_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(supplier_bp)

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal server error"}), 500

    @app.route("/health")
    def health():
        return jsonify({"status": "ok"})

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=Config.DEBUG, host="0.0.0.0", port=5000)