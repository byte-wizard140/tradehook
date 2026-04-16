import sqlite3, time

class SQLiteReader:
    def __init__(self, cfg):
        self.path = cfg["db_path"]
        self.schema = cfg.get("schema", {})
        self.interval = cfg.get("poll_interval", 60)
        self._last_id = self._max_id()

    def _conn(self):
        # read-only, never locks TradeMAV
        return sqlite3.connect(f"file:{self.path}?mode=ro", uri=True,
                               check_same_thread=False)

    def _max_id(self):
        try:
            table = self.schema.get("table", "notifications")
            col_id = self.schema.get("col_id", "id")
            row = self._conn().execute(f"SELECT MAX({col_id}) FROM {table}").fetchone()
            return row[0] or 0
        except Exception as e:
            print(f"[SQLiteReader] Init warning: {e}")
            return 0

    def poll(self):
        table   = self.schema.get("table",        "notifications")
        col_id  = self.schema.get("col_id",       "id")
        col_t   = self.schema.get("col_ticker",   "ticker")
        col_dir = self.schema.get("col_direction", "direction")
        col_str = self.schema.get("col_strength",  "strength")
        col_aln = self.schema.get("col_aligned",   "signals_aligned")
        col_ts  = self.schema.get("col_timestamp", "updated_at")

        while True:
            try:
                con = self._conn()
                rows = con.execute(
                    f"SELECT {col_id},{col_t},{col_dir},{col_str},{col_aln},{col_ts} "
                    f"FROM {table} WHERE {col_id} > ? ORDER BY {col_id} ASC",
                    (self._last_id,)
                ).fetchall()
                for row in rows:
                    self._last_id = row[0]
                    yield {
                        "ticker": row[1], "direction": row[2],
                        "strength": row[3], "signals_aligned": row[4],
                        "timestamp": row[5]
                    }
            except Exception as e:
                print(f"[SQLiteReader] Error: {e}")
            time.sleep(self.interval)
