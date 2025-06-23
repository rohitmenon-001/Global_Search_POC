from flask import request, abort

# Simulated tenant-user mapping
USER_TENANT_MAP = {
    "apikey-abc": "tenant_ABC",
    "apikey-xyz": "tenant_XYZ",
}

def get_tenant_from_api_key():
    api_key = request.headers.get("X-API-KEY")
    return USER_TENANT_MAP.get(api_key)

def tenant_auth_required(func):
    def wrapper(*args, **kwargs):
        requested_tenant = kwargs.get("tenant_id")
        current_tenant = get_tenant_from_api_key()

        if not current_tenant:
            abort(401, description="Missing or invalid API key.")

        if requested_tenant != current_tenant:
            abort(403, description="Forbidden: Tenant access mismatch.")

        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper
