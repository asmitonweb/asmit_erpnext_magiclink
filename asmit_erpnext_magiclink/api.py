import frappe
from frappe import _
from frappe.utils import get_url
import secrets
from asmit_erpnext_magiclink.utils import generate_jwt_token

@frappe.whitelist(allow_guest=True)
def generate_magic_link(email, name=None, redirect_to=None, mobile_number=None):
    """
    Generates a magic link for the given email.
    If the user does not exist and name is provided, creates a new Website User.
    Args:
        email (str): User's email.
        name (str, optional): User's name for creation.
        redirect_to (str, optional): External URL to redirect to with the token.
        mobile_number (str, optional): User's mobile number to save in Contact.
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

    # Update/Create Contact if mobile number is provided
    if mobile_number:
        _update_user_contact(user, mobile_number)

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

def _update_user_contact(user_name, mobile_number):
    """
    Ensures a Contact exists for the user with the given mobile number.
    """
    try:
        # Check if a contact is already linked to this user
        contact_name = frappe.db.get_value("Dynamic Link", {
            "link_doctype": "User", 
            "link_name": user_name, 
            "parenttype": "Contact"
        }, "parent")

        contact = None
        if contact_name:
            contact = frappe.get_doc("Contact", contact_name)
        else:
            user_doc = frappe.get_doc("User", user_name)
            contact = frappe.new_doc("Contact")
            contact.first_name = user_doc.first_name
            contact.last_name = user_doc.last_name
            contact.email_id = user_doc.email
            contact.is_primary_contact = 1
            contact.append("links", {
                "link_doctype": "User",
                "link_name": user_name
            })

        # Update mobile number in main field
        if contact.mobile_no != mobile_number:
            contact.mobile_no = mobile_number

        # Update mobile number in child table (phone_nos)
        # This is required if the child table is mandatory
        found_in_table = False
        for row in contact.get("phone_nos", []):
            if row.phone == mobile_number:
                found_in_table = True
                break
        
        if not found_in_table:
            contact.append("phone_nos", {
                "phone": mobile_number,
                "is_primary_mobile_no": 1
            })

        contact.save(ignore_permissions=True)

    except Exception as e:
        frappe.log_error(message=f"Error updating contact for user {user_name}: {str(e)}", title="Magic Link Contact Error")


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
    frappe.local.response["location"] = "/all-products"

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

    # Generate JWT using local utility
    jwt_token = generate_jwt_token(user_doc.email, user_doc.full_name)
    if jwt_token:
        response["access_token"] = jwt_token
        response["token_type"] = "X-Authorization"
    
    return response
