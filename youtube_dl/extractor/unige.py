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
        'url': 'http://www.vidio.com/watch/165683-dj_ambred-booyah-live-2015',
        'md5': 'cd2801394afc164e9775db6a140b91fe',
        'info_dict': {
            'id': '165683',
            'display_id': 'dj_ambred-booyah-live-2015',
            'ext': 'mp4',
            'title': 'DJ_AMBRED - Booyah (Live 2015)',
            'description': 'md5:27dc15f819b6a78a626490881adbadf8',
            'thumbnail': r're:^https?://.*\.jpg$',
            'duration': 149,
            'like_count': int,
            'uploader': 'TWELVE Pic',
            'timestamp': 1444902800,
            'upload_date': '20151015',
            'uploader_id': 'twelvepictures',
            'channel': 'Cover Music Video',
            'channel_id': '280236',
            'view_count': int,
            'dislike_count': int,
            'comment_count': int,
            'tags': 'count:4',
        },
    }, {
        'url': 'https://www.vidio.com/watch/77949-south-korea-test-fires-missile-that-can-strike-all-of-the-north',
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
            self._login(video_id)

        # TODO more code goes here, for example ...
        #title = self._html_search_regex(r'<title>(.+?)</title>', webpage, 'title')
        #title = title.split('-')[0].strip()

        video_url = self._search_regex(
            r'<source src="([^"]+)"', webpage, 'video URL')

        return {
            'id': video_id,
            'title': f'My video {video_id}', #title,
            'url': video_url,
            # TODO more properties (see youtube_dl/extractor/common.py)
        }
