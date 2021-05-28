import csv
from io import StringIO

from rweb_datatable import Dataset, Table, TableContext


def render_csv(data: Dataset, table: Table, context: TableContext) -> str:
    out = StringIO()
    writer = csv.writer(out)
    columns = [col.title for col in table.columns.values()]
    ids = [col.id for col in table.columns.values()]
    writer.writerow(columns)
    for row in data.rows:
        writer.writerow([row[id] for id in ids])
    return out.getvalue()