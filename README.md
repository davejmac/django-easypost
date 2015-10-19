# django-easypost

A django wrapper for the python easypost library

## Usage

The package requires an easypost api key. Easypost supplies both a live key and a test key which can be added to the
site's `settings.py` like the following which distinguishes between environments:

```
#############
# EASYPOST  #
#############
if PRODUCTION:
    EASYPOST_API_KEY = 'uiop4567890'
else:
    EASYPOST_API_KEY = 'qwerty12345'
```

## Testing

`python runtests.py `


## Development

```
# to get easypost on the python sys path (should be in a virtualenv for this project)
pip install -e .

# For model migrations
django-admin makemigrations easypost --settings=easypost.test_settings
```
