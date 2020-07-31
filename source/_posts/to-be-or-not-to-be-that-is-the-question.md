---
title: 技术共享的现状 - 生存还是毁灭，这是一个问题
date: 2017-07-08 17:33:12
tags: [随笔,开源,Google]
---

> 「技术共享」是什么？
> 它是一种信念。

<!-- more -->
## 毁灭
Linux kernel ，作为在操作系统内核方面开源的先驱，距离诞生已有 24 年之长，并即将在 8 月 25 日迎来第 25 次生日。这个曾经在国际社会上引起巨大轰动的内核（底层），只在一波热潮之后便迅速被寻常百姓所忘记。即使是在第 25 个年头，基于 Linux 的系统（发行版）在市场上的占比仍然低于基于 Unix 的 macOS ，更别说和 Windows 比较了。

为什么？

Linux 提倡的是「技术共享」，也就是人人可查阅、人人可使用、人人可修改，任何人都能修改任何人修改/创造的任何开源软件并根据协议使用。这本是一个非常超前的理念。然而，正是因为任何人都能以开源协议重新发布，使得 Linux 的发行版有…… *我数不清了丢个链接给你们你们自己数吧： [List of Linux distributions](https://en.wikipedia.org/wiki/List_of_Linux_distributions)* 这么多种，碎片化非常严重，包管理器混乱，几乎每更换一个发行版，甚至每更换一个软件包，就得重新适应一遍并养成新的习惯。虽然 Linux 最开始的目的「技术共享」已经达到，每个人都能够获取到最新的技术，然而 Linux 对普通用户的吸引力并不高，「技术共享」对普通用户来讲仍然是一个可望而不可及的梦想。

而在用户占比上将 Linux 及其发行版远远甩在后面的 Windows ，在一些人的眼里从头到脚全是「罪恶」。闭源的内核，闭源的软件，闭源的一整个生态链，使得许多极客对 Windows 嗤之以鼻。然而，对于普通用户来讲， Windows 无疑是最好的选择。

为什么？

「不用折腾」。 Windows 的用户都是渴望稳定的，他们不愿意折腾，他们也不需要折腾就能用上稳定的系统和软件，这在很多时候比「技术共享」和「自由」更有吸引力。

除此之外，不知道你是否听说过 Steam 。作为一个游戏平台， Steam 无疑是成功的，每年大量的打折活动给开发者和其背后的 Valve 带来了同样大量的利润。然而 Steam 上的游戏，大部分却只有 Windows 版本。与此相同，由 Adobe 所开发的 Photoshop 、 Premiere Pro 、 After Effects 等优秀应用，也只有 Windows 和 macOS 版本。这些游戏 / 应用未必开源也未必自由，它们大部分都需要付费，导致了「某个游戏因为砸钱自己做了一套黑科技引擎爆红之后坐着收钱」，从而「同样的内容我的游戏砸钱买好引擎卖得更好」，又或者「某个软件因为秘密的优化技巧得到大量用户」。

它们之间有「技术共享」吗？恐怕各位都知道，当然没有。在追名逐利的 21 世纪，完全开放而自由的软件尤其稀少，而且大部分都被限制在了 Linux 及其各类发行版上，所以推广开来几乎是一个遥不可及的梦想。

Android ，作为 Mobile 端最大的操作系统，碎片化与 Linux 同样严重。暂且不说各种爱好者开发的第三方开源 ROM ，即使是厂商自己出厂预装，也有各种各样的不同，像 Sony 机型的 ROM 与 Samsung 的 TouchWiz 就完全不能扯到一处，更别说各类中国特色（比如 MIUI EMUI EUI Funtouch ……）了。

而 Android 的拥有者， Google ，正出于各种我们无法获知的原因逐渐降低 AOSP （ Android Open Source Project ）的自由度，收紧对 Android 的控制。曾经的 AOSP 源码内附带了一整套 Android 基础应用，从相机到日历再到浏览器，而现在， AOSP 内只含有极少一部分。厂商只有两个选择，一是抛弃大多数 Google 用户自己做一套，另一个就是支付高昂的授权费以内置 Google 的 GMS 。 Cyanogen 曾经有过一个宏伟的计划，想要建立一个完全 Google-free 的 Android 生态，最后却遗憾退场。也许你会这样说：「 Android 就是 Google 家的， Google 对 Android 的控制有何不可？」然而，如果当初就想把 Android 牢牢掌握在手中，又为何要将其开源？

「技术共享」之所以不为人所看好，其中一个巨大的原因就是利益。现在大部分人的创造都只是为了利益，仅此而已。我的产品创意新，就能卖到更高的价格；我的开发周期比友商短，就能更早上市捞钱；我的宣传比友商好，就能坐拥用户资源，如此这般，等等等等。
## 生存
Google 对 Android 的控制欲，在 Android 3.0 Honeycomb 发布的时候就已经体现出来。当时的 Honeycomb 几乎完全不开源，但 Google 很快就发现这样完全行不通，根本没有厂商会选择继续花钱升级到 Honeycomb ，大部分都仍然在使用 Gingerbread 甚至 Froyo 。这种大部分厂商落后时代的局面直到 Android 4.0 Ice Cream Sandwich 发布才得到缓解。

同样，在如今的应用市场上不乏能与闭源软件分庭抗礼的开源应用。比如，与 Photoshop 一样强大的 GIMP ，与 UltraISO 齐头并进的 UNetbootin ，以及完全找不到替代品的 VLC ……

知识不应当用来出售，知识应该共享。如果 Nikola Tesla 没有共享自己的发现，那么日落后的世界也许仍然漆黑一片；如果 Marie Curie 没有共享自己的成果，那么可能没有人知道辐射为何物；如果 Niels Bohr 没有共享自己的技术，那么历史书上的二战大概会到 1948 年。知识带来的应该是荣誉，而不是万贯家财。研究的原因应该是研究，而不是成果发布后的利益。

不管「技术共享」的现状怎样，当我们坚信未来会发生的时候，未来就正在发生。

愿每一个人都能获取自己需要的技术并得到帮助，不管白人抑或黑人，不管贫穷抑或富贵。

***

#### References:
1. https://en.wikipedia.org/wiki/Open-source_software - Wikipedia
2. https://en.wikipedia.org/wiki/History_of_Linux - Wikipedia
3. https://www.netmarketshare.com - NetMarketShare
4. https://en.wikipedia.org/wiki/List_of_Linux_distributions - Wikipedia
5. [https://en.wikipedia.org/wiki/Android_(operating_system)](https://en.wikipedia.org/wiki/Android) - Wikipedia
6. https://www.oschina.net/news/63203/how-google-control-android - OSChina
7. https://en.wikipedia.org/wiki/CyanogenMod - Wikipedia
8. https://en.wikipedia.org/wiki/Nikola_Tesla - Wikipedia
9. https://en.wikipedia.org/wiki/Niels_Bohr - Wikipedia