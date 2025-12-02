import frappe
from frappe import _
from frappe.utils import get_url
import secrets
try:
    from shopbridge.api.v1.auth_utils import _generate_jwt_token
except ImportError:
    _generate_jwt_token = None

@frappe.whitelist(allow_guest=True)
def generate_magic_link(email, name=None, redirect_to=None):
    """
    Generates a magic link for the given email.
    If the user does not exist and name is provided, creates a new Website User.
    Args:
        email (str): User's email.
        name (str, optional): User's name for creation.
        redirect_to (str, optional): External URL to redirect to with the token.
    """
    if not email:
        frappe.throw(_("Email is required"))

    user = frappe.db.get_value("User", {"email": email}, "name")

    if not user:
        if name:
            # Create new user
            user_doc = frappe.get_doc({
                "doctype": "User",
                "email": email,
                "first_name": name,
                "enabled": 1,
                "user_type": "Website User",
                "send_welcome_email": 0
            })
            user_doc.insert(ignore_permissions=True)
            user = user_doc.name
        else:
            frappe.throw(_("User not found and name not provided for creation"))

    # Generate secure token
    token = secrets.token_urlsafe(32)
    
    # Store token in cache with expiry (30 minutes)
    cache_key = f"magic_link:{token}"
    frappe.cache.set_value(cache_key, user, expires_in_sec=1800)

    # Construct URL
    if redirect_to:
        # Append token to the external URL
        separator = "&" if "?" in redirect_to else "?"
        url = f"{redirect_to}{separator}token={token}"
    else:
        # Default internal login URL
        url = get_url(f"/api/method/asmit_erpnext_magiclink.api.login_via_token?token={token}")
    
    return url

@frappe.whitelist(allow_guest=True)
def login_via_token(token):
    """
    Logs in the user using the provided magic link token.
    Used for internal ERPNext login.
    """
    if not token:
        frappe.throw(_("Token is required"))

    cache_key = f"magic_link:{token}"
    user = frappe.cache.get_value(cache_key)

    if not user:
        frappe.throw(_("Invalid or Expired Link"))

    # Delete token to prevent reuse
    frappe.cache.delete_value(cache_key)

    # Login user
    frappe.local.login_manager.login_as(user)

    # Redirect to shop or home
    frappe.local.response["type"] = "redirect"
    frappe.local.response["location"] = "/app"

@frappe.whitelist(allow_guest=True)
def verify_token(token):
    """
    Verifies the token and returns the user email and JWT access token.
    Used by external apps to validate the token.
    """
    if not token:
        return {"status": "error", "message": "Token is required"}

    cache_key = f"magic_link:{token}"
    user = frappe.cache.get_value(cache_key)

    if not user:
        return {"status": "error", "message": "Invalid or Expired Token"}

    # Delete token to prevent reuse
    frappe.cache.delete_value(cache_key)

    user_doc = frappe.get_doc("User", user)
    
    response = {
        "status": "success",
        "user": user,
        "email": user_doc.email,
        "full_name": user_doc.full_name
    }

    # Generate JWT if shopbridge is available
    if _generate_jwt_token:
        jwt_token = _generate_jwt_token(user_doc.email, user_doc.full_name)
        if jwt_token:
            response["access_token"] = jwt_token
            response["token_type"] = "X-Authorization"
    
    return response
