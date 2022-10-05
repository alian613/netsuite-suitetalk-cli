# Preparation

- NetSuite ([Getting Started with OAuth 2.0](https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_157771281570.html))
    1. [Enabled the OAuth 2.0 Feature](https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_157771482304.html)
    2. [Set Up OAuth 2.0 Roles](https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_157771510070.html)
    3. [Assign Users to OAuth 2.0 Roles](https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_157771650112.html)
    4. [New  integration](https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_157771733782.html)
    5. [New Access Token](https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/bridgehead_4254081947.html) (requires permissions of role)
    6. Reference Implement Client Credntials (Machine to Machine) Section, and upload certificated to OAuth 2.0 Client Credentials Setup
- Python
  1. install python 3 above
  2. run init.bat to install library, if you haven't installed these libraries
  3. run and read main.py --help
- Postman
    1. download [NetSuite oauth Token.postman_collection.json](NetSuite%20oauth%20Token.postman_collection.json) and import to posman, or reference **Postman using OAuth2.0 Client Credentials** section
    2. send \> Get JSRSASIGN Crypto Library
    3. send \> Get Access Token
    4. send \> Get Customer List or Query SuiteQL

---

# Implement Client Credntials (Machine to Machine)

- Must be in x.509 format with a file extension of .cer, .pen, or .crt.
- The length of the RSA key must be 3072 or 4096 bits. The length of the EC key must be 256, 384, or 512 bits
- Maximun time period of two year, if the certificate is valid for a longer time period, the system automatically shortens the time period to two years
- Uploads the public part of the certificate to OAuth 2.0 Client Credentials Setup
- The private part of the certificate provides the signature of the JWT token

## Create Certificate

> When Git is installed, it also incloudes openssl, which you can use,
Windows default path:  `C:\Program Files\Git\usr\bin`

```
openssl req -x509 -newkey rsa:4096 -sha256 -keyout auth-key.pem -out auth-cert.pem -nodes -days 730
```

- -newkey: this option creates a new certificate request and a new private key.
- -keyout:  this gives the filename to write the newly created private key to
- -out: output certificate
- -nodes: private key is created it will not be encrypted

# Python POC

> command line --help

```shell
  Options:
    -alg [PS256|PS284|PS512|RS256|RS384|RS512]
                                    the algorithm used for signing of the token,
                                    supports PS256, PS284, PS512, RS256, RS384,
                                    or RS512. default is PS256
    -kid TEXT                       the Certificate ID generated during OAuth
                                    2.0 Client Credential Setup of NetSuite
                                    [required]
    -iss TEXT                       the client ID for the NetSuite Integration
                                    [required]
    -i TEXT                         is your NetSuite account ID  [required]
    -pk TEXT...                     the private part of the certificate: b "
                                    -----BEGIN PRIVATE KEY-----\n..........-----
                                    END PRIVATE KEY-----" the path to the
                                    private part of the certificate: p
                                    "C:\certificat\private-key.pem"  [required]
    -p TEXT                         the passphrase of the certificate
    -cli                            enter interactive command line interface
    --copy                          copy access token to clipboard
    --get TEXT                      send a GET request to this url,it can be
                                    multiple
    --post TEXT                     send a POST request to this url,it can be
                                    multiple
    --put TEXT                      send a PUT request to this url,it can be
                                    multiple
    --delete TEXT                   send a DELETE request to this url,it can be
                                    multiple
    --help                          Show this message and exit.
```

> cli(interactive command line interface) mode help

```
    cd: Change URL/path
    mode: Change CompanyURL for RESTlet or RESTWebService
    get: HTTP method set to GET request
    post: HTTP method set to POST request
    put: HTTP method set to PUT request
    delete: HTTP method set to DELETE request
    send: send request, support http method then grep
    ps: preview request
    help: List cli mode commands, actions
    exit: exit suite prompt
```

## Interactive Command Example

- RESTWebService get customer list：
    ```{{company_url}}/services/rest/record/v1/customer```

    ``` shell
        > python main.py -i ${account_id} -iss ${client_id} -kid ${certificate_id} -pk p "${private_key}" --get ${company_url}/services/rest/record/v1/customer
    ```

- RESTlet :

    ``` shell
        > python main.py -i ${account_id} -iss ${client_id} -kid ${certificate_id} -pk p "${private_key}" -cli

        >>>mode restlet
        >>>cd app/site/hosting/restlet.nl?script=<script_id>&deploy=1
        >>>get|send
    ```

# Postman using OAuth2.0 Client Credentials

Reference REST WebServices

- [NetSuite REST API](https://system.netsuite.com/help/helpcenter/en_US/APIs/REST_API_Browser/record/v1/2022.1/index.html)
- [OAuth 2.0 for REST Web Services](https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_157780312610.html)
- Help Center：[The REST API Browser](https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_157373386674.html)

## Postman Lab

Step.

1. enabled oauth feature
2. new  integration (oauth redirect uri : <https://oauth.pstmn.io/v1/browser-callback>)
3. new access token (requires permissions of role)
4. optional authorization code grant
5. optional client credentials (M2M)
6. download file https://\<accountID\>.app.netsuite.com/app/external/integration/integrationDownloadPage.nl or download [NetSuite oauth Token.postman_collection.json](NetSuite%20oauth%20Token.postman_collection.json)
7. import environment
8. edit environment variable
9. import collections
