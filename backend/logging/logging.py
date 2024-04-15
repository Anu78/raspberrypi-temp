import sqlite3
from pathlib import Path 


class Logger: 
  INFO = 1
  ERROR = 2
  DEBUG = 3
  CRITICAL = 4
  ALL = 5
  PARENT_DIR = Path(__file__).resolve().parent.parent

  def __init__(self): 
    self.con = sqlite3.connect(self.PARENT_DIR/"database.db")
    self.cur = self.con.cursor()

  def setup_logging(self): 
    res = self.cur.execute("select name from sqlite_master")
    names = res.fetchone()
    if "logs" in names: 
      self.post_log(self.INFO, "logs table present. not creating another", "logger")
    else:
      self.cur.execute("""
        create table logs (

        logID INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp datetime default CURRENT_TIMESTAMP,
        loglevel TEXT,
        message TEXT
        )
        """)
      self.post_log(self.INFO, "new logs table created.", "logger")
  def clear_all(self):
    self.cur.execute("delete from logs")
    pass
  def search_logs(self, order="asc", severity=ALL, message=None, component=None):
    pass
  def post_log(self, severity, message, component):
    pass


if __name__ == "__main__": 
  logger = Logger()
  logger.setup_logging()