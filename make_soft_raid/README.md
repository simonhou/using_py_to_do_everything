## 需求描述

在linux机器上使用mdadm制作软raid5，原始流程设计包含多个步骤，设备再一多容易出错。

## 前置依赖

- 容易依赖出错7上进行了测试，如果需要python3.x，需要适当调整
- 适用于对2T以上的device制作分区
- 执行机能免密访问目标机器，即可以执行ssh -q -T -o StrictHostKeyChecking=no -o PasswordAuthentication=no -l root命令
- 执行机上安装了pexpect包
- 目标机器上mdadm工具

## 执行

python mkraid.py <目标机器IP，换成你自己的IP>

## 示例

```
# python mkraid.py <目标机器IP>
find following disks:
*************************
42.9GB      ['/dev/vda']
4001GB      ['/dev/sda', '/dev/sdb', '/dev/sdc', '/dev/sdd', ... '/dev/sdq']
300GB       ['/dev/sdm']
Please enter the correct disk size to make raid:4001GB     # 指定对哪一组盘符进行格式化
4001GB
will make raid 5 using /dev/sda,/dev/sdb,/dev/sdc,/dev/sdd,...,/dev/sdq
 
step1: change to gpt format:
parted -s /dev/sda mklabel gpt
parted -s /dev/sda mkpart primary 0% 100%
parted -s /dev/sdb mklabel gpt
parted -s /dev/sdb mkpart primary 0% 100%
parted -s /dev/sdc mklabel gpt
parted -s /dev/sdc mkpart primary 0% 100%
parted -s /dev/sdd mklabel gpt
parted -s /dev/sdd mkpart primary 0% 100%
...
parted -s /dev/sdq mklabel gpt
parted -s /dev/sdq mkpart primary 0% 100%
 
step2: mkfs:
mkfs.ext4 /dev/sda1
mkfs.ext4 /dev/sdb1
mkfs.ext4 /dev/sdc1
mkfs.ext4 /dev/sdd1
...
mkfs.ext4 /dev/sdq1
 
step3: create raid:
mdadm --create /dev/md0 --level=5 --raid-devices=16 /dev/sda1 /dev/sdb1 /dev/sdc1 /dev/sdd1 ... /dev/sdq1
step4: login <目标机器IP> and execute `watch -n1 cat /proc/mdstat` to check making status.
```

