from drivers import Thermocouple
import time


def post_to_csv(filename, time, meas1, meas2):
    with open(filename, 'a') as f:
        f.write(f"{time}, {meas1}, {meas2}\n")

def main():
  csv_file = 'temp_data.csv'
  start_time = time.time()
  # write csv heading
  with open(csv_file, 'w') as f:
    f.write('time, left_temp, right_temp\n')

  tcLeft = Thermocouple("left plate",chipSelect=7, clock=11, data=9)
  tcRight = Thermocouple("right plate",chipSelect=8, clock=11, data=9)
  try: 
      while True:
        temp1 = tcLeft.get()
        temp2 = tcRight.get()
        post_to_csv(round(time.time() - start_time, 2), temp1, temp2)

        time.sleep(1)
  except KeyboardInterrupt:
    print("shutting down safely")
    tcLeft.cleanup()
    tcRight.cleanup()


if __name__ == "__main__":
  main()