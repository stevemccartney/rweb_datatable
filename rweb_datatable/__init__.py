import math
from typing import Dict, Optional

from rweb_datatable.html import Node
from rweb_datatable.models import Table, TableContext, SortColumn, Dataset, Column, Pagination, PaginationPage
from rweb_datatable.utils import url, make_table_section_id


def get_table_context_from_args(table: Table, args: dict, extra_args: Optional[dict]=None) -> TableContext:
    """
    Create a TableContext object from a set of incoming arguments

    :param table: the table definition
    :param args: the incoming arguments, typically from a request object
    :return: a TableContext object
    """
    page_number = get_page_number(args=args)
    per_page = get_per_page(args=args)
    sort = get_sort_columns(args=args, table=table)
    hx_target = f"#{make_table_section_id(table)}"
    is_download = args.get("download", False)
    search = args.get("search", None)
    return TableContext(
        page=page_number,
        per_page=per_page,
        sort=sort,
        hx_target=hx_target,
        args=dict(args),
        is_download=is_download,
        search=search,
        extra_args=extra_args if extra_args else {}
    )


def get_page_number(args: dict) -> int:
    try:
        page = int(args.get("page", 1))
        if page < 1:
            page = 1
    except ValueError:
        page = 1
    return page


def get_per_page(args: dict) -> int:
    try:
        per_page = int(args.get("per_page", 20))
        if per_page < 10:
            per_page = 10
        if per_page > 200:
            per_page = 200
    except ValueError:
        per_page = 20
    return per_page


def get_sort_columns(table: Table, args: dict) -> Dict[str, SortColumn]:
    """
    Given a dict of args (typically from a request.args object)
    Extract the sort_by1+sort_dir1, sort_by2+sort_dir2 values until a pair of values is missing of invalid
    sort_byX must be a key/ID of a column in table.columns (case sensitive)
    sort_dirX must be one of asc, desc, none
    """
    i = 1
    sorted_cols = set()
    sort = {}
    while True:
        try:
            sort_by = args.get(f"sort_by{i}")
            sort_dir = args.get(f"sort_dir{i}").lower()

            if (
                sort_by not in table.columns.keys()
                or sort_dir not in ("asc", "desc", "none")
                or sort_by in sorted_cols
            ):
                break
            # clicking on a column heading multiple times sorts that column by asc->desc->none->asc etc...
            if sort_dir == "none":
                break
            sorted_cols.add(sort_by)
            sort[sort_by] = SortColumn(sort_by=sort_by, sort_dir=sort_dir, sort_order=i)
        except Exception:
            break
        i += 1
    return sort


def make_pagination_data(table: Table, data: Dataset, context: TableContext) -> Pagination:
    """
    Make a data structure that describes all the data needed to render both the "position" and the "pagination"
    sections of a table:
    """
    max_page = math.ceil(data.total_rows / context.per_page)
    base_params = dict(per_page=context.per_page)
    if context.search:
        base_params["search"] = context.search

    if context.sort:
        sort_cols = list(context.sort.values())
        base_params.update(dict(sort_by1=sort_cols[0].sort_by, sort_dir1=sort_cols[0].sort_dir))
    if context.page > 1:
        first_url = url(context.path, page=1, **base_params)
        prev_url = url(context.path, page=context.page - 1, **base_params)
    else:
        first_url = prev_url = None

    pages = get_pagination_pages(current_page=context.page, max_page=max_page, delta=2)
    page_links = [
        PaginationPage(
            page_number=page, url=url(context.path, page=page, **base_params), is_current=page == context.page,
        )
        for page in pages
    ]

    if context.page < max_page:
        next_url = url(context.path, page=context.page + 1, **base_params)
        last_url = url(context.path, page=max_page, **base_params)
    else:
        next_url = last_url = None

    first_row = 1 + ((context.page - 1) * context.per_page)
    last_row = first_row + len(data.rows) - 1

    return Pagination(
        first_url=first_url,
        prev_url=prev_url,
        next_url=next_url,
        last_url=last_url,
        page_links=page_links,
        first_row=first_row,
        last_row=last_row,
        total_rows=data.total_rows,
        total_pages=max_page,
    )


def get_pagination_pages(current_page: int, max_page: int, delta: int = 2):
    left = max(current_page - delta, 1)
    right = min(current_page + delta, max_page)
    return range(left, right + 1)
