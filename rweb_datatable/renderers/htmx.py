from copy import copy
from typing import Union, Callable, Optional

from rweb_datatable.html import Node
from rweb_datatable.models import Column, Table, Dataset, TableContext, Pagination
from rweb_datatable.utils import url, make_table_section_id


def render_table_section(
    data: Dataset, table: Table, context: TableContext, pagination: Optional[Pagination] = None
) -> Node:
    section = Node("section", attributes={"id": make_table_section_id(table)})
    section += make_actions(data=data, table=table, context=context)
    table_data = Node("div", attributes={"id": f"table-data-{table.id}"})
    table_data += make_table(data=data, table=table, context=context)
    if pagination:
        table_data += make_pagination(context=context, pagination=pagination)
    section += table_data
    return section


def make_actions(data: Dataset, table: Table, context: TableContext) -> Node:
    """
    Table section that includes filters, download button, column selector eventually
    """
    div = Node("div", attributes={"class": "d-flex justify-content-between align-items-center mb-3"})
    download_url = url(context.path, download="csv", **context.args)
    div.node("div", Node("a", "Download", attributes={"href": download_url, "class": "btn btn-primary "}))
    form = div.node(
        "form",
        attributes={
            "method": "GET",
            "class": "input-group",
            "style": "max-width: 15rem",
            "hx-get": url(context.path, args=context.args, exclude=["search"]),
            "hx-target": context.hx_target,
            "hx-select": context.hx_target,
            "hx-trigger": "keyup delay:500ms from:#search",
            **context.search_box_attributes,
        },
    )
    form.node(
        "input",
        attributes={
            "id": "search",
            "type": "search",
            "name": "search",
            "class": "form-control",
            "aria-label": "Search",
            "placeholder": "Search...",
            "value": context.search or "",
            "hx-preserve": "true",
        },
    )

    form.node(
        "button",
        """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-search" viewBox="0 0 16 16">
  <path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0z"/>
</svg>""",
        attributes={"class": "input-group-text btn btn-primary", "type": "submit"},
    )
    return div


def make_table(data: Dataset, table: Table, context: TableContext) -> Node:
    t = Node("table", attributes={"id": f"table-{table.id}", "class": "table table-striped table-hover table-sm"})
    t += make_thead(table=table, data=data, context=context)
    t += make_tbody(table=table, data=data, context=context)
    return t


def make_thead(table: Table, data: Dataset, context: TableContext) -> Node:
    thead = Node("thead", attributes={"class": "table-dark"})
    tr = thead.node("tr")
    for col_id, col in table.columns.items():
        th_factory = col.render_header or make_th
        tr += th_factory(table=table, data=data, context=context, column=col)
    return thead


def make_th(table: Table, data: Dataset, context: TableContext, column: Column) -> Node:
    th = Node("th", attributes={"scope": "col", **column.render_header_config.get("attributes", {})})
    args = copy(context.args)
    target = th
    sort_symbol = ""
    if column.is_sortable:
        current_dir = context.sort[column.id].sort_dir if column.id in context.sort else None
        if current_dir == "asc":
            sort_dir = "desc"
            sort_symbol = "&uarr;"
        elif current_dir == "desc":
            sort_dir = None
            sort_symbol = "&darr;"
        else:
            sort_dir = "asc"

        if sort_dir:
            sort_args = dict(sort_dir1=sort_dir, sort_by1=column.id)
        else:
            sort_args = {}

        if "sort_dir1" in args:
            del args["sort_dir1"]
        if "sort_by1" in args:
            del args["sort_by1"]

        sort_url = url(path=context.path, args=args, search=context.search, **sort_args)
        a = Node(
            "a",
            attributes={
                "href": sort_url,
                "data-hx-get": sort_url,
                "data-hx-target": context.hx_target,
                "data-hx-select": context.hx_target,
            },
        )
        th += a
        target = a
    target += column.title.format(**context.args, **context.extra_args)
    target += " "
    target += Node("span", sort_symbol,)
    return th


def make_tbody(table: Table, data: Dataset, context: TableContext) -> Node:
    tbody = Node("tbody")
    if data.rows:
        for row in data.rows:
            tr = tbody.node("tr")
            for col_id, col in table.columns.items():
                value = row.get(col_id)
                rendered_value = render_cell(context=context, row=row, value=value, renderer=col.render_body)
                tr.node("td", rendered_value, attributes=col.render_body_config.get("attributes"))
    else:
        tr = tbody.node("tr")
        tr.node("td", "There is no data to display", attributes={"colspan": len(table.columns)})
    return tbody


def render_cell(context: TableContext, row, value: str, renderer: Union[None, str, Callable]):
    if not renderer:
        renderer = str
    try:
        try:
            return renderer(value=value, row=row)
        except Exception:
            return renderer(value)
    except Exception as e:
        raise ValueError(f"Could not render table cell context={context}, value={value}, renderer={renderer}") from e


def make_pagination(context: TableContext, pagination: Pagination):
    target = context.hx_target

    p = Node("nav", attributes={"aria-label": "Paginate Table"})
    ul = p.node("ul", attributes={"class": "pagination"})

    ul += make_pagination_li(
        text="First", pagination_url=pagination.first_url, target=target, aria_label="Goto First Page"
    )
    ul += make_pagination_li(
        text="Prev", pagination_url=pagination.prev_url, target=target, aria_label="Goto Previous Page"
    )

    for page_link in pagination.page_links:
        ul += make_pagination_li(
            text=str(page_link.page_number),
            pagination_url=page_link.url,
            target=target,
            aria_label=f"Goto Page {page_link.page_number}",
            is_current=page_link.is_current,
        )

    ul += make_pagination_li(
        text="Next", pagination_url=pagination.next_url, target=target, aria_label="Goto Next Page"
    )
    ul += make_pagination_li(
        text="Last", pagination_url=pagination.last_url, target=target, aria_label="Goto Last Page"
    )

    current_position = Node(
        "span",
        f"Showing {pagination.first_row} - {pagination.last_row} of {pagination.total_rows} entries",
        attributes={"class": "pagination-page"},
    )
    div = Node("div", current_position, p, attributes={"class": "d-flex justify-content-between align-items-center"})

    return div


def make_pagination_li(
    text: str, pagination_url: str, target: str, aria_label: str, is_current: bool = False, is_disabled: bool = False
) -> Node:
    li_attributes = {"class": "page-item"}
    a_attributes = {"class": "page-link"}
    if is_current:
        li_attributes["class"] += " active"
        a_attributes["aria-current"] = "page"
    if is_disabled or pagination_url is None:
        li_attributes["class"] += " disabled"
        a_attributes["tabindex"] = -1
        a_attributes["aria-disabled"] = True
    else:
        a_attributes.update(
            {
                "href": pagination_url,
                "data-hx-get": pagination_url,
                "data-hx-target": target,
                "data-hx-select": target,
                "aria-label": aria_label,
            }
        )
    li = Node("li", attributes=li_attributes)
    li += Node("a", text, attributes=a_attributes,)
    return li
