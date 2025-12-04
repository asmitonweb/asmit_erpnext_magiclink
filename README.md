# Asmit ERPNext Magic Link

A generic Frappe app to generate Magic Links for user login via API.

## Installation

Since this app is located in a custom directory (`c:\Work\frappe_docker\asmit_erpnext_magiclink`), you need to install it manually.

### Steps

1.  **Move the App to `apps` directory**:
    Move the `asmit_erpnext_magiclink` folder into your `frappe-bench/apps` directory.
    *If you are in the `frappe-bench` directory:*
    ```bash
    mv ../../asmit_erpnext_magiclink apps/
    ```

2.  **Install the App (Python)**:
    Install the app in editable mode using pip:
    ```bash
    pip install -e apps/asmit_erpnext_magiclink
    ```

3.  **Register App**:
    Add the app to `apps.txt`:
    ```bash
    echo "asmit_erpnext_magiclink" >> sites/apps.txt
    ```

4.  **Install on Site**:
    ```bash
    bench --site <your-site-name> install-app asmit_erpnext_magiclink
    ```

5.  **Migrate**:
    ```bash
    bench --site <your-site-name> migrate
    ```

## Usage

### 1. Generate Magic Link
**Endpoint**: `POST /api/method/asmit_erpnext_magiclink.api.generate_magic_link`

**Params**:
- `email` (required): User's email address.
- `name` (optional): User's name. If provided and user doesn't exist, a new Website User will be created.
- `redirect_to` (optional): URL to redirect to (e.g., `http://localhost:3000/magic-login`).

**Response**:
Returns a full URL string. If `redirect_to` is used, it appends `?token=...` to that URL.

### 2. Login via Token (Internal)
Used for logging into ERPNext directly.

**Endpoint**: `GET /api/method/asmit_erpnext_magiclink.api.login_via_token`

**Params**:
- `token` (required): The secure token.

### 3. Verify Token (External)
Used by external apps to validate the token and get user details.

**Endpoint**: `GET /api/method/asmit_erpnext_magiclink.api.verify_token`

**Params**:
- `token` (required): The secure token.

**Response**:
```json
{
    "status": "success",
    "user": "user_id",
    "email": "user@example.com",
    "full_name": "User Name"
}
```
