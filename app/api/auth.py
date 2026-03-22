"""Authentication API endpoints.

Use Cases:
- UC-R: Register account (email/password or Gmail)
- UC-L: Login account (email/password or Gmail OAuth)
- UC-FP: Forgot password with OTP
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.auth_service import AuthService
from app.services.email_service import EmailService

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user.
    
    UC-R: Register account
    ---
    tags:
      - Authentication
    summary: Register a new user account
    description: Create a new user account with email and password
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              format: email
              example: user@example.com
            password:
              type: string
              format: password
              minLength: 6
              example: "securePassword123"
            first_name:
              type: string
              example: "John"
            last_name:
              type: string
              example: "Doe"
    responses:
      201:
        description: User created successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: "User registered successfully"
            user:
              $ref: "#/definitions/User"
      400:
        description: Validation error
        schema:
          $ref: "#/definitions/Error"
      409:
        description: Email already registered
        schema:
          $ref: "#/definitions/Error"
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    email = data.get('email', '').strip()
    password = data.get('password', '')
    first_name = data.get('first_name', '').strip() or None
    last_name = data.get('last_name', '').strip() or None
    
    user, error = AuthService.register_user(email, password, first_name, last_name)
    
    if error:
        return jsonify({'error': error}), 400 if 'Invalid' in error or 'required' in error else 409
    
    return jsonify({
        'message': 'User registered successfully',
        'user': user.to_dict()
    }), 201


@auth_bp.route('/register/google', methods=['POST'])
def register_google():
    """
    Register or login with Google OAuth.
    
    UC-R: Register account with Gmail
    
    Request Body:
        google_id: Google's unique user ID
        email: User's email from Google
        first_name: First name from Google
        last_name: Last name from Google
    
    Returns:
        200: Login/Register successful
        400: Invalid data
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    google_id = data.get('google_id', '').strip()
    email = data.get('email', '').strip()
    first_name = data.get('first_name', '').strip() or None
    last_name = data.get('last_name', '').strip() or None
    
    if not google_id or not email:
        return jsonify({'error': 'google_id and email are required'}), 400
    
    result, error = AuthService.login_with_google(google_id, email, first_name, last_name)
    
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify({
        'message': 'Login successful',
        **result
    }), 200


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login with email and password.
    
    UC-L: Login account
    ---
    tags:
      - Authentication
    summary: Login to get JWT tokens
    description: Authenticate with email and password to receive access and refresh tokens
    security: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              format: email
              example: user@example.com
            password:
              type: string
              format: password
              example: "securePassword123"
    responses:
      200:
        description: Login successful
        schema:
          $ref: "#/definitions/LoginResponse"
      400:
        description: Missing email or password
        schema:
          $ref: "#/definitions/Error"
      401:
        description: Invalid credentials
        schema:
          $ref: "#/definitions/Error"
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    email = data.get('email', '').strip()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    result, error = AuthService.login(email, password)
    
    if error:
        return jsonify({'error': error}), 401
    
    return jsonify({
        'message': 'Login successful',
        **result
    }), 200


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Logout the current user.
    
    UC-L: Login account (logout part)
    
    Returns:
        200: Logout successful
    """
    user_id = get_jwt_identity()
    AuthService.logout(user_id)
    
    return jsonify({'message': 'Logout successful'}), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh access token.
    
    Returns:
        200: New access token
        401: Invalid token
    """
    user_id = get_jwt_identity()
    result, error = AuthService.refresh_token(user_id)
    
    if error:
        return jsonify({'error': error}), 401
    
    return jsonify(result), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_profile():
    """
    Get current user profile.
    
    Returns:
        200: User profile
        404: User not found
    """
    user_id = get_jwt_identity()
    user = AuthService.get_user_by_id(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({'user': user.to_dict()}), 200


@auth_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_profile():
    """
    Update current user profile.
    
    Request Body:
        first_name: New first name
        last_name: New last name
    
    Returns:
        200: Profile updated
        400: Validation error
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    
    user, error = AuthService.update_profile(user_id, first_name, last_name)
    
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify({
        'message': 'Profile updated',
        'user': user.to_dict()
    }), 200


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """
    Change user's password.
    
    Request Body:
        current_password: Current password
        new_password: New password
    
    Returns:
        200: Password changed
        400: Validation error
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    current_password = data.get('current_password', '')
    new_password = data.get('new_password', '')
    
    success, error = AuthService.change_password(user_id, current_password, new_password)
    
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify({'message': 'Password changed successfully'}), 200


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """
    Request password reset OTP.
    
    UC-FP: Forgot password
    
    Request Body:
        email: User's email
    
    Returns:
        200: OTP sent (or silent fail for security)
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    email = data.get('email', '').strip()
    
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    
    token, error = AuthService.request_password_reset(email)
    
    # Send OTP via email if token was created
    if token:
        try:
            email_service = EmailService.get_instance()
            if email_service:
                email_service.send_otp_email(
                    email,
                    token.token,
                    token.expires_at
                )
        except Exception as e:
            current_app.logger.error(f"Failed to send OTP email: {e}")
    
    # Always return success to prevent email enumeration
    return jsonify({
        'message': 'If the email exists, a reset code has been sent'
    }), 200


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """
    Reset password with OTP.
    
    UC-FP: Forgot password (reset part)
    
    Request Body:
        email: User's email
        otp: The OTP code
        new_password: New password
    
    Returns:
        200: Password reset successful
        400: Invalid or expired OTP
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    email = data.get('email', '').strip()
    otp = data.get('otp', '').strip()
    new_password = data.get('new_password', '')
    
    if not email or not otp or not new_password:
        return jsonify({'error': 'Email, OTP, and new_password are required'}), 400
    
    success, error = AuthService.reset_password(email, otp, new_password)
    
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify({'message': 'Password reset successful'}), 200


@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    """
    Verify OTP without resetting password.
    
    Request Body:
        email: User's email
        otp: The OTP code
    
    Returns:
        200: OTP is valid
        400: Invalid OTP
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    email = data.get('email', '').strip()
    otp = data.get('otp', '').strip()
    
    if not email or not otp:
        return jsonify({'error': 'Email and OTP are required'}), 400
    
    user, error = AuthService.verify_reset_token(email, otp)
    
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify({'message': 'OTP is valid', 'valid': True}), 200


@auth_bp.route('/deactivate', methods=['POST'])
@jwt_required()
def deactivate_account():
    """
    Deactivate the current user's account.
    
    Returns:
        200: Account deactivated
    """
    user_id = get_jwt_identity()
    success, error = AuthService.deactivate_account(user_id)
    
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify({'message': 'Account deactivated'}), 200