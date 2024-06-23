# Obscura

Hide information until a later time.

```sh
# Install deps
pipenv shell
pipenv install

# Run tests
pipenv run tests

# Start app
ENV='development' DATABASE_URL='obscura.sqlite3' API_TOKEN='very-secret' python3 main.py
```

```sh
# Protect link to your Google form.
# NOTE: x-api-token has to match $API_TOKEN provided when the app was started.
# NOTE: "kind=gform-embed" currently doesn't do anything.
curl -X POST 'http://127.0.0.1:8000/submit?kind=gform-embed&payload=https%3A%2F%2Fforms.google.com' -H 'x-api-token: very-secret' 
# Returns a JSON list of strings, for example:
#   [ "VRcHWEZRVBZJUhddWF5QAh" ]

# Fetch the protected link using one of the returned strings:
curl 'https://127.0.0.1:8000/VRcHWEZRVBZJUhddWF5QAh'
# Returns the protected payload, for example:
#   https://forms.google.com
```
