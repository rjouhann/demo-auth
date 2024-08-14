from flask import Flask, request, jsonify, render_template_string
import logging
import json

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

# In-memory user store
users = {}
next_user_id = 1

# SCIM 2.0 endpoints

@app.route('/scim/v2/ServiceProviderConfig', methods=['GET'])
def service_provider_config():
    logging.info("Received GET /scim/v2/ServiceProviderConfig")
    response = {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:ServiceProviderConfig"],
        "documentationUri": "http://example.com/help/scim.html",
        "patch": {"supported": True},
        "bulk": {"supported": False, "maxOperations": 0, "maxPayloadSize": 0},
        "filter": {"supported": True, "maxResults": 200},
        "changePassword": {"supported": False},
        "sort": {"supported": True},
        "etag": {"supported": False},
        "authenticationSchemes": [
            {
                "name": "OAuth Bearer Token",
                "description": "Authentication scheme using the OAuth Bearer Token Standard",
                "specUri": "http://www.rfc-editor.org/info/rfc6750",
                "documentationUri": "http://example.com/help/oauth.html",
                "type": "oauthbearertoken",
                "primary": True
            }
        ]
    }
    return jsonify(response), 200

@app.route('/scim/v2/ResourceTypes', methods=['GET'])
def resource_types():
    logging.info("Received GET /scim/v2/ResourceTypes")
    response = {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:ResourceType"],
        "Resources": [
            {
                "id": "User",
                "name": "User",
                "endpoint": "/Users",
                "description": "User Account",
                "schema": "urn:ietf:params:scim:schemas:core:2.0:User",
                "schemaExtensions": []
            }
        ]
    }
    return jsonify(response), 200

@app.route('/scim/v2/Schemas', methods=['GET'])
def schemas():
    logging.info("Received GET /scim/v2/Schemas")
    response = {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:Schema"],
        "Resources": [
            {
                "id": "urn:ietf:params:scim:schemas:core:2.0:User",
                "name": "User",
                "description": "User Account",
                "attributes": [
                    {
                        "name": "userName",
                        "type": "string",
                        "multiValued": False,
                        "description": "Unique identifier for the User",
                        "required": True,
                        "caseExact": False,
                        "mutability": "readWrite",
                        "returned": "default",
                        "uniqueness": "server"
                    },
                    {
                        "name": "email",
                        "type": "string",
                        "multiValued": False,
                        "description": "Email address of the User",
                        "required": True,
                        "caseExact": False,
                        "mutability": "readWrite",
                        "returned": "default",
                        "uniqueness": "server"
                    },
                    {
                        "name": "name",
                        "type": "complex",
                        "multiValued": False,
                        "description": "The components of the user's real name.",
                        "required": False,
                        "subAttributes": [
                            {
                                "name": "givenName",
                                "type": "string",
                                "multiValued": False,
                                "description": "The given name of the User",
                                "required": False,
                                "caseExact": False,
                                "mutability": "readWrite",
                                "returned": "default"
                            },
                            {
                                "name": "familyName",
                                "type": "string",
                                "multiValued": False,
                                "description": "The family name of the User",
                                "required": False,
                                "caseExact": False,
                                "mutability": "readWrite",
                                "returned": "default"
                            }
                        ]
                    },
                    {
                        "name": "externalId",
                        "type": "string",
                        "multiValued": False,
                        "description": "External ID of the User",
                        "required": False,
                        "caseExact": False,
                        "mutability": "readWrite",
                        "returned": "default"
                    },
                    {
                        "name": "urn:custom:role",
                        "type": "string",
                        "multiValued": False,
                        "description": "Role of the User",
                        "required": False,
                        "caseExact": False,
                        "mutability": "readWrite",
                        "returned": "default",
                        "canonicalValues": ["member", "manager", "owner"]
                    },
                    {
                        "name": "urn:custom:accessLevels",
                        "type": "complex",
                        "multiValued": True,
                        "description": "Access Levels of the User",
                        "required": False,
                        "subAttributes": [
                            {
                                "name": "value",
                                "type": "string",
                                "multiValued": False,
                                "description": "Access Level ID",
                                "required": False,
                                "caseExact": False,
                                "mutability": "readWrite",
                                "returned": "default",
                                "canonicalValues": [
                                    "readonly_secret",
                                    "write_secret",
                                    "readonly_sca",
                                    "write_sca",
                                    "readonly_iac",
                                    "write_iac",
                                    "readonly_honeytoken",
                                    "write_honeytoken"
                                ]
                            }
                        ]
                    },
                    {
                        "name": "urn:custom:remoteId",
                        "type": "string",
                        "multiValued": False,
                        "description": "Remote ID of the User",
                        "required": False,
                        "caseExact": False,
                        "mutability": "readWrite",
                        "returned": "default"
                    },
                    {
                        "name": "urn:custom:idpId",
                        "type": "string",
                        "multiValued": False,
                        "description": "IDP ID of the User",
                        "required": False,
                        "caseExact": False,
                        "mutability": "readWrite",
                        "returned": "default"
                    }
                ]
            }
        ]
    }
    return jsonify(response), 200

# User management endpoints

@app.route('/scim/v2/Users', methods=['POST'])
def create_user():
    global next_user_id

    data = request.json
    logging.info(f"Received POST /scim/v2/Users with data: {data}")

    user_id = next_user_id
    next_user_id += 1

    user = {
        "id": user_id,
        "externalId": data.get('externalId', str(user_id)),
        "userName": data.get('userName', data.get('email', '')),  # Set userName to email if not specified
        "name": {
            "givenName": data.get('name', {}).get('givenName', ''),
            "familyName": data.get('name', {}).get('familyName', '')
        },
        "email": data.get('emails', [{}])[0].get('value', ''),
        "urn:custom:role": data.get('urn:custom:role', 'member'),  # Default to 'member' if not specified
        "urn:custom:remoteId": data.get('urn:custom:remoteId', ''),
        "urn:custom:accessLevels": data.get('urn:custom:accessLevels', ['readonly_secret']),  # Default to 'readonly_secret' if not specified
        "urn:custom:idpId": data.get('id', '')
    }

    users[user_id] = user

    response = {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
        "id": user_id,
        "externalId": user['externalId'],
        "userName": user['userName'],
        "name": user['name'],
        "email": user['email'],
        "urn:custom:role": user['urn:custom:role'],
        "urn:custom:remoteId": user['urn:custom:remoteId'],
        "urn:custom:accessLevels": user['urn:custom:accessLevels'],
        "urn:custom:idpId": user['urn:custom:idpId'],
        "meta": {
            "resourceType": "User"
        }
    }
    return jsonify(response), 201

@app.route('/scim/v2/Users', methods=['GET'])
def list_users():
    logging.info("Received GET /scim/v2/Users")
    
    # Get query parameters
    count = int(request.args.get('count', '10'))
    start_index = int(request.args.get('startIndex', '1'))
    
    # Calculate pagination indices
    end_index = start_index + count - 1
    
    # Convert users dict to list for slicing
    user_list = list(users.values())
    paginated_users = user_list[start_index-1:end_index]
    
    response = {
        "schemas": ["urn:ietf:params:scim:api:messages:2.0:ListResponse"],
        "totalResults": len(user_list),
        "Resources": []
    }
    
    for user in paginated_users:
        user_response = {
            "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
            "id": user['id'],
            "externalId": user['externalId'],
            "userName": user['userName'],
            "name": user['name'],
            "email": user['email'],
            "urn:custom:role": user['urn:custom:role'],
            "urn:custom:remoteId": user['urn:custom:remoteId'],
            "urn:custom:accessLevels": user['urn:custom:accessLevels'],
            "urn:custom:idpId": user['urn:custom:idpId'],
            "meta": {
                "resourceType": "User"
            }
        }
        response["Resources"].append(user_response)
    
    return jsonify(response), 200

@app.route('/scim/v2/Users/<user_id>', methods=['GET'])
def get_user(user_id):
    logging.info(f"Received GET /scim/v2/Users/{user_id}")
    user = users.get(int(user_id))
    if not user:
        return jsonify({"detail": "User not found"}), 404

    response = {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
        "id": user_id,
        "externalId": user['externalId'],
        "userName": user['userName'],
        "name": user['name'],
        "email": user['email'],
        "urn:custom:role": user['urn:custom:role'],
        "urn:custom:remoteId": user['urn:custom:remoteId'],
        "urn:custom:accessLevels": user['urn:custom:accessLevels'],
        "urn:custom:idpId": user['urn:custom:idpId'],
        "meta": {
            "resourceType": "User"
        }
    }
    return jsonify(response), 200

@app.route('/scim/v2/Users/<user_id>', methods=['PATCH'])
def update_user(user_id):
    data = request.json
    logging.info(f"Received PATCH /scim/v2/Users/{user_id} with data: {data}")
    user = users.get(int(user_id))
    if not user:
        return jsonify({"detail": "User not found"}), 404

    for op in data.get('Operations', []):
        if op['op'] == 'replace':
            value = op['value']
            if isinstance(value, str):
                value = json.loads(value)
            for key, val in value.items():
                if key == 'name':
                    user['name']['givenName'] = val.get('givenName', user['name']['givenName'])
                    user['name']['familyName'] = val.get('familyName', user['name']['familyName'])
                elif key == 'email':
                    user['email'] = val
                elif key == 'userName':
                    user['userName'] = val
                else:
                    user[f"urn:custom:{key}"] = val

    users[int(user_id)] = user

    response = {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
        "id": user_id,
        "externalId": user['externalId'],
        "userName": user['userName'],
        "name": user['name'],
        "email": user['email'],
        "urn:custom:role": user['urn:custom:role'],
        "urn:custom:remoteId": user['urn:custom:remoteId'],
        "urn:custom:accessLevels": user['urn:custom:accessLevels'],
        "urn:custom:idpId": user['urn:custom:idpId'],
        "meta": {
            "resourceType": "User"
        }
    }
    return jsonify(response), 200

@app.route('/scim/v2/Users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    logging.info(f"Received DELETE /scim/v2/Users/{user_id}")
    if int(user_id) in users:
        del users[int(user_id)]
        return '', 204
    else:
        return jsonify({"detail": "User not found"}), 404

# HTML endpoint to display users
@app.route('/')
def display_users():
    users_list = list(users.values())
    
    html_template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Users</title>
        <style>
            table {
                border-collapse: collapse;
                width: 100%;
            }
            th, td {
                border: 1px solid black;
                padding: 8px;
                text-align: left;
            }
            th {
                background-color: #f2f2f2;
            }
            .blue {
                color: blue;
            }
        </style>
    </head>
    <body>
        <h1>Demo SCIM Endpoints</h1>
        <ul>
            <li><a href="/scim/v2/ServiceProviderConfig">/scim/v2/ServiceProviderConfig</a></li>
            <li><a href="/scim/v2/ResourceTypes">/scim/v2/ResourceTypes</a></li>
            <li><a href="/scim/v2/Schemas">/scim/v2/Schemas</a></li>
            <li><a href="/scim/v2/Users">/scim/v2/Users</a></li>
        </ul>
        <h1>Users</h1>
        <table border="1">
            <tr>
                <th class="blue">ID</th>
                <th>User Name</th>
                <th class="blue">Given Name</th>
                <th class="blue">Family Name</th>
                <th class="blue">Email</th>
                <th>Role</th>
                <th>Remote ID</th>
                <th>Access Levels</th>
                <th class="blue">IDP ID</th>
            </tr>
            {% for user in users %}
            <tr>
                <td>{{ user.id }}</td>
                <td>{{ user.userName }}</td>
                <td>{{ user.name.givenName }}</td>
                <td>{{ user.name.familyName }}</td>
                <td>{{ user.email }}</td>
                <td>{{ user['urn:custom:role'] }}</td>
                <td>{{ user['urn:custom:remoteId'] }}</td>
                <td>{{ user['urn:custom:accessLevels'] | join(', ') }}</td>
                <td>{{ user['urn:custom:idpId'] }}</td>
            </tr>
            {% endfor %}
        </table>
    </body>
    </html>
    '''

    return render_template_string(html_template, users=users_list)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8081)
