# -*- coding: utf-8 -*-

import json
from enum import Enum
from typing import List
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import aiohttp

from ...utils import USER_AGENT, AppSession


class ParseProp(Enum):
    text = 'text'                   # 提供wiki文本中的被解析文本
    images = 'images'               # 在被解析的wiki文本中提供图片
    revid = 'revid'                 # 添加被解析页面的修订ID
    displaytitle = 'displaytitle'   # 为被解析的wiki文本添加标题
    wikitext = 'wikitext'           # 提供被解析的原始wiki文本


class QueryProp(Enum):
    imageinfo = "imageinfo"         # 返回文件信息和上传历史
    revisions = 'revisions'         # 获取修订版本信息


class MediaWikiEndpoint:
    def __init__(self, domain: str):
        self.domain = domain
        self.default_config = {'format': 'json', 'formatversion': 2}
        self.headers = {'User-Agent': USER_AGENT}

    def parse(self,  *props: ParseProp,  page: str = None,  pageid: int = None,  oldid: int = None) -> dict:
        """解析内容并返回解析器输出

        See https://fgo.wiki/api.php?action=help&modules=parse
        or https://www.mediawiki.org/wiki/API:Parsing_wikitext

        :params page: 解析此页的内容.
        :params props: 要获取的信息束, 默认为空，全部获取.
        :returns: json
        """

        params = self._parse_params(
            *props, page=page, pageid=pageid, oldid=oldid)
        return self.request_json(params)

    def query(self, *props: QueryProp, titles: List[str] = None, pageids: List[int] = None, revids: List[int] = None) -> dict:
        """取得来自并有关MediaWiki的数据

        See https://fgo.wiki/api.php?action=help&modules=query
        or https://www.mediawiki.org/wiki/API:Query

        :params titles: 要工作的标题列表，最大数量50.
        :params pageids: 要工作的页面ID列表，最大数量50.
        :params revids: 要工作的修订ID列表，最大数量50.
        :returns: json
        """

        params = self._query_params(
            *props, titles=titles, pageids=pageids, revids=revids)
        return self.request_json(params)

    async def async_parse(self,  *props: ParseProp, page: str = None, pageid: int = None, oldid: int = None) -> dict:
        """解析内容并返回解析器输出

        See https://fgo.wiki/api.php?action=help&modules=parse
        or https://www.mediawiki.org/wiki/API:Parsing_wikitext#parse

        :params page: 解析此页的内容.
        :params props: 要获取的信息束, 默认为空，全部获取.
        :returns: json
        """

        params = self._parse_params(
            *props, page=page, pageid=pageid, oldid=oldid)
        return await self.async_request_json(params)

    async def async_query(self, *props: QueryProp, titles: List[str] = None, pageids: List[int] = None, revids: List[int] = None) -> dict:
        """取得来自并有关MediaWiki的数据

        See https://fgo.wiki/api.php?action=help&modules=query
        or https://www.mediawiki.org/wiki/API:Query

        :params titles: 要工作的标题列表，最大数量50.
        :params pageids: 要工作的页面ID列表，最大数量50.
        :params revids: 要工作的修订ID列表，最大数量50.
        :returns: json
        """

        params = self._query_params(
            *props, titles=titles, pageids=pageids, revids=revids)
        return await self.async_request_json(params)

    def _parse_params(self,  *props: ParseProp, page: str = None, pageid: int = None, oldid: int = None) -> dict:
        params = self.default_config
        if oldid:
            params['oldid'] = oldid
        elif pageid:
            params['pageid'] = pageid
        elif page:
            params['page'] = page
        else:
            raise Exception(
                'At least one parameter is required in `page`, `pageid` and `oldid`')
        if props:
            params['prop'] = '|'.join(map(lambda p: p.value, props))
        params['action'] = 'parse'
        return params

    def _query_params(self, *props: QueryProp, titles: List[str] = None, pageids: List[int] = None, revids: List[int] = None) -> dict:
        params = self.default_config
        if revids:
            params['revids'] = revids
        elif pageids:
            params['pageids'] = pageids
        elif titles:
            params['titles'] = titles
        else:
            raise Exception(
                'At least one parameter is required in `titles`, `pageids` and `revids`')
        if props:
            params['prop'] = '|'.join(map(lambda p: p.value, props))
        params['action'] = 'query'
        return params

    def request_json(self, params: dict) -> dict:
        url = self.domain + '?' + urlencode(params)
        req = Request(url, headers=self.headers)
        resp = urlopen(req, timeout=10)
        r = resp.read().decode('utf8')
        j = json.loads(r)
        return j

    async def async_request_json(self, params: dict, session: aiohttp.ClientSession = None) -> dict:
        if not session:
            session = AppSession.session()
        async with session.get(self.domain, params=params) as resp:
            j = await resp.json()
            return j


__all__ = ['MediaWikiEndpoint', 'ParseProp', 'QueryProp']
