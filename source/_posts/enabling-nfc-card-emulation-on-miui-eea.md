---
title: 在 MIUI EEA 上自己动手实现 NFC 卡模拟
date: 2023-11-14 16:42:07
tags: [MIUI, Android, Root]
---

前些日子对手上的 Pixel 6 Pro 忍无可忍，趁着好友换小米 14 的机会，带走了他的小米 13。作为对日用系统有着严苛要求、见不得一丝广告的人，到手第一件事自然是解锁刷国际版。由于 [EU 版](https://xiaomi.eu/community/) 只是 **基于国行系统** 的 **第三方** 魔改，我对它也不太信任，选择了从底层上就不一样的 EEA 版，它由官方发布，专为欧盟地区定制，理论上广告和遥测都很少，而且深度集成 Google，对于 Pixel 用户来说迁移起来也很方便。

EEA 版本哪里都好，唯独缺了一项重要的功能：NFC 卡模拟。在国行系统中，这一功能由「钱包」应用提供，它以特殊的方式集成在系统底层，能够直接与安全模块通讯；EEA 版由于底层不一致，系统内没有安全模块的选项，向系统内塞智能卡组件更是直接闪退。尝试使用 [Card Emulator Pro (NFC 卡模拟)](https://play.google.com/store/apps/details?id=com.yuanwofei.cardemulator.pro) 也以失败告终，我并不确定它生成配置的原理，但它似乎只是往固定的位置塞固定的文件，一旦 NFC 配置不同就会失效，甚至直接使 NFC 功能不可用。

除此之外，可能是由于安全模块仍在工作，直接读取手机的 ID 得到的值不是固定的 `01, 02, 03, 04` ，而是 `08, XX, XX, XX` ，其中后三位完全随机，难以直接全文搜索替换。由此看来，唯一能够实现这一功能的方式，就是自行提取、修改系统的 NFC 配置，再将其刷回。我将我的解决办法记录于此，希望能对你有所帮助。

<!-- more -->

> 我所使用的设备是小米 13，系统为 MIUI Global 14.0.6 (UMCEUXM)。不同设备的 NFC 配置可能不同，该文章仅供参考，请勿直接照搬。
>
> 本文不提供懒人解决方案，需要读者至少具有安装了 KernelSU / Magisk 的 Android 手机，以及压缩包操作的基础知识。

## 太长不看：怎么做？

假设需要模拟的卡 ID 是 `AA, BB, CC, DD` ，获取 root 权限后，提取 `/odm/etc` 及 `/vendor/etc` 下 `libnfc` 开头的配置文件，并且：

将 `/odm/etc/libnfc-nci.conf` 中 `NXP_PRFD_TECH_SE` 的值更改为 `0x00` ；

在 `/odm/etc/libnfc-nxp.conf` 中，将 `NXP_NFC_PROFILE_EXTN` 补足：

```
# === 修改前 ===
NXP_NFC_PROFILE_EXTN={20, 02, 05, 01, A0, 44, 01, 00}
# === 修改后 ===
NXP_NFC_PROFILE_EXTN={20, 02, 05, 01, A0, 44, 01, 00, 33, 00, AA, BB, CC, DD}
```

其中填充的 `33, 00` 我并不确定意义，只是照搬了其他手机的配置；如果添加后出现问题，也可以将这一项复原。

将一些模块的默认路由从安全模块修改至本机：

```
#Set the default AID route Location :
#This settings will be used when application does not set this parameter
# host  0x00
# eSE   0x01
# UICC  0x02
# UICC2 0x03
# === 修改前 ===
DEFAULT_AID_ROUTE=0x01
# === 修改后 ===
DEFAULT_AID_ROUTE=0x00
```

除 `DEFAULT_AID_ROUTE` 外，我还修改了 `DEFAULT_ISODEP_ROUTE` 和 `DEFAULT_MIFARE_CLT_ROUTE` ，避免漏改。下方还有一个 `DEFAULT_FELICA_CLT_ROUTE` ，但它的注释中没有写 `host 0x00` ，而且卡模拟应该也不需要动 FeliCa 设置，所以我跳过了这一项。

最后，补足 `NXP_CORE_CONF` ：

```
# Core configuration settings
NXP_CORE_CONF={ 20, 02, 33, 11,
        28, 01, 00,
        21, 01, 00,
        30, 01, 04,
        31, 01, 00,
        32, 01, 60,
        38, 01, 01,
# === 修改前 ===
        33, 00,
# === 修改后 ===
        33, 00, AA, BB, CC, DD,
        54, 01, 06,
        50, 01, 02,
        …………
```

`/vendor/etc` 下有许多 `libnfc` 开头的配置文件，需要逐个修改；也可以使用 VS Code 打开提取出来的文件夹，批量搜索替换。具体配置与 `/odm/etc/libnfc-nxp.conf` 类似，如果没有也不必添加，只修改已经存在的配置即可。

具体来说， `NXP_CORE_CONF` 不需要补充，直接可以看到默认的 `01, 02, 03, 04` ，修改为 `AA, BB, CC, DD` ；额外需要修改的部分是：

```
# Configure the default AID route.
# host  0x00
# eSE   0x82 (eSE),    0x86 (eUICC/SPI-SE)
# UICC  0x81 (UICC_1), 0x85 (UICC_2)
# === 修改前 ===
DEFAULT_ROUTE=0x81
# === 修改后 ===
DEFAULT_ROUTE=0x00
```

这类以 `0x81` 为默认值的配置，包括 `DEFAULT_ROUTE` 、`DEFAULT_NFCF_ROUTE` 、`DEFAULT_OFFHOST_ROUTE` 、`DEFAULT_SYS_CODE_ROUTE` 以及一部分 `DEFAULT_ISODEP_ROUTE` ，推荐一起修改，当然也可以直接使用正则表达式匹配： `DEFAULT_\S+_ROUTE` 。

如此，便完成了配置文件的修改。接下来，下载 [NFC_Emulation.zip](NFC_Emulation.zip) ，将修改后的 `/odm/etc` 的文件放入 `odm/etc` 下， `/vendor/etc` 的文件放入 `system/vendor/etc` 下，重新打包后使用 KernelSU 或 Magisk 刷入即可。

## 折腾过程

一开始，我参考了 [《MIUI 国际版/EU  安装小米钱包 傻瓜教程》](https://zhuanlan.zhihu.com/p/264800660) 、 [《MIUI 国际版/EU 版本地化教程 - 小米钱包篇》](https://sspai.com/post/60065) 以及 [《小米 11 Pro 折腾笔记》](https://wingu.se/2021/06/14/xiaomi.html) ，也用了 [MIUI EU 欧洲版 本地化 Magisk 模块](https://blog.minamigo.moe/archives/184) ，试图还原小米钱包 app 以及相关的智能卡组件，结果它们要么将钱包 app 放在 `/system/app` 却无法启动，要么放在 `/system/product/app` 后虽然可以启动钱包，但会在点击公交卡 / 门卡后直接闪退。除此之外，向 `system.prop` 中添加 `ro.se.type=eSE,HCE,UICC` 后，NFC 设置也没有像预期那样出现「安全模块设置」。

试图从卡刷包中提取钱包组件的尝试也以失败告终。我将 `payload.bin` 解包得到了文件格式为 `data` 的 `system.img` ，无法继续：它们既不能挂载到本地目录，也不能被 `file` 命令读取到正确的格式，看来除非我抛弃所有数据刷回原厂系统，否则是无法继续了。考虑到此前没有正常工作的 [模块](https://blog.minamigo.moe/archives/184) 提供的理应是正确版本的安装包，安全模块设置也与 EU 版表现不同，我理智地放弃了这一条路，转而选择对 NFC 设置进行研究。

于是，为了一次性搞定所有问题，我简单粗暴地把我见到的所有文件都拉了出来，对照着 Pixel 6 Pro 提取出来的文件，按照上面描述的方法一通编辑，然后重新打包为模块刷入后，它奇迹般地工作了。由于能查询到的相关文档实在太少，并且 `odm` 与 `vendor` 分区都受厂商控制，很难从 AOSP 项目中找到相关内容，为了弄明白到底是哪一项设置在起作用，我又在 `/data/adb/modules` 内模块目录下对配置文件进行修改，结果发现 `/odm/etc` 下的配置似乎不重要，哪怕只是使用原来的文件进行替换，NFC ID 也会从随机数变成 `01, 02, 03, 04` 。

当我更新 `/vendor/etc` 下某个文件的 `NXP_CORE_CONF` ，并以此开始测试各项设置时，灵异的事情发生了：重启后 NFC 虽然显示已开启而且可以正常开关，但无法被其他设备读取。紧接着我将理应工作正常的文件放回了 `/data/adb/modules` ，却再也无法使它恢复正常，直到我将模块卸载后重新刷入。看着 `/vendor/etc` 下面整整十个 `libnfc` 开头的文件以及每个文件里各有不同的繁琐配置，以及每次卸载后重新安装模块所需的漫长等待时间，我选择放弃一探究竟，将其留给后人探索。
