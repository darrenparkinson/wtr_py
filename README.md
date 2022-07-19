# WTR<sup>2</sup> - Python Edition

This is a python version of the original Go version of [wtr<sup>2</sup>](https://github.com/darrenparkinson/wtr).

It is essentially a small utility for retrieving and subsequently refreshing an integration token from Webex.  Primarily useful for when you just want to get a token to test with.

See the Webex documentation for further information on [Webex Integrations and Authorization](https://developer.webex.com/docs/integrations)

This was purely done as a learning exercise and still has some more work to be done. You are free to download binaries for the Go version from the [release page there](https://github.com/darrenparkinson/wtr/releases).

## Quick Start

Set Up Webex if you want to use your own integration, or use the one provided (client id / secret available on request).

* Head over to [Create a New App on developer.webex.com](https://developer.webex.com/my-apps/new) and select "Integration"
* Provide a name and description
* Enter "http://localhost:6855/token" in the "Redirect URI(s) field".
* Select "spark:all" at least and any other scopes you need based on what you're doing
* Click "Add Integration"
* Copy the client ID and secret to a `.env` file.

Run the code:

```sh
$ git clone github.com/darrenparkinson/wtr_py
$ cd wtr_py
$ python3 -m venv venv
$ . ./venv/bin/activate
$ pip install -r requirements.txt
$ uvicorn wtr:app --reload --port 6855
```

Add a `.env` file which should look like the following:

```
WEBEX_CLIENT_ID=""
WEBEX_CLIENT_SECRET=""
WEBEX_REDIRECT_URI="http://localhost:6855/token"
WEBEX_SCOPES="spark:kms spark:all"
```

Add other desired scopes to the `WEBEX_SCOPES` variable and to the integration configuration.

# TODO

* [ ] Add Refresh capability
* [ ] Add extra functions for updating users
