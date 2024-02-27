from flask import Flask, render_template, request, redirect, url_for, session
import pyotp
import qrcode
import io
import base64
import random


app = Flask(__name__)
# used for flask encrypting session data and other security-related functions
app.secret_key = 'demo_secret_key'

# Define a simple in-memory database of user credentials
# Replace this with a database in a real application
users = {'demo': {'password': 'changeme', 'mfa_secret_key': None, 'backup_codes': []}}

# Goolge Authenticator, and the underlying TOTP concept, does not have backup codes. 
# These are a different mechanism, which would have to be impemented indepedenty, alongside their TOTP implementation.
# IMO, if user need to reset MFA, we can just provide a way for the admin to reset
def generate_backup_codes(num_codes=3):
    # Generate random backup codes
    backup_codes = ['{:06d}'.format(random.randint(0, 999999)) for _ in range(num_codes)]
    return backup_codes

@app.route('/')
def index():
    print(users)
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    print(users)
    
    username = request.form['username']
    password = request.form['password']

    user = users.get(username)
    if user and user['password'] == password:
        session['authenticated'] = True
        # Authentication successful, check for MFA setup
        if user['mfa_secret_key']:
            session['username'] = username
            return redirect(url_for('verify_mfa'))
        else:
            # MFA not set up, redirect to setup page
            session['username'] = username
            return redirect(url_for('setup_mfa'))
    else:
        # Authentication failed, display error message
        return 'Invalid username or password'

@app.route('/setup-mfa', methods=['GET', 'POST'])
def setup_mfa():
    print(users) 
    if 'authenticated' not in session or not session['authenticated']:
        return redirect(url_for('index'))
    user = users.get(session['username'])
    # Check if MFA is enabled and verified for the user
    if user['mfa_secret_key']:
        return 'MFA has been already setup'
    else:
        if request.method == 'GET':
            # Generate TOTP secret and URI
            totp_secret = pyotp.random_base32()
            users[session['username']]['mfa_secret_key'] = totp_secret  # Store TOTP secret in user data

            print("TOTP Secret:", totp_secret)
            
            # Generate TOTP URI
            totp_uri = pyotp.totp.TOTP(totp_secret).provisioning_uri(name=session['username'], issuer_name='Demo MFA GG')
            
            # Generate backup codes based on TOTP secret
            backup_codes = generate_backup_codes()
            print("Generated Backup Codes:", backup_codes)  # Print generated backup codes for debugging
            users[session['username']]['backup_codes'] = backup_codes  # Store backup codes in user data

            # Generate QR code image
            img = qrcode.make(totp_uri)
            print(type(img))

            # Convert image to base64-encoded string
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            qr_code_data = base64.b64encode(buffered.getvalue()).decode()

            return render_template('setup_mfa.html', qr_code=qr_code_data, totp_secret=totp_secret)
        elif request.method == 'POST':
            # Handle POST request for MFA verification
            totp_code = request.form['totp_code']
            totp_secret = users[session['username']]['mfa_secret_key']

            if totp_secret:
                if pyotp.totp.TOTP(totp_secret).verify(totp_code):
                    # MFA verification successful, redirect to protected page
                    return redirect(url_for('protected'))
                else:
                    # Clear the totp_secret from user data if failed
                    users[session['username']]['mfa_secret_key'] = None
                    # MFA verification failed, display error message
                    return 'Invalid MFA code'
            else:
                # TOTP secret not found in user data, redirect to setup page
                return redirect(url_for('setup_mfa'))

@app.route('/verify-mfa', methods=['GET', 'POST'])
def verify_mfa():
    print(users) 
    if 'authenticated' not in session or not session['authenticated']:
        return redirect(url_for('index'))
    if request.method == 'GET':
        return render_template('verify_mfa.html')
    elif request.method == 'POST':
        # Handle POST request for MFA verification
        totp_code = request.form['totp_code']
        totp_secret = users[session['username']]['mfa_secret_key']

        if totp_secret:
            totp = pyotp.TOTP(totp_secret)
            if totp.verify(totp_code):
                # MFA verification successful, set flag in session
                session['totp_verified'] = True
                print("MFA verification successful")
                print("Session:", session)
                # Redirect to protected page
                return redirect(url_for('protected'))
            else:
                # MFA verification failed, display error message
                return redirect(url_for('invalid_token'))
        else:
            # TOTP secret not found in user data, redirect to setup page
            return redirect(url_for('setup_mfa'))
        
@app.route('/invalid-token')
def invalid_token():
    print(users) 
    return render_template('invalid_token.html')

@app.route('/protected')
def protected():
    print(users) 
    response = require_full_authentication()
    if response:
        return response
    # Check if MFA is enabled and verified for the user
    if session.get('totp_verified'):
        # MFA is enabled and verified, allow access to protected page
        return render_template('protected.html')
    else:
        # MFA is not verified, redirect to verify MFA page
        return redirect(url_for('verify_mfa'))

@app.route('/backup-codes')
def backup_codes():
    print(users) 
    response = require_full_authentication()
    if response:
        return response
    # Check if MFA is enabled and verified for the user
    if session.get('totp_verified'):
        # MFA is enabled and verified, allow access to backup page
        # Retrieve backup codes from session
        backup_codes = users[session['username']]['backup_codes']
        return render_template('backup_codes.html', backup_codes=backup_codes)
    else:
        # MFA is not verified, redirect to verify MFA page
        return redirect(url_for('verify_mfa'))

def require_full_authentication():
    if 'authenticated' not in session or not session['authenticated'] or 'totp_verified' not in session or not session['totp_verified']:
        return redirect(url_for('index')) 

@app.route('/logout', methods=['POST'])
def logout():
    print(users) 
    # Clear session data
    session.pop('authenticated', None)
    session.pop('totp_verified', None)
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
    # app.run(ssl_context=('cert.pem', 'privkey.pem'), host='0.0.0.0', port=5000, debug=True) # if you want SSL for the app
