# coding: utf-8
from __future__ import unicode_literals

import re

from .common import InfoExtractor
from ..utils import (
    ExtractorError,
    int_or_none,
    parse_iso8601,
    urlencode_postdata,
    str_or_none,
    strip_or_none,
    try_get,
)

from youtube_dl.compat import (
    compat_HTTPError,
)

class UnigeIE(InfoExtractor):
    _VALID_URL = r'https://mediaserver.unige.ch/play/(?P<id>\d+)'
    _TESTS = [{
        'url': 'https://mediaserver.unige.ch/play/196613',
        'md5': 'xxxx',
        'info_dict': {
            'id': '196613',
            'display_id': '196613',
            'ext': 'mp4',
        },
    }, {
        'url': 'https://mediaserver.unige.ch/proxy/196613/VN3-2569-2023-2024-09-19.mp4',
        'only_matching': True,
    }]

#    def _real_initialize(self):
#        self._api_key = self._download_json(
#            'https://www.vidio.com/auth', None, data=b'')['api_key']


    def _login(self, video_id):
        # Login credentials are per video group

        username, password = self._get_login_info(netrc_machine=f'unige-mediaserver-{video_id}')
        if not username or not password:
            self.raise_login_required('You need a username/pwd to access this video')

        try:
            secure_wp = f'https://mediaserver.unige.ch/proxy/{video_id}/secure.php?view=play&id={video_id}'
            data = self._download_webpage(secure_wp, None, 'Logging in',
                data=urlencode_postdata({
                    'httpd_username': username,
                    'httpd_password': password,
                }), headers={
                    'Referer': secure_wp,
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                })
        except ExtractorError as e:
            if isinstance(e.cause, compat_HTTPError) and e.cause.code == 400:
                raise ExtractorError(
                    'Unable to login: incorrect username and/or password',
                    expected=True)
            raise

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)

        try:
            # This dumb download only checks if we need to login, as authentication
            # is unique (and sometimes optional) for each video
            secure_wp = f'https://mediaserver.unige.ch/proxy/{video_id}/secure.php?view=play&id={video_id}'
            data = self._download_webpage(secure_wp, f'secure_{video_id}')
        except ExtractorError as e:
            if isinstance(e.cause, compat_HTTPError) and e.cause.code == 401:
                self._login(video_id)
            else:
                # The video doesn't require login
                pass

        # TODO more code goes here, for example ...
        #title = self._html_search_regex(r'<title>(.+?)</title>', webpage, 'title')
        #title = title.split('-')[0].strip()

        video_url = self._search_regex(
            r'<source src="([^"]+)"', webpage, 'video URL')



        #title = self._html_search_regex(r'<title>(.+?)</title>', webpage, 'title', default=None).split('-')[0]


        return {
            'id': video_id,
            'title': f'My video {video_id}', #title,
            'url': video_url,
            'title': '', #title,
            # TODO more properties (see youtube_dl/extractor/common.py)
        }



class UnigePlaylistIE(InfoExtractor):
    _VALID_URL = r'https://mediaserver.unige.ch/collection/(?P<id>[-\w+]+)'

    def _real_extract(self, url):
        collection_id = self._match_id(url)

        rss = self._download_xml(url + '.rss', collection_id)

        entries = [self.url_result(video.text, 'Unige')
                   for video in rss.findall('./channel/item/link')]
        title_text = rss.find('./channel/title').text

        return self.playlist_result(entries, collection_id, title_text)
