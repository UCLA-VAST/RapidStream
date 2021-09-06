import argparse
import csv
import json
from collections import OrderedDict
from typing import List, Dict, Tuple, Any


CPU_AVERAGE_PERIOD = 100

def get_cpu_at_sample_time(sample_time, list_of_timestamp_and_cpu):
  cpu_sum = 0
  for list_of_t_and_cpu in list_of_timestamp_and_cpu:
    sample_val_list = []
    for t, cpu in list_of_t_and_cpu:
      if sample_time - CPU_AVERAGE_PERIOD <= t <= sample_time + CPU_AVERAGE_PERIOD:
        sample_val_list.append(cpu)
    cpu_sum += sum(sample_val_list) / len(sample_val_list)

  cpu_sum = round(cpu_sum, 2)
  return cpu_sum

def get_sample_timestamps(list_of_timestamp_and_cpu: List[List[Tuple[int, float]]], sample_period):
  start_time = list_of_timestamp_and_cpu[0][0][0]
  end_time = list_of_timestamp_and_cpu[0][-1][0]
  return list(range(start_time, end_time, sample_period))

def merge_tracking_log(
    sample_timestamps: List[int], 
    list_of_timestamp_and_cpu: List[List[Tuple[int, float]]]
) -> List[Tuple[int, float]]:
  merged_timestamp_to_val = []
  for sample_time in sample_timestamps:
    cpu_sum = get_cpu_at_sample_time(sample_time, list_of_timestamp_and_cpu)
    merged_timestamp_to_val.append([sample_time, cpu_sum])

  return merged_timestamp_to_val

def count_active_jobs(sample_timestamps: List[int], job_start_end_time_list: List[Tuple[int, int]]) -> List[int]:
  active_job_tracking = []
  for sample_time in sample_timestamps:
    cnt = 0
    for start, end in job_start_end_time_list:
      if int(start) <= sample_time <= int(end):
        cnt += 1
    active_job_tracking.append(cnt)

  return active_job_tracking

def count_all_active_jobs_csv(
    sample_timestamps: List[int], 
    type_to_job_start_end_time_list: Dict[str, List[Tuple[int, int]]]
) -> List[List[Any]]:
  all_active_jobs = [[t] for t in sample_timestamps]
  for job_type, worker_to_prop in type_to_job_start_end_time_list.items():
    job_start_end_time_list = [prop["unix_time"] for prop in worker_to_prop.values()]
    active_job_tracking = count_active_jobs(sample_timestamps, job_start_end_time_list)
    assert len(active_job_tracking) == len(all_active_jobs)

    for i in range(len(all_active_jobs)):
      all_active_jobs[i].append(active_job_tracking[i])

  all_active_jobs.insert(0, ['time'] + list(type_to_job_start_end_time_list.keys()))

  file = open('active_job_count.txt', 'w')
  wr = csv.writer(file)
  wr.writerows(all_active_jobs)

def get_sampling_from_all_servers(sample_item):
  list_of_timestamp_and_val_list = []
  dir = '/expr/cnn/13x14_3FF_double_reg/system_utilization_tracking'
  for server in ("u5", "u16", "u17", "u18"):
    cpu_usage = json.JSONDecoder(object_pairs_hook=OrderedDict).decode(open(f'{dir}/{server}_{sample_item}_usage.json').read())
    t_and_cpu_list = [(int(t), cpu) for t, cpu in cpu_usage.items()]
    list_of_timestamp_and_val_list.append(t_and_cpu_list)
  
  return list_of_timestamp_and_val_list

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument("--sample_item", type=str, required=True)
  parser.add_argument("--sample_period", type=int, required=True)
  args = parser.parse_args()

  sample_item = args.sample_item
  sample_period = args.sample_period

  list_of_timestamp_and_val_list = get_sampling_from_all_servers(sample_item)

  sample_timestamps = get_sample_timestamps(list_of_timestamp_and_val_list, sample_period)

  merged_timestamp_to_val = merge_tracking_log(sample_timestamps, list_of_timestamp_and_val_list)
  file = open(f'merged_t_to_{sample_item}.txt', 'w')
  wr = csv.writer(file)
  wr.writerows(merged_timestamp_to_val)

  type_to_job_start_end_time_list = json.loads(open('job_start_end_time.json', 'r').read())
  count_all_active_jobs_csv(sample_timestamps, type_to_job_start_end_time_list)