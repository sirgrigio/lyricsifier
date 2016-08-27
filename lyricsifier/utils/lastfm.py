import logging
import json
import urllib.parse
import urllib.request

log = logging.getLogger(__name__)


def get_tag(api_key, artist, title):
    base_url = "http://ws.audioscrobbler.com/2.0/"
    params = {'method': 'track.gettoptags',
              'artist': artist,
              'track': title,
              'api_key': api_key,
              'format': 'json'}
    log.info('executing request to last.fm with params {}'.format(params))
    data = urllib.parse.urlencode(params)
    full_url = base_url + '?' + data
    log.info('requesting URL {}'.format(full_url))
    request = urllib.request.Request(full_url)
    response = urllib.request.urlopen(request)
    json_data = json.loads(response.read().decode('utf8'))
    log.debug('response {}'.format(json_data))
    error = json_data.get('error', None)
    if error:
        log.error(json_data['message'])
        return None
    return json_data['toptags']['tag'][0]['name']
