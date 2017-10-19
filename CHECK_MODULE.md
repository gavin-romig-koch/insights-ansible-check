
Using Ansible's --check mode to check if a system is in a given state rather than to ensure
that it is in a given state by first checking and changing if not.

Say that you want to run a spot check that some set of your systems are in fips mode. Ansible
has a fact named 'ansible_fips' which will tell you, true/false, is the system in fips mode.
OK great, almost done, scribble down a playbook that checks 'ansible_fips' and prints out a
message.

---
- hosts: all
  tasks:

  - debug: msg="{{ ansible_host }} is NOT in fips mode"
    when: not ansible_fips

  - debug: msg="{{ ansible_host }}  is in fips mode"
    when: ansible_fips

You run this against the systems in question and ansible-playbook will print out:


PLAY [all] **********************************************************************************************

TASK [Gathering Facts] **********************************************************************************
ok: [gavin-rhel6-fips]
ok: [gavin-rhel66-epel1]

TASK [debug] ********************************************************************************************
skipping: [gavin-rhel66-epel1]
ok: [gavin-rhel6-fips] => {
    "msg": "gavin-rhel6-fips is NOT in fips mode"
}

TASK [debug] ********************************************************************************************
skipping: [gavin-rhel6-fips]
ok: [gavin-rhel66-epel1] => {
    "msg": "gavin-rhel66-epel1  is in fips mode"
}

PLAY RECAP **********************************************************************************************
gavin-rhel6-fips           : ok=2    changed=0    unreachable=0    failed=0
gavin-rhel66-epel1         : ok=2    changed=0    unreachable=0    failed=0

Assuming you ran it against two systems, gavin-rhel6-fips that is NOT fips enabled and gavin-rhel66-epel1 that is not fips enabled.

Now all you need are some scripts (sed, awk, grep, bash, python, your favorite tool) that filter out
the clutter and get you down to something like:

  gavin-rhel6-fips is NOT in fips mode
  gavin-rhel66-epel1  is in fips mode

This repo is about what if we use the power of Ansible to avoid having to write "some scripts".

But before we go there, let's look at another hypothetical.

Say that you want to run a spot check that some set of your systems do not have the prelink package
installed.  Ansible has blah, blah, blah... OK great, almost done, scribble down a playbook:

---
- hosts: all
  user: root
  tasks:

  - package:
      name: prelink
      state: absent
    check_mode: yes  # just checking
    register: prelink_task

  - debug: msg="prelink is NOT installed on {{ ansible_host }}"
    when: not prelink_task|changed

  - debug: msg="prelink is installed on {{ ansible_host }}"
    when: prelink_task|changed

Remember, we want to confirm that the prelink package is absent (NOT installed), that's the
state we care about, that's the state we want to mark as "ok".  Anything else is NOT "ok" for
the purposes of this example.  Ansible is about describing the state you want the machine in.

You run this playbook against the same systems as above and get the output:

PLAY [all] **********************************************************************************************

TASK [Gathering Facts] **********************************************************************************
ok: [gavin-rhel6-fips]
ok: [gavin-rhel66-epel1]

TASK [Is the prelink package absent?] *******************************************************************
changed: [gavin-rhel6-fips]
ok: [gavin-rhel66-epel1]

TASK [debug] ********************************************************************************************
skipping: [gavin-rhel6-fips]
ok: [gavin-rhel66-epel1] => {
    "msg": "prelink is NOT installed on gavin-rhel66-epel1"
}

TASK [debug] ********************************************************************************************
skipping: [gavin-rhel66-epel1]
ok: [gavin-rhel6-fips] => {
    "msg": "prelink is installed on gavin-rhel6-fips"
}

PLAY RECAP **********************************************************************************************
gavin-rhel6-fips           : ok=3    changed=1    unreachable=0    failed=0
gavin-rhel66-epel1         : ok=3    changed=0    unreachable=0    failed=0


And we can use most if not all of the scripts we wrote for the previous case to filter this output
down to something usable.

Of course, Ansible experts, and even the moderately observant Ansible-newbies will point out that all
that those two debug:when: tasks are superfluous in this case.  The task named "Is the prelink package
absent?"  already tells us if prelink is absent or not.  The line "ok: [gavin-rhel66-epel1]" tells
us that the system gavin-rhel66-epel1 is in the state we specified, and "changed: [gavin-rhel6-fips]"
tells us that gavin-rhel6-fips is NOT.  Remember, we are running in check mode, so gavin-rhel6-fips
was not actually changed, it just would be changed if we were not running in check mode.  We wrote
the two debug:when: tasks because for facts, there isn't a single task/module that will tell
us if the fact is in a given state or not.  But Ansible is extendable...

Ansible has a module Assert that does sorta what we want.  Assert checks that an expression is
true which would let us check that a fact was in a given state.  But, when the expression is false,
assert fails, and doesn't run any further tasks on that system.  We don't want to check and fail,
we just want to check and print out yes/no.  Ideally we would like our new check module to print
out "ok"/"changed" to parallel what other modules do in check mode.  "ok" means yes the system is
in the state you require, "changed" means "no" the system is not in the state you require.

We go get the assert module.  Yea for Open Source.  Preserve the License, Copyright, and Credit
statements.  And a few small changes later, we have a check module that returns "ok"/"changed"
just like a normal module.

Now we can write check mode playbooks that checks both facts and modules uniformly.

The next step is that we are trying to confirm that a set of systems are in a given state.  It would
be better if the output from the playbook run concentrated on that.  We would like to get just a
summary of what machines are and are not in the given state, and if not, which checks (tasks) on
which systems we not in the given state.  Ansible is extendable....
