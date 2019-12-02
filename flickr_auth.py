#!/usr/bin/env python
"""
    by oPromessa, 2018

    flickrapi login example (python 2.7 and 3.6 compatible)
"""
import sys
import os
import logging
import flickrapi

# -----------------------------------------------------------------------------
# authenticate
#
# Authenticates via flickrapi on flickr.com
#
def authenticate(my_cfg):
    """
    Authenticate user so we can upload files.
    Assumes the cached token is not available or valid.

    Receives dictionary with the configuration.
    Returns an instance object for the class flickrapi
    """

    # Instantiate nuflickr for connection to flickr via flickrapi
    nuflickr = flickrapi.FlickrAPI(my_cfg["api_key"],
                                   my_cfg["api_secret"],
                                   token_cache_location=my_cfg["TOKEN_CACHE"])
    # Authenticate
    logging.warning('Getting new token.')
    try:
        nuflickr.get_request_token(oauth_callback='oob')
    except flickrapi.exceptions.FlickrError as exc:
        logging.error('+++010 Flickrapi exception on authenticate. '
                      'Error code/msg: [%s]/[%s]', exc.code, exc)
        sys.exit(4)

    # Show url. Copy and paste it in your browser
    # Adjust parameter "perms" to to your needs
    authorize_url = nuflickr.auth_url(perms=u'read')
    print('Copy and paste following authorizaiton URL '
          'in your browser to obtain Verifier Code.')
    print(authorize_url)

    # Prompt for verifier code from the user.
    # Python 2.7 and 3.6
    # use "# noqa" to bypass flake8 error notifications
    verifier = unicode(raw_input(  # noqa
        'Verifier code (NNN-NNN-NNN): ')) \
        if sys.version_info < (3, ) \
        else input('Verifier code (NNN-NNN-NNN): ')

    print('Verifier: {!s}'.format(verifier))

    # Trade the request token for an access token
    try:
        nuflickr.get_access_token(verifier)
    except flickrapi.exceptions.FlickrError as exc:
        logging.error('+++020 Flickrapi exception on get_access_token. '
                      'Error code/msg: [%s]/[%s]', exc.code, exc)
        sys.exit(5)

    print('{!s} with {!s} permissions: {!s}'
          .format('Check Authentication',
                  'read',
                  nuflickr.token_valid(perms='read')))

    # Some debug...
    logging.info('Token Cache: [%s]', nuflickr.token_cache.token)

    return nuflickr


# -----------------------------------------------------------------------------
# get_cached_token
#
# If available, obtains the flickrapi Cached Token from local file.
# returns the flickrapi object associated with the token
#
def get_cached_token(my_cfg):
    """
    Attempts to get the flickr token from disk.

    Receives dictionary with the configuration.
    Returns an instance object for the class flickrapi
    """

    logging.warning('Obtaining Cached token')
    logging.warning('TOKEN_CACHE:[%s]', my_cfg["TOKEN_CACHE"])
    nuflickr = flickrapi.FlickrAPI(my_cfg["api_key"],
                                   my_cfg["api_secret"],
                                   token_cache_location=my_cfg["TOKEN_CACHE"])

    result = None
    try:
        # Check if token permissions are correct.
        if nuflickr.token_valid(perms='read'):
            logging.warning('Cached token obtained: [%s]',
                            nuflickr.token_cache.token)
            result = nuflickr
        else:
            logging.warning('Token Non-Existant.')
    except flickrapi.exceptions.FlickrError as exc:
        logging.error('+++030 Flickrapi exception on get_request_token. '
                      'Error code/msg: [%s]/[%s]', exc.code, exc)
        sys.exit(6)

    return result


# -----------------------------------------------------------------------------
# flickr_login
#
# Uses flickrapi to performs a login/authenticate into flickr
#
def flickr_login(my_cfg):
    """
    Uses flickrapi to performs a login/authenticate into flickr

    Receives dictionary with the configuration.
    Returns an instance object for the class flickrapi
    """

    flickr = None
    flickr = get_cached_token(my_cfg)

    if flickr is None:
        flickr = authenticate(my_cfg)

    return flickr


# -----------------------------------------------------------------------------
# is_good
#
# Checks if res.attrib['stat'] == "ok"
#
def is_good(res):
    """ isGood

        Check res is not None and res.attrib['stat'] == "ok" for XML object
    """
    if res is None:
        result = False
    elif not res == "" and res.attrib['stat'] == "ok":
        result = True
    else:
        result = False

    return result


# -----------------------------------------------------------------------------
# Global Variables + Main code
#
logging.basicConfig(stream=sys.stderr,
                    level=logging.WARNING,  # Use logging.DEBUG if required
                    format='[%(asctime)s]:[%(processName)-11s]'
                    '[%(levelname)-8s]:[%(name)s] %(message)s')

if __name__ == "__main__":
    try:
        CFG = {
            'api_key': os.environ['api_key'],
            'api_secret': os.environ['api_secret'],
            'TOKEN_CACHE': os.path.join(
                os.path.dirname(
                    sys.argv[0]),
                "token")}
    except KeyError as exc:
        logging.error(
            '+++040 Please define api_key and api_secret OS variables. '
            'Error msg: [%s]/[%s]', exc, sys.exc_info())
        sys.exit(3)

    print('Connecting to Flickr...')
    FLICKR = flickr_login(CFG)

    if FLICKR is not None:
        print(FLICKR.token_cache.token)
