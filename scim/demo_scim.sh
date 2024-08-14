#!/bin/bash

# Function to show usage
usage() {
    echo "Usage: $0 [create|get|list|update|delete] [options] [users]"
    echo ""
    echo "Commands:"
    echo "  create - Create a new user"
    echo "  get    - Retrieve a specific user by ID"
    echo "  list   - List all users"
    echo "  update - Update a specific user by ID"
    echo "  delete - Delete a specific user by ID"
    echo ""
    echo "Options:"
    echo "  --host HOST             Hostname or IP address (default: 127.0.0.1:8081)"
    echo "  --user-id USER_ID       User ID (required for get, update, delete user)"
    echo "  --remote-id ID          Remote ID (optional for create user)"
    echo "  --user-name USERNAME    Username (required for create user)"
    echo "  --given-name NAME       Given name (required for create user)"
    echo "  --family-name NAME      Family name (required for create user)"
    echo "  --email EMAIL           Email (required for create user)"
    echo "  --role ROLE             Role (required for create, update user)"
    echo "  --access-levels LEVELS  Access levels (comma separated, required for create, update user)"
    echo "  --new-given-name NAME   New given name (required for update user)"
    echo ""
    echo "Examples:"
    echo "  $0 create user --remote-id 1234567890 --given-name John --family-name Doe --email johndoe@example.com --role member --access-levels readonly_secret,readonly_sca"
    echo "  $0 get user --user-id 1"
    echo "  $0 list users"
    echo "  $0 update user --user-id 1 --new-given-name Johnny"
    echo "  $0 delete user --user-id 1"
}

# Default values
host="127.0.0.1:8081"
user_id=""
remote_id=""
given_name=""
family_name=""
email=""
role=""
access_levels=""
new_given_name=""

# Parse arguments
command=$1
entity=$2
shift 2

while [ "$1" != "" ]; do
    case $1 in
        --host )              shift
                              host=$1
                              ;;
        --user-id )           shift
                              user_id=$1
                              ;;
        --remote-id )         shift
                              remote_id=$1
                              ;;
        --given-name )        shift
                              given_name=$1
                              ;;
        --family-name )       shift
                              family_name=$1
                              ;;
        --email )             shift
                              email=$1
                              ;;
        --role )              shift
                              role=$1
                              ;;
        --access-levels )     shift
                              access_levels=$1
                              ;;
        --new-given-name )    shift
                              new_given_name=$1
                              ;;
        * )                   usage
                              exit 1
    esac
    shift
done

# Validate required options
case $command in
    create )
        if [ "$entity" == "user" ]; then
            if [ -z "$remote_id" ] || [ -z "$given_name" ] || [ -z "$family_name" ] || [ -z "$email" ] || [ -z "$role" ] || [ -z "$access_levels" ]; then
                usage
                exit 1
            fi
        else
            usage
            exit 1
        fi
        ;;
    get | update | delete )
        if [ "$entity" == "user" ]; then
            if [ -z "$user_id" ]; then
                usage
                exit 1
            fi
        else
            usage
            exit 1
        fi
        ;;
    update )
        if [ "$entity" == "user" ]; then
            if [ -z "$new_given_name" ]; then
                usage
                exit 1
            fi
        else
            usage
            exit 1
        fi
        ;;
esac

# Perform the requested command
case $command in
    create )
        if [ "$entity" == "user" ]; then
            json_payload="{
                \"schemas\": [\"urn:ietf:params:scim:schemas:core:2.0:User\"],
                \"name\": {
                    \"givenName\": \"$given_name\",
                    \"familyName\": \"$family_name\"
                },
                \"email\": \"$email\",
                \"urn:custom:role\": \"$role\",
                \"urn:custom:remoteId\": \"$remote_id\",
                \"urn:custom:accessLevels\": [\"$(echo "$access_levels" | sed 's/,/","/g')\"]
            }"
            echo "JSON Payload:"
            echo "$json_payload"
            echo "Curl:"
            curl -X POST http://$host/scim/v2/Users \
                -H "Content-Type: application/json" \
                -d "$json_payload"
        fi
        ;;
    get )
        if [ "$entity" == "user" ]; then
            curl -X GET http://$host/scim/v2/Users/$user_id
        fi
        ;;
    list )
        if [ "$entity" == "users" ]; then
            curl -X GET http://$host/scim/v2/Users
        fi
        ;;
    update )
        if [ "$entity" == "user" ]; then
            curl -X PATCH http://$host/scim/v2/Users/$user_id \
                -H "Content-Type: application/json" \
                -d "{
                    \"schemas\": [\"urn:ietf:params:scim:api:messages:2.0:PatchOp\"],
                    \"Operations\": [{
                        \"op\": \"replace\",
                        \"value\": {
                            \"name\": {
                                \"givenName\": \"$new_given_name\"
                            }
                        }
                    }]
                }"
        fi
        ;;
    delete )
        if [ "$entity" == "user" ]; then
            curl -X DELETE http://$host/scim/v2/Users/$user_id
        fi
        ;;
    * )
        usage
        exit 1
esac
