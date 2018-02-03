---
title: 将 Ubuntu 引导从 Legacy 转换为 UEFI
date: 2018-02-03 15:20:03
tags: [Linux,System,BIOS]
---

最近突然心血来潮，想用 `UEFI` 装 Windows 10 玩玩，搞定了安装 U 盘后发现之前的 Ubuntu 一直使用 ``Legacy`` 作为引导方式。秉着人不折腾就会死的精神，弄了差不多一整天，终于将 Ubuntu 的引导方式从 `Legacy` 转为了 `UEFI` ，并成功地实现了 Ubuntu 与 Win10 双系统引导。为了方便各位作死，特在此分享出来。

> 注意：本文需要计算机引导的基本知识以及一定的动手能力，若不熟悉 Linux 命令行，虽可完成所有步骤，但不建议尝试。本文所述 Ubuntu 包含所有 Ubuntu 分支，例如 Lubuntu 和 Xubuntu 。
<!--more-->

## Ubuntu `Legacy` 转 `UEFI`

### Step 1. 建立 ESP 分区

首先进入任何一个 **EFI 启动** 的、基于 Ubuntu 的 Live System ，使用 `GParted` 在硬盘首 2.2 TB 内分出 100MB 以上（推荐 200MB ）的空间，格式化成 FAT32 后 `Manage flags` 勾选 `boot` ，像这样：

![01](http://img.vim-cn.com/f9/3e3680bcb7eceae05c15d5612de80440ef28a5.png)

### Step 2. 迁移 Ubuntu 引导文件

**反复确认网络没问题** ，然后打开终端，用以下命令安装 [`Boot Repair`](https://launchpad.net/~yannubuntu/+archive/ubuntu/boot-repair) ：

```shell
sudo add-apt-repository ppa:yannubuntu/boot-repair
sudo apt update
sudo apt install boot-repair
```

或者，你也可以使用 [`Boot Repair CD`](https://sourceforge.net/p/boot-repair-cd/) ，基于 Lubuntu 。总之，在一切完成后，启动 `Boot Repair` 。

![02](http://img.vim-cn.com/74/745a352737e686f62ad56ab548e48dc5ca3464.png)

等待数据收集完毕，在 `Advanced options` 选择 `GRUB location` ，如果原来是使用 `Legacy` 引导，那么勾选 `Seperate /boot/efi partition` ，选择刚刚在 `GParted` 中分好的区（这里是 `/dev/sda1` ）。

![03](http://img.vim-cn.com/e5/4f4ad7d3c1deb809c300654d9e0bfc7ac36b18.png)

点击 `Apply` ，然后跟着 `Boot Repair` 的指示做，并静等完成。

### Step 3. 试试看！

```shell
reboot
```

### Step 4. 跌进大坑？

如果这里直接启动已经没问题，那么这一部分就到此为止了。如果有问题……

#### 关掉 `Legacy` 支持

在 BIOS 的设置页面中，一般能找到类似于「启用 `Legacy` 支持」的选项。把它关掉 ~~我们还能做朋友~~ 即可仅使用 `UEFI` 来引导启动。当然如果已经爆炸这也没什么用处，可能也就只是确定确实是 `UEFI` 的问题而不是系统仍然在尝试走 `Legacy` 。

#### 尝试用命令行重新安装 GRUB

进入 Live System ， **确保网络通畅** ，用 `GParted` 记下原系统所在的分区（比如说我的是 `/dev/sda2` ），然后打开终端，键入：

```shell
sudo mount /dev/sda1 /mnt
sudo mkdir -p /mnt/boot/efi
sudo mount /dev/sda3 /mnt/boot/efi
sudo mount --bind /dev /mnt/dev
sudo mount --bind /proc /mnt/proc
sudo mount --bind /sys /mnt/sys
sudo mount --bind /run /mnt/run
modprobe efivars
sudo chroot /mnt
```

这时，这个终端已经切换 root 到了原系统并可以用最高权限进行一些操作，随后我们便需要在原系统上重新安装支持 `UEFI` 引导的 GRUB ，即 `grub-efi-amd64` 。

```shell
apt install grub-efi-amd64
grub-install --target=x86_64-efi --efi-directory=/boot/efi --bootloader-id=ubuntu --recheck --no-floppy --debug
```

现在再重启试试看？

#### 将分区表从 `MBR` 转换成 `GPT`

虽然 `MBR(Master Boot Record)` 并不影响 `UEFI` 的正常引导，但 Windows 却拒绝使用，转而要求用户切换到 `GPT(GUID Partition Table)` 。 `Legacy` 只能通过 `MBR` 引导，因此通常执行完上述操作之后分区表仍然采用 `MBR` ，强烈推荐更换到 `GPT` 。

要从 `MBR` 切换到 `GPT` ，操作也不是很困难，需要使用 `gdisk` 。首先在 Live System 中安装并以系统所在硬盘为对象运行：

```shell
sudo apt install gdisk
sudo gdisk /dev/sda
```

在 `gdisk` 启动后，目前的分区表情况会显示在屏幕中。为了将 `MBR` 转换为 `GPT` ，首先需要按 `r` ，进入 `恢复/转换` 模式，接着 `f` 启动转换，若需要确认操作则输入 `Y` ，一切后用 `w` 保存并退出。此时，分区表就从 `MBR` 被转换为了 `GPT` 。重新进入 `gdisk` 可看到，原有的 `MBR` 分区表变成了 `Protective` ，而 `GPT` 变成了 `Present` 。

此时建议重新使用命令行安装 GRUB 或者重新运行一遍 `Boot Repair` ，虽然不确定不重新安装是否会影响正常启动。此外，按道理来讲是否转换并不会干涉 `UEFI` 下 Ubuntu 的启动， 但奇幻的是本人的问题在转换完后消失掉了……

## UEFI 引导 Windows 安装

### Step 1. 安装 Windows 10

傻瓜式的操作步骤应该没有问题（吧）……

### Step 2. 使用 GRUB 引导 Windows 10

这个也不难……请翻出 `Boot Repair` 进行一次 `Recommended Repair` ，然后应该就啥问题没有能够正常引导 Windows 10 了。

### Step 3. Enjoy it!

```shell
reboot
```

***

#### References:

1. [UEFI](https://help.ubuntu.com/community/UEFI) - Ubuntu Documentation
2. [Which commands to convert a Ubuntu BIOS install to EFI/UEFI without boot-repair on single boot hardware?](https://askubuntu.com/questions/509423/which-commands-to-convert-a-ubuntu-bios-install-to-efi-UEFI-without-boot-repair) - Ask Ubuntu
3. [How to change ubuntu install from Legacy to UEFI](https://askubuntu.com/questions/913397/how-to-change-ubuntu-install-from-Legacy-to-UEFI) - Ask Ubuntu
4. [How to reinstall GRUB2 EFI?](https://superuser.com/questions/376470/how-to-reinstall-grub2-efi) - Super User
5. [Does the UEFI partition either “MUST” or “SHOULD” be first for some reason? If so why?](https://askubuntu.com/questions/618244/does-the-UEFI-partition-either-must-or-should-be-first-for-some-reason-if-s) - Ask Ubuntu
6. [Steps to Convert MBR to GPT Ubuntu / Debian with images](http://www.linuxtopic.com/2017/08/convert-mbr-to-gpt.html) - LinuxTopic
7. [WindowsDualBoot](https://help.ubuntu.com/community/WindowsDualBoot) - Ubuntu Documentation

