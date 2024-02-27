from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def index():
    client_verify = request.headers.get('X-Client-Verified', 'None')
    print(f"Authentication succeed. X-Client-Verified: {client_verify}")
    if client_verify == 'SUCCESS':
        # Extracting certificate details from headers
        subject_dn = request.headers.get('X-Subject-DN', 'Not provided')
        validity_end = request.headers.get('X-SSL-Cert-End', 'Not provided')
        
        # Constructing the HTML response
        html_response = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="utf-8">
            <title>SSL Client Authentication Demo</title>
        </head>
        <body>
        <h2>Client SSL authentication succeeded.</h2>
        <p>Your client certificate details:</p>
        <ul>
            <li>Subject Identifier: <b>{subject_dn}</b></li>
            <li>Verification Result: <b>{client_verify}</b></li>
        </ul>
        </body>
        </html>
        """
        return html_response, 200
    else:
        print(f"Authentication failed. X-Client-Verified: {client_verify}")
        return '<h2>Client SSL authentication failed.</h2><p>Please ensure you have a valid client certificate.</p>', 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)