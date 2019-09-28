from fastapi import Security, HTTPException
from fastapi.security.api_key import APIKeyQuery, APIKeyCookie, APIKeyHeader

from starlette.status import HTTP_403_FORBIDDEN

from .settings import Settings


api_key_query = APIKeyQuery(name=Settings.API_KEY_NAME, auto_error=False)
api_key_header = APIKeyHeader(name=Settings.API_KEY_NAME, auto_error=False)
api_key_cookie = APIKeyCookie(name=Settings.API_KEY_NAME, auto_error=False)


async def get_api_key(
        api_key_query: str = Security(api_key_query),
        api_key_header: str = Security(api_key_header),
        api_key_cookie: str = Security(api_key_cookie),
):
    if api_key_query == Settings.API_KEY:
        return api_key_query
    elif api_key_header == Settings.API_KEY:
        return api_key_header
    elif api_key_cookie == Settings.API_KEY:
        return api_key_cookie
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="无法认证API KEY"
        )
