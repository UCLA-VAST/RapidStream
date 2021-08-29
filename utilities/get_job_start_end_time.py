import argparse
import calendar
import json
import os
import re
from collections import defaultdict
from datetime import datetime
from typing import List, Any, Dict

VIVADO_STEPS = [
  "slot_synth",
  "init_slot_placement",
  "opt_placement_iter0",
  "slot_routing"
]
ILP_PLACEMENT_STEP = "ILP_anchor_placement_iter0"
LOG_START_TIME_MARKER = "Start of session at"
LOG_END_TIME_MARKER = "Exiting Vivado at"
VIVADO_LOG = "vivado.log"
ILP_PLACEMENT_LOG = "ILP-placement.log"


def get_all_vivado_log_in_directory(directory: str, log_name: str) -> List[str]:
  log_list = []
  for root, dirs, files in os.walk(directory):
    for file in files:
      if file.endswith(log_name):
        log_list.append(root.replace(f"{directory}/", ""))
  
  return log_list


def get_vivado_log_start_end_time(log_path: str) -> Dict[str, List[Any]]:
  """
  get the start unix time
  """
  timestamps = defaultdict(list)
  month_abbr_to_num = {month: index for index, month in enumerate(calendar.month_abbr) if month}

  for line in open(log_path, "r").readlines():
    if LOG_START_TIME_MARKER in line or LOG_END_TIME_MARKER in line:
      match = re.search(r'[ ]+([A-Za-z]+)[ ]+(\d{1,2})[ ]+(\d{2}):(\d{2}):(\d{2})[ ]+(\d{4})', line)
      month = month_abbr_to_num[match.group(1)]
      day = int(match.group(2))
      hour = int(match.group(3))
      minute = int(match.group(4))
      second = int(match.group(5))
      year = int(match.group(6))
      timestamps['unix_time'].append(datetime(year, month, day, hour, minute, second).timestamp()) 
      timestamps['date'].append(match.group(0)) 

  assert len(timestamps['unix_time']) == 2, timestamps
  return timestamps


def get_ilp_placement_log_start_end_time(log_path: str) -> Dict[str, List[Any]]:
  """
  get the start unix time
  """
  timestamps = defaultdict(list)

  for line in open(log_path, "r").readlines():
    if LOG_START_TIME_MARKER in line or LOG_END_TIME_MARKER in line:
      match = re.search(r'\d+', line)
      timestamps['unix_time'].append(match.group(0)) 

  assert len(timestamps['unix_time']) == 2, timestamps
  return timestamps


def get_worker_start_end_time(base_dir: str):
  """
  for each step, for each worker, record the start/end time
  """
  worker_start_end_time = defaultdict(dict)
  for step in VIVADO_STEPS:
    job_list = get_all_vivado_log_in_directory(f"{base_dir}/{step}", VIVADO_LOG)
    for job in job_list:
      log_path = f'{base_dir}/{step}/{job}/{VIVADO_LOG}'
      worker_start_end_time[step][job] = get_vivado_log_start_end_time(log_path)

  # ilp placement jobs
  job_list = get_all_vivado_log_in_directory(f"{base_dir}/{ILP_PLACEMENT_STEP}", ILP_PLACEMENT_LOG)
  for job in job_list:
    log_path = f'{base_dir}/{ILP_PLACEMENT_STEP}/{job}/{ILP_PLACEMENT_LOG}'
    worker_start_end_time[ILP_PLACEMENT_STEP][job] = get_ilp_placement_log_start_end_time(log_path)

  return worker_start_end_time


def save_results(output_path: str, worker_start_end_time) -> None:
  open(output_path, "w").write(json.dumps(worker_start_end_time, indent=2))


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Extract the start/end time of RW-Bridge jobs')
  parser.add_argument("--base_dir", type=str, required=True)
  parser.add_argument("--output_path", type=str, nargs="?", default="./job_start_end_time.json")
  args = parser.parse_args()

  worker_start_end_time = get_worker_start_end_time(args.base_dir)

  save_results(args.output_path, worker_start_end_time)