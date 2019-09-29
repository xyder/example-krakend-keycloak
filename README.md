# Example of KrakenD and Keycloak Integration

## Description

This weekend project was created to test out and offer a guide for the following requirements:

- python REST API service proxied through a KrakenD gateway
- Keycloak-based JWT validation
- Response filtering, merging, grouping and stubbing

### Implementation details

- the python service, by default runs on `localhost:8400` and krakend is configured to work with that. Inside the krakend container it's referred to through `host.docker.internal` to have access to the host port. Normally you'd want this on a virtual network and access it by container name, or ELB domain name, etc
- the services generates some random data for a generic `/parent/[parent_id]` endpoint, `/sibling/[parent_id]` (stand-in for an auxiliary API that augments the `parent`) and `/children/[child_id]` (stand-in for a sub-resource of `parent`). There's also a `/parent/<parent_id>/children` endpoint that serves only the children of the specified parent
- two endpoints are exposed via krakend (host `localhost:8402`):
  - `/mock/parents/<parent_id>` - composite API that serves the normal response of the `parent` endpoint for that id, merged with the equivalent `sibling` response and relative `children` response
  - `/mock/bogus-new-api/<some-bogus-path>` - stubbed response, using the 'always' strategy

## Installation

### Tooling

Tooling versions used in this example (others might work, but were not tested):

- Python 3.7.3
- Docker 19.03.2
- Docker Compose 1.24.1
- KrakenD 0.9
- Keycloak 7.0.0
- Postman 7.8.0

### Deployment

1. Clone the repo and change to the repo directory
2. Deploy docker containers with `docker-compose up -d`
3. Python service:

```bash
# install and load virtualenv
python3.7 -m pip install virtualenv
python3.7 -m virtualenv venv
source ./venv/bin/activate

# install requirements
pip install -r server/requirements.txt

# run service
python server/main.py
```

### Configure minimal required settings for Keycloak JWT validation

Notes:

- Using [https://www.jerney.io/secure-apis-kong-keycloak-1/](https://www.jerney.io/secure-apis-kong-keycloak-1/) as reference
- login using admin/admin

Steps:

1. Client creation
    - client id: `krakend-api-gateway`
    - protocol: `openid-connect`
    - root url: `http://localhost:8402`
2. Client configuration (after creation)
    - access type: `confidential`
    - go to Credentials and copy the Secret
3. User creation:
    - username: `test-app`
    - email verified: `checked`
4. User configuration (after creation)
    - go to Credentials:
        - password: `password`
        - temporary: `unchecked`
5. Get OAuth2 token using Postman:
    - Note: using info from [http://localhost:8403/auth/realms/master/.well-known/openid-configuration](http://localhost:8403/auth/realms/master/.well-known/openid-configuration)
    - select Auth Type to Oauth 2.0 and fill in the following:
        - token name: `keycloak-token`
        - grant type: `Authorization code`
        - callback url: `http://localhost:8402/mock/whatever`
        - auth url: `http://localhost:8403/auth/realms/master/protocol/openid-connect/auth`
        - access token url: `http://localhost:8403/auth/realms/master/protocol/openid-connect/token`
        - client id: `krakend-api-gateway`
        - client secret: (get from Clients/Krakend-api-gateway/Credentials)
        - scope: `openid`
        - state: `12345`
        - client authentication: `send client credentials in body`
    - request token
    - login with test-app/password on the popup login page
    - use token to request localhost:8402/mock/* endpoints

## Disclaimer

Code in this repository is provided as-is. I offer no guarantees and take no responsibility for any damage or injury one might sustain from trying this code out. This repository will probably not receive updates.
