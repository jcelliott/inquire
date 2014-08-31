""" create labeled dataset from task runs """
from __future__ import absolute_import, division, print_function
import json
from collections import defaultdict
# from pprint import pprint

TASK_RUN_FILE = 'trec_2002_task_run.json'
TASK_FILE = 'trec_2002_task.json'
OUT_FILE = 'trec_2002_data_out.txt'

# pylint: disable=invalid-name
tasks = {}
with open(TASK_FILE) as json_data:
    tasks_data = json.load(json_data)
    for q_obj in tasks_data:
        tasks[int(q_obj['id'])] = q_obj['info']['question']

# pprint(tasks)

count_dict = lambda: defaultdict(int)
task_runs = defaultdict(count_dict)

with open(TASK_RUN_FILE) as json_data:
    run_data = json.load(json_data)
    for run_obj in run_data:
        # this nested dict will map task ids to a map of classes to counts:
        # {1: {'LOC:country': 1, 'LOC:other': 2}, 2: ...}
        task_runs[int(run_obj['task_id'])][run_obj['info']] += 1

# pprint(dict(task_runs))
unanimous = 0
majority = 0
manual = 0

out = open(OUT_FILE, 'w')

for i in range(1, 501):
    out.flush()
    print("{}: {}".format(i, tasks[i]))
    cur_task = task_runs[i]
    question = tasks[i]
    if len(cur_task) == 1:  # unanimous
        category = cur_task.keys().pop()  # get first (and only) key
        out.write("{} {}\n".format(category, question))
        unanimous += 1
        continue

    # check for majority
    found_majority = False
    total = sum(cur_task.values())  # number of judgements for this task
    for category, count in cur_task.iteritems():
        if count / total > 0.5:
            out.write("{} {}\n".format(category, question))
            majority += 1
            found_majority = True
            break

    if found_majority is True:
        continue
    # no majority, manually annotate
    options = ['TODO']
    options.extend(cur_task.keys())
    opts_text = ", ".join('[{}]{}'.format(num, opt) for (num, opt) in enumerate(options))
    opt = raw_input(opts_text + ': ')
    out.write("{} {}\n".format(options[int(opt)], question))
    manual += 1

    # print()

out.close()

print()
print("unanimous: " + str(unanimous))
print("majority: " + str(majority))
print("manually annotate: " + str(manual))
print("total: " + str(unanimous + majority + manual))
