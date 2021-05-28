from typing import List
from urllib.parse import urlencode

from rweb_datatable import Table


def url(path: str, args: dict = None, exclude: List = None, **params) -> str:
    """
    Create a URL to update the table

    :param path: the path of the page endpoint
    :param args: a dict of base args to include in the query string
    :param exclude: a list of keys to exclude from the final url query string
    :param params: additional k-v pairs to include in the query string
    :return: a url string
    """
    exclude = exclude if exclude else []
    out = dict(args) if args else {}
    out.update(params)

    # eliminate keys from the query string which are None to avoid for example ?search=None from being sent
    # eliminate keys in the exclude list
    filtered = {}
    for k, v in out.items():
        if v is None or v is "" or k in exclude:
            continue
        filtered[k] = v

    qs = urlencode(filtered)
    return f"{path}?{qs}"


def make_table_section_id(table: Table) -> str:
    return f"{table.id}-section"
