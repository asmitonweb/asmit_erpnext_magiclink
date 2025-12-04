import frappe
import jwt
from datetime import datetime, timedelta, timezone

def _jwt_secret():
    """Get JWT secret from config"""
    conf = frappe.get_conf()
    return conf.get("jwt_secret_key") or "ecom_api_default_secret_key_for_development_only"

def _jwt_algorithm():
    """Get JWT algorithm from config"""
    conf = frappe.get_conf()
    return conf.get("jwt_algorithm", "HS256")

def generate_jwt_token(email, full_name):
    """
    Generate JWT token for user authentication
    """
    try:
        payload = {
            "user": email,
            "full_name": full_name,
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(days=7)  # Token expires in 7 days
        }

        token = jwt.encode(payload, _jwt_secret(), algorithm=_jwt_algorithm())
        return token

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "JWT Token Generation Error")
        return None
