import aiohttp

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4090.0 ' \
             'Safari/537.36 Edg/83.0.467.0 '


class AppSession:
    _session = None

    @classmethod
    def session(cls):
        if not cls._session:
            conn = aiohttp.TCPConnector(limit=5, use_dns_cache=False)
            headers = {
                'User-Agent': USER_AGENT}
            cls._session = aiohttp.ClientSession(
                connector=conn, headers=headers)
        return cls._session

    @classmethod
    def close(cls):
        if cls._session:
            cls._session.close()

    def __del__(self):
        self.close()
