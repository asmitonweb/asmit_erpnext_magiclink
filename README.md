# Asmit ERPNext Magic Link

A standalone Frappe app to generate secure, one-time-use magic login links for ERPNext and external applications.

## Features

- **Internal Login**: Log users directly into the ERPNext desk or website.
- **External Login (Headless)**: Authenticate users on external apps (e.g., Next.js, React) using JWT.
- **Mobile Number Support**: Automatically update or create user contacts with mobile numbers.
- **Secure**: Single-use tokens with configurable expiry (default 30 mins).
- **Standalone**: No external dependencies required.

## Installation

1.  Get the app
    ```bash
    bench get-app https://github.com/yourusername/asmit_erpnext_magiclink
    ```

2.  Install the app
    ```bash
    bench --site [site-name] install-app asmit_erpnext_magiclink
    ```

## API Usage

### 1. Generate Magic Link

**Endpoint**: `/api/method/asmit_erpnext_magiclink.api.generate_magic_link`
**Method**: `POST`

**Parameters**:
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `email` | string | Yes | User's email address. |
| `name` | string | No | Name to create user if not exists. |
| `redirect_to` | string | No | External URL to redirect to (for headless mode). |
| `mobile_number` | string | No | Mobile number to save in User Contact. |

**Example (Internal Login)**:
```bash
curl -X POST https://your-site.com/api/method/asmit_erpnext_magiclink.api.generate_magic_link \
    -d "email=user@example.com"
```
**Returns**: `https://your-site.com/api/method/asmit_erpnext_magiclink.api.login_via_token?token=...`

**Example (External Login)**:
```bash
curl -X POST https://your-site.com/api/method/asmit_erpnext_magiclink.api.generate_magic_link \
    -d "email=user@example.com" \
    -d "redirect_to=https://myapp.com/login" \
    -d "mobile_number=1234567890"
```
**Returns**: `https://myapp.com/login?token=...`

### 2. Verify Token (External App)

**Endpoint**: `/api/method/asmit_erpnext_magiclink.api.verify_token`
**Method**: `GET`

**Parameters**:
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `token` | string | Yes | The token received in the URL. |

**Response**:
```json
{
    "status": "success",
    "user": "user@example.com",
    "email": "user@example.com",
    "full_name": "User Name",
    "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
    "token_type": "X-Authorization"
}
```

## Configuration

### JWT Secret
To ensure secure JWT generation, set the `jwt_secret_key` in your `site_config.json`:

```json
{
    "jwt_secret_key": "your-very-secure-secret-key"
}
```

## License

MIT
