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


### Protecting an embedded Google form

```sh
curl -X POST 'http://127.0.0.1:8000/submit?variant=gform-embed&payload=https%3A%2F%2Fforms.google.com' -H 'x-api-token: very-secret'
# Returns a JSON list of references, for example:
#   [
#     {
#       "ref": "UEVTVERQVUtQHUJ",
#       "usable_after": "2024-06-23T09:06:36.357157+00:00",
#       "usable_duration_seconds": 86400
#     },
#     {
#       "ref": "UkRWVURTU0RSWA9",
#       "usable_after": "2024-06-24T09:06:36.357157+00:00",
#       "usable_duration_seconds": 86400
#     },
#   ]
```
- NOTE: x-api-token has to match `$API_TOKEN` provided when the app was started. 
- NOTE: "kind=gform-embed" indicates an embedded Google form. Currently this is the onl 


### Fetch the protected link using one of the references:

```sh
curl 'https://127.0.0.1:8000/UEVTVERQVUtQHUJ'
# Returns the protected payload. Since we specified kind=gform-embed, the result will be a
# HTML page that has the form embedded.
```
