from functools import wraps
from flask import request, jsonify

def tenant_auth_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        tenant_id_in_url = kwargs.get("tenant_id")
        tenant_id_in_header = request.headers.get("X-Tenant-ID")

        if not tenant_id_in_header or tenant_id_in_header != tenant_id_in_url:
            return jsonify({"error": "Unauthorized: Tenant ID mismatch or missing"}), 401

        return func(*args, **kwargs)
    return wrapper