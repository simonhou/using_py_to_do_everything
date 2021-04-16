#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: houjun
# @Date:    16/4/2021
# @Last Modified by:  houjun
# @Last Modified time:  16/4/2021

import subprocess
import sys
import time
import pexpect

reload(sys)
sys.setdefaultencoding('utf-8')

def ssh_cmd(host, cmd, timeout=100):
    global sshq
    sshq = "ssh -q -T -o StrictHostKeyChecking=no -o PasswordAuthentication=no -l root"
    return execute_cmd(sshq + " " + host + " " + cmd + " ", timeout)


def local_cmd(cmd, timeout):
    try:
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = ""
        t_beginning = time.time()
        while True:
            if p.poll() is not None:
                break
            seconds_passed = time.time() - t_beginning
            if timeout and seconds_passed > timeout:
                p.terminate()
                raise Exception(cmd, timeout)
        for line in p.stdout.readlines():
            output = output + line
        p.wait()
        return output
    except Exception, e:
        print e


def execute_cmd_local(cmd):
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    return proc.stdout.read().__str__()


if __name__ == '__main__':
    host = sys.argv[1]
    cmd = "parted -l |grep /dev"
    result = ssh_cmd(host, cmd)
    disk_dict = {}
    for i in result.strip().split("\n"):
        tmp = i.split(" ")
        if tmp[2] in disk_dict.keys():
            disk_dict[tmp[2]].append(tmp[1].strip(":"))
        else:
            disk_dict[tmp[2]] = [tmp[1].strip(":")]
    print "find following disks:\n*************************"
    print '{}\t{}'.format("disk_size", "disks")
    for k, v in disk_dict.items():
        print '{}\t\t{}'.format(k, v)

    disk_size = raw_input("Please enter the correct disk size to make raid:")
    print disk_size
    if disk_size in disk_dict.keys():
        print "will make raid 5 using %s" % ",".join(disk_dict[disk_size])
        print "\nstep1: change to gpt format:"
        for dev in disk_dict[disk_size]:
            cmd1 = "parted -s %s mklabel gpt" % dev.strip()
            print cmd1
            ssh_cmd(host, cmd1)
            cmd2 = "parted -s %s mkpart primary 0%% 100%%" % dev.strip()
            print cmd2
            ssh_cmd(host, cmd2)
        print "\nstep2: mkfs:"
        for dev in disk_dict[disk_size]:
            cmd3 = "mkfs.ext4 %s1" % dev.strip()
            print cmd3
            ssh_cmd(host, cmd3)
        print "\nstep3: create raid:"
        cmd4 = "mdadm --create /dev/md0 --level=5 --raid-devices=%d %s" % (
        len(disk_dict[disk_size]), " ".join(list(map(lambda x: x + '1', disk_dict[disk_size]))))
        print cmd4
        child = pexpect.spawn(sshq + " " + host + " " + cmd4)
        child.expect('Continue creating array?', timeout=None)
        child.sendline('yes')
        child.expect(pexpect.EOF, timeout=None)
        print "\nstep4: login %s and execute `watch -n1 cat /proc/mdstat` to check making status." % host
    elif disk_size in ("exit", "bye"):
        sys.exit(0)
    else:
        print "wrong disk choose,exit"
