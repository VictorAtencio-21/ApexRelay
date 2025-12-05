# f1_api/api/v1/races_routes.py
from flask import Blueprint, jsonify, request

from ...utils.validators import validate_query_params

races_bp = Blueprint("races_bp", __name__)


@races_bp.get("/health")
def health():
    """Simple endpoint to verify the races blueprint works."""
    validate_query_params(request.args, {})
    return jsonify({"status": "ok", "service": "races"}), 200
