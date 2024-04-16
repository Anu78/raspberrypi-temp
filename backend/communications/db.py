import sqlite3
from pathlib import Path
from logging import Logger
"""
needs to store: logs, sensor values, # of motor steps, ip addr on startup, and a way to store temporary measurements for x-minute durations (time-series data) 
"""

class Database:
  PARENT_DIR = Path(__file__).resolve().parent.parent
  PARAMS_LIST = ["snake_highscore", "motor_compress_steps", "target_temperature"]
  logger = Logger()

  def __init__(self):
    self.con = sqlite3.connect(self.PARENT_DIR/"database.sqlite")
    self.cur = self.con.cursor()
    self.verify_tables()

  def verify_tables(self):
    # check if params table exists
    res = self.cur.execute("select name from sqlite_master where name='params'")
    params_exists = res.fetchone()

    if "params" not in params_exists:
      self.logger.post_log(self.logger.INFO, "new key/value table created", "database")
      self.cur.execute("create table params (key text primary key, value text)")
      self.con.commit()
      self.cur.execute("insert into params (key, value) values ('snake_highscore','0'), ('motor_compress_steps', '0'), ('target_temperature', '0')")
      self.con.commit()
  def get_parameters(self):
    res = self.cur.execute("select * from params")
    return {key:float(value) for key, value in res.fetchall()}
  def update_parameter(self, param, value):
    try:
      self.cur.execute(f"update params set value = '{value}' where key = '{param}'")
      self.con.commit()
    except Exception:
      return False 
    finally:
      return True
  def put_sensor_value(self, sensor, value):
    pass
  def read_sensor_value(self, sensor):
    pass


if __name__ == "__main__":
  db = Database()
  params = db.get_parameters()
  print(params)