from dataclasses import dataclass, field
from typing import Union, Callable, Any, Optional, Dict, List

StringOrCallable = Union[None, str, Callable[..., str]]


@dataclass
class Column:
    id: str
    title: str
    is_sortable: bool = field(default=True)
    render_header: StringOrCallable = field(default=None)
    render_body: StringOrCallable = field(default=None)
    render_footer: StringOrCallable = field(default=None)
    render_header_config: Any = field(default_factory=dict)
    render_body_config: Any = field(default_factory=dict)
    render_footer_config: Any = field(default_factory=dict)


@dataclass
class Table:
    """
    Definition of a table
    """

    id: str
    caption: Optional[StringOrCallable] = field(default=None)
    columns: Dict[str, Column] = field(default_factory=dict)
    table_attributes: Dict[str, str] = field(default_factory=dict)
    thead_attributes: Dict[str, str] = field(default_factory=dict)
    tbody_attributes: Dict[str, str] = field(default_factory=dict)


@dataclass
class PaginationPage:
    page_number: int
    url: str
    is_current: bool


@dataclass
class Pagination:
    """
    Describe the pagination structure which will be passed to the pagination renderer
    """

    first_url: Optional[str]
    prev_url: Optional[str]
    next_url: Optional[str]
    last_url: Optional[str]
    # list of the page numbers and links to show in the central section of the pagination
    page_links: List[PaginationPage]
    # start row being shown (i.e. Showing X to Y of Z ... this is X)
    first_row: int
    # slice end row being shown (i.e. Showing X to Y of Z ... this is Y)
    last_row: int
    # (i.e. Showing X to Y of Z ... this is Z)
    total_rows: int
    total_pages: int


@dataclass
class Dataset:
    rows: List[dict]
    total_rows: int


@dataclass
class SortColumn:
    sort_by: str
    sort_dir: str
    sort_order: int = field(default=1)


@dataclass
class TableContext:
    # the CSS selector that acts as the htmlx target for all table nav links
    # such as pagination, sorting, filtering etc...
    hx_target: str
    page: int = field(default=1)
    per_page: int = field(default=20)
    sort: Dict[str, SortColumn] = field(default_factory=list)
    # the url path to the page?
    path: str = field(default="")
    args: dict = field(default_factory=dict)
    is_download: bool = field(default=False)
    search: Optional[str] = field(default=None)
    search_box_attributes: dict = field(default_factory=dict)
    # additional args used for formatting
    extra_args: dict = field(default_factory=dict)

