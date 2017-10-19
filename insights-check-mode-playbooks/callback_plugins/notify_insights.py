# -*- coding: utf-8 -*-
# adapted from the Foreman plugin
# (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    callback: notify_insights
    type: notification
    short_description: Sends events to Insights
    description:
      - This callback will task events to Insights
    requirements:
'''

from datetime import datetime
from collections import defaultdict
import json
import time

from ansible import constants as C
from ansible.playbook.task_include import TaskInclude
from ansible.plugins.callback import CallbackBase
from ansible.utils.color import stringc

class CallbackModule(CallbackBase):
    """
    """

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'notify_insights'

    # Ara doesn't define this at all
    CALLBACK_NEEDS_WHITELIST = False

    TIME_FORMAT = "%Y-%m-%d %H:%M:%S %f"

    def __init__(self):
        super(CallbackModule, self).__init__()
        self.items = defaultdict(list)
        self.insights_system_ids = defaultdict(list)
        self.start_time = int(time.time())

    def _build_log(self, data):
        logs = []
        for event_name, task_title, result in data:
            r = result.copy()
            if "ansible_facts" in r:
                del r["ansible_facts"]
            
            r["_insights_event_name"] = event_name
            r["_insights_task_title"] = task_title

            logs.append(r)
        return logs

    def send_report(self,report):
        if False:
            # Can't actually send this to Insight's yet, because no API yet
            if "insights_system_id" in report:
                filename = "report_%s_ID_%s.txt" % (report["host"], report["insights_system_id"])
            else:
                filename = "report_%s.txt" % report["host"]

            with open(filename, 'w') as the_file:
                the_file.write(json.dumps(report))
                self._display.display("Insights report written to %s" % filename)
        else:
            # Instead we print out a short summary of "changed", "ok", "fatal" and Title
            #   skip "skipping"
            if not self.banner_printed:
                self._display.banner("CHECKMODE SUMMARY")
                self.banner_printed = True

            if "insights_system_id" in report:
                self._display.display("%s SYSTEM ID %s" % (report["host"], report["insights_system_id"]))
            else:
                self._display.display("%s" % (report["host"]))
            
            for each in report["task_results"]:
                if each["_insights_event_name"] != "skipped":
                    self._display.display(self._format_summary_for(each))
                    #print(json.dumps(each, indent=2))

    def _format_summary_for(self, task_result):
        if task_result["_insights_event_name"] == "ok":
            icon = stringc("ok", C.COLOR_OK) 
        elif task_result["_insights_event_name"] == "changed":
            icon = stringc("no", C.COLOR_ERROR)
        elif task_result["_insights_event_name"] == "fatal":
            icon = stringc("ERROR", C.COLOR_ERROR)
        else:
            icon = stringc(task_result["_insights_event_name"], C.COLOR_DEBUG)

        return "    %s : %s"  % (icon, task_result["_insights_task_title"])
    
    def send_reports(self, stats):
        """
        """
        status = defaultdict(lambda: 0)
        metrics = {}

        self.banner_printed = False
        for host in stats.processed.keys():
            sum = stats.summarize(host)
            status["applied"] = sum['changed']
            status["failed"] = sum['failures'] + sum['unreachable']
            status["skipped"] = sum['skipped']
            log = self._build_log(self.items[host])
            metrics["time"] = {"total": int(time.time()) - self.start_time}
            now = datetime.now().strftime(self.TIME_FORMAT)
            report = {
                "host": host,
                "reported_at": now,
                "metrics": metrics,
                "status": status,
                "task_results": log,
            }
            if host in self.insights_system_ids:
                report["insights_system_id"] = self.insights_system_ids[host]
            self.send_report(report)
            self.items[host] = []

    def append_result(self, result, event_name):
        task_name = result._task.get_name()
        host_name = result._host.get_name()
        if "ansible_facts" in result._result:
            if "ansible_local" in result._result["ansible_facts"]:
                if "insights" in result._result["ansible_facts"]["ansible_local"]:
                    if "system_id" in result._result["ansible_facts"]["ansible_local"]["insights"]:
                        self.insights_system_ids[host_name] = result._result["ansible_facts"]["ansible_local"]["insights"]["system_id"]
        self.items[host_name].append((event_name, task_name, result._result))


    # Ansible Callback API
    #
    #
    #

    def v2_runner_on_failed(self, result, ignore_errors=False):
        self.append_result(result, "failed")

    def v2_runner_on_ok(self, result):
        # This follows the logic of this function in the 'default.py' callback
        # but all we need to determine is "changed" vs "ok"

        if isinstance(result._task, TaskInclude):
            # probably don't have to tread TaskInclude tasks special for this plugin
            return
        elif result._result.get('changed', False):
            self.append_result(result, "changed")
        else:
            self.append_result(result, "ok")

    def v2_runner_on_skipped(self, result):
        self.append_result(result, "skipped")

    def v2_runner_on_unreachable(self, result):
        self.append_result(result, "unreachable")

    def v2_playbook_on_stats(self, stats):
        self.send_reports(stats)
