from flask import Flask, request, render_template, redirect, url_for, session

app = Flask(__name__)

# used for flask encrypting session data and other security-related functions
app.secret_key = 'demo_secret_key'

# Define a simple in-memory database of user credentials
# Replace this with a database in a real application
users = {'demo': {'password': 'changeme'}}

@app.route('/')
def home():
    print(users)
    # Check if user is authenticated
    if not session.get('authenticated'):
        # Redirect to login page if not authenticated
        return redirect(url_for('login'))
    return redirect(url_for('secure_page'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    print(users)
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Authenticate user
        if username in users and users[username]['password'] == password:
            session['authenticated'] = True
            return redirect(url_for('secure_page'))
        else:
            return 'Invalid username or password', 401
    return render_template('login.html')  # Render your login page template here

@app.route('/logout', methods=['POST'])
def logout():
    print(users)
    # Clear session data
    session.pop('authenticated', None)
    session.clear()
    return redirect(url_for('login'))  # Redirect to the login page

@app.route('/secure')
def secure_page():
    print(users)
    # This endpoint now requires user authentication before proceeding
    if not session.get('authenticated'):
        return redirect(url_for('login'))
    
    client_verify = request.headers.get('X-Client-Verified', 'None')
    if client_verify == 'SUCCESS':
        # Extracting certificate details from headers
        subject_dn = request.headers.get('X-Subject-DN', 'Not provided')
        
        # Use render_template to render the HTML response with variables
        return render_template('success.html', subject_dn=subject_dn, client_verify=client_verify)
    else:
        return 'Secure Page - Client SSL authentication failed.', 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
