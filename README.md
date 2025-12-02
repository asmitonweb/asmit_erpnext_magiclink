# Asmit ERPNext Magic Link

A generic Frappe app to generate Magic Links for user login via API. This app allows you to generate secure, one-time login links for your users, enabling a password-less login experience.

## Features

- **Generate Magic Links**: Create secure, time-limited login links via API.
- **Auto-User Creation**: Optionally create a new Website User if the email doesn't exist.
- **Custom Redirects**: Specify where the user should be redirected after login.
- **Token Verification**: Verify tokens externally to authenticate users in third-party apps.

## Installation

You can install this app using `bench get-app`.

1.  **Get the App**:
    ```bash
    bench get-app https://github.com/asmitonweb/asmit_erpnext_magiclink.git
    ```

2.  **Install on Site**:
    ```bash
    bench --site <your-site-name> install-app asmit_erpnext_magiclink
    ```

3.  **Migrate** (Just build is fine for newer versions of ERPNext):
    ```bash
    bench --site <your-site-name> migrate
    ```

## Usage

### 1. Generate Magic Link
**Endpoint**: `POST /api/method/asmit_erpnext_magiclink.api.generate_magic_link`

**Params**:
- `email` (required): User's email address.
- `name` (optional): User's name. If provided and user doesn't exist, a new Website User will be created.
- `redirect_to` (optional): URL to redirect to (e.g., `https://your-frontend.com/magic-login`).

**Response**:
Returns a full URL string. If `redirect_to` is used, it appends `?token=...` to that URL.

### 2. Login via Token (Internal)
Used for logging into ERPNext directly.

**Endpoint**: `GET /api/method/asmit_erpnext_magiclink.api.login_via_token`

**Params**:
- `token` (required): The secure token.

**Behavior**:
Logs the user in and redirects them to `/app` (or the configured default).

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

## License

MIT

## System Design

View the [System Design](system_design.md) to understand the authentication flow.
