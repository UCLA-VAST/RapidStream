import argparse
import json
import psutil
import os
import signal
import time

GB_SIZE = (1024 * 1024 * 1024)


class GracefulKiller:
  """
  allow us to do extra stuff after being killed
  """
  kill_now = False
  def __init__(self):
    signal.signal(signal.SIGINT, self.exit_gracefully)
    signal.signal(signal.SIGTERM, self.exit_gracefully)

  def exit_gracefully(self, *args):
    self.kill_now = True


def utilization_tracking(report_dir, report_prefix, transfer_target=""):
  period = 20
  cpu_core_num = psutil.cpu_count()

  time_to_cpu = {}
  time_to_mem = {}

  cpu_temp = open(f"{report_dir}/{report_prefix}_cpu_usage_temp.txt", "w")
  mem_temp = open(f"{report_dir}/{report_prefix}_mem_usage_temp.txt", "w")


  killer = GracefulKiller()
  while not killer.kill_now:
    timestamp = round(time.time())

    # how many cores are being used
    cpu = round(psutil.cpu_percent(interval=0.5) / 100 * cpu_core_num, 3)
    mem_gb = round(psutil.virtual_memory().used / GB_SIZE, 3)
    
    time_to_mem[timestamp] = mem_gb
    time_to_cpu[timestamp] = cpu

    cpu_temp.write(f"{timestamp}: {cpu}\n")
    mem_temp.write(f"{timestamp}: {mem_gb}\n")
    cpu_temp.flush()
    mem_temp.flush()

    time.sleep(period)

  # when the program gets killed
  open(f"{report_dir}/{report_prefix}_cpu_usage.json", "w").write(json.dumps(time_to_cpu, indent=2))
  open(f"{report_dir}/{report_prefix}_mem_usage.json", "w").write(json.dumps(time_to_mem, indent=2))

  if transfer_target:
    os.system(f"scp {report_dir}/{report_prefix}_cpu_usage.json {transfer_target}")
    os.system(f"scp {report_dir}/{report_prefix}_mem_usage.json {transfer_target}")


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Record the system utilization until killed')
  parser.add_argument("--output_dir", type=str, nargs="?", default=".")
  parser.add_argument("--report_prefix", type=str, nargs="?", default="")
  parser.add_argument("--transfer_target", type=str, nargs="?", default="")
  args = parser.parse_args()

  utilization_tracking(
    args.output_dir, 
    args.report_prefix,
    args.transfer_target
  )