---
title: 在 OpenWrt 上打造 Rickroll 访客 Wi-Fi
date: 2022-04-08 01:06:25
tags: [OpenWrt, Linux, Rickroll, 访客网络]
---

昨天在 TG 上看到隔壁频道的点子：必须观看一定时间 [Rickroll](https://www.bilibili.com/video/BV1GJ411x7h7) 后才允许连接，并且每次暂停会 +10s 的访客 Wi-Fi，顿时震惊：「原来还可以这么搞？？」仔细分析可行性后发现，这个访客 Wi-Fi 原理并不复杂，有折腾 OpenWrt 经验并且写过一丢丢 HTML 的话极其容易上手，于是将步骤记录如下。

## 0. 准备条件

- 一台运行 OpenWrt 的路由器
- 一台能联网并且能 `ssh` 的设备
- 一点点计算机网络及开发知识
- 一点点折腾精神

> 我自己使用的是红米 AX6 基于 [LEDE](https://github.com/coolsnowwolf/LEDE) 的自编译固件，因此能深入地自主精简、定制，如果没有自编译固件的条件或想法，可能会遇到一些奇妙的依赖问题。推荐选择闪存容量大或可扩展存储的路由器，防止折腾半天发现没有留给视频的空间。除此之外，如果想对这个访客网络进行限速（比如使用 SQM QoS），那么也许还需要较强的性能。

<!-- more -->

## 1. 创建访客网络

既然是新造访客 Wi-Fi，那第一步自然是把这个 Wi-Fi 做出来。OpenWrt 后台的 `网络 -> 无线` 设置中，在想要创建新网络的网卡上点击「添加」，在下方的接口配置——基本设置——网络中勾选「创建」输入 `lan_guest` （或者任何其他名字，只要能分辨出这是访客网络），进行一些自定义，然后「保存&应用」。

接下来，打开 `网络 -> 接口` ，应该已经能看到刚刚添加的新接口了。我们点进它的「修改」，将协议切换到「静态地址」，调整访客网络的网关：「IPv4 地址」。我主用网络的网关 / `lan` 中设置的地址为 `192.168.13.1` ，这里就可以写成 `192.168.3.1` 或者任何一个不以 `192.168.13` 开头且符合 IPv4 标准的值，再把子网掩码调整到 `255.255.255.0` 。如图所示，我选择的是 `192.168.0.1` ，声明了我这个接口占用了 `192.168.0.0/24` 这个网段，也就是 `192.168.0.0 ~ 192.168.0.254` 。对这些不熟悉的话，按照图上来就好。

![interface](interface.png)

此时「防火墙设置」中默认选中的应该是「不指定或新建」，我们在后面的文本框中同样输入 `lan_guest` （不必相同，只是方便辨识），保存，在 `网络 -> 防火墙` 中就能看到新建的这个区域了。点击「修改」，这时「覆盖网络」应当勾选且只勾选了 `lan_guest` ，将「入站数据」、「出站数据」和「转发」全部调至「接受」，下方「端口触发」中「允许转发到*目标区域*」勾选 `wan` ，保存即可。这样，我们将访客网络和主用网络隔离开，不允许互相访问。

> 如果你不需要对访客网络进行再进一步的限制，在「防火墙设置」处可以直接将访客网络划入 `lan` 。这一步主要是为了后面阻止访客网络访问路由器配置。

![firewall](firewall.png)

这时，我们已初步完成访客网络的搭建。然而，此时的访客网络除了无法与主用网络通信外还没有任何限制，不过它的好日子也不长了，我们接下来就「限制访客访问后台」并「对访客网络限速」。

## 2. 限制访客访问后台

默认情况下，OpenWrt 的 HTTP 服务器 `uhttpd` 监听的是 `0.0.0.0:80` ，也就是所有连接请求只要发送就照单全收，这肯定不是我们想要的，所以我们要将它改成主用网络的网关地址。如果你安装了 `luci-app-uhttpd` 软件包，那么可以在管理后台修改；下文说的是没有安装这个软件包的情况，我们需要用 `ssh` 连入后台，用 `uci` 修改配置。

用任意趁手的 `ssh` client 连入路由器后台后，我们执行 `uci show uhttpd` 看看当前的配置。默认情况下，它应该长这样：

```shell
…
uhttpd.main=uhttpd
uhttpd.main.listen_http='0.0.0.0:80' '[::]:80'
uhttpd.main.listen_https='0.0.0.0:443' '[::]:443'
uhttpd.main.redirect_https='0'
…
```

在不使用 HTTPS 的情况下，第二行就是我们要更改的配置。我主用网络的网关在 `192.168.13.1` ，所以我输入的内容如下：

```shell
uci set uhttpd.main.listen_http='192.168.13.1:80'
uci commit
/etc/init.d/uhttpd restart
```

分别代表着「将监听地址设置到 `192.168.13.1` 」，「保存设置」，「重启 HTTP 服务器 / 重启后台」。此时再 `uci show uhttpd` 可以看到，我们调整的内容出现在了以 `uhttpd.main` 开头的列表的最末端，并且通过访客网络已经无法再打开路由器后台。

## 3. 对访客网络限速

> 若不需限制访客网络速度，可忽略本节内容；本节需要安装 `luci-app-sqm` 和 `sqm-scripts` 软件包。  

创建、隔离都完成了，接下来就要对访客做限速了——毕竟在限速 24Mbps 的校园网环境，放任访客随便跑带宽势必会影响主用网络。我们用于限速的工具是 `luci-app-sqm` ，它是 `sqm-scripts` 的 GUI 控制台，附带了一系列用于控制网络质量的工具。在网络正常的情况下，你可以直接这样安装它们：

```shell
opkg update
opkg install luci-app-sqm
```

完成后，在 OpenWrt 后台的 `网络 -> SQM QoS` 里就能调整限速设置。在「接口名称」处选中刚刚新增的 `lan_guest` ，再自主指定上下行速率就行。

![qos](qos.png)

## 4. Rickroll！

> 本节需要安装 `nodogsplash` 软件包，并且可能需要一些前端开发知识。

最后一步就是配置验证服务了。它的学名叫 captive portal 「强制门户」，常见于机场、星巴克等地的公共 Wi-Fi，同时也被用来做校园网 Wi-Fi 的登录页。原理很简单，现代设备都有一个检查网络是否可用的机制，我们只要将它们检测网络可用的数据包指向我们的认证页面，系统就知道这个网络需要认证才能使用，并自动打开认证页面。

要造轮子理论上并不难，但已经有了用于完成这一整套步骤的完善工具： [Nodogsplash](https://github.com/nodogsplash/nodogsplash) 。像这样操作就能安装并启动它：

```shell
opkg update
opkg install nodogsplash
/etc/init.d/nodogsplash start
```

默认情况下，Nodogsplash 会在重启时自动启动，并且对 `lan` 下的所有设备启用认证。使用 `uci show nodogsplash` 可以看到像这样的一段：

```shell
…
nodogsplash.@nodogsplash[0]=nodogsplash
nodogsplash.@nodogsplash[0].enabled='1'
nodogsplash.@nodogsplash[0].fwhook_enabled='1'
nodogsplash.@nodogsplash[0].gatewayname='OpenWrt Nodogsplash'
nodogsplash.@nodogsplash[0].gatewayinterface='br-lan'
…
```

但我们只希望它监听访客网络，所以我们修改 `nodogsplash.@nodogsplash[0].gatewayname` 的值：

```shell
uci set nodogsplash.@nodogsplash[0].gatewayinterface='wlan1'
uci commit
```

这里的 `wlan1` 应修改为访客网络的接口名。在我的案例中，我将没有用上的 2.4GHz Wi-Fi 设置为了访客网络，所以它是 `wlan1` ，如果一张网卡下有多个 Wi-Fi 网络，它也可能是 `wlan1-1` 等，不确定的话可以参考 `SQM QoS` 的「接口名称」设置，括号内是 `lan_guest` ，括号外就是访客网络对应的接口名。

初始认证页面，作为示例，是一个有图有文字，只要点击「Continue」就会认证成功的简单页，位于 `/etc/nodogsplash/htdocs/splash.html` ，我们修改这个文件的内容就能控制认证页面。我将我写完的 `splash.html` 放在了 [nodogsplash-rickroll](https://github.com/Rachel030219/nodogsplash-rickroll) 这个 GitHub 项目中，可以直接用我完成的 `splash.html` 替换掉已有文件，再将视频命名为 `nevergonnagiveyouup.mp4` 放在同一文件夹（ `/etc/nodogsplash/htdocs/` ）下，输入 `/etc/init.d/nodogsplash restart` ，就能看到效果。

***

如果你还想深入了解这个页面的组成，这里摘录 `<body>` 部分如下：

```html
<h1>Never Gonna Give $clientip Up</h1>
```

这是一个朴素的一级标题，调用了 Nodogsplash 的变量功能，将 `$clientip` 替换为当前认证设备的 IP 地址。这个特性在提交认证数据部分也有用到：

```html
<form id="authform" method="get" action="$authaction" hidden>
    <input type="hidden" name="tok" value="$tok">
    <input type="hidden" name="redir" value="$redir">
    <input type="submit" value="开始上网">
</form>
```

除了用来控制显示的 `id="authform"` ，这个 `<form>` tag 用于向 `$authaction` （会被替换为实际的认证地址）提交一个 GET 请求，附带了一个 token `$tok` 和重定向目标 `$redir` 。这是官方推荐的用来认证设备的方式。除此之外，Nodogsplash 还提供了许多其他变量，在自带的 `splash.html` 中可以找到，包括网关 / 用户 MAC，网关名等。

```html
<video id="video" autoplay loop controls>
    <source src="nevergonnagiveyouup.mp4" type="video/mp4">
    你的浏览器不支持 video 标签。
</video>
```

这就是一个简单的视频播放组件，包含了「自动播放」、「循环播放」两个特性，还提供了播放控制（也带来了暂停惩罚）。 `src` 告诉浏览器应该播放的是同一个文件夹下的 `nevergonnagiveyouup.mp4` ， `type` 则声明了视频的类别。

文件末尾是一段 JavaScript，作用已在注释中说明，完成了最基本的倒计时 + 暂停检测功能。

> ⚠注意⚠：你可能已经看到了，官方注释中说： 
>
> *It should be noted when designing a custom splash page that for security reasons many CPD implementations: Immediately close the browser when the client has authenticated. Prohibit the use of href links. Prohibit downloading of external files (including .css and .js). **Prohibit the execution of javascript.***
>
> 翻译过来，为了安全考虑，完成认证后应该立即关闭浏览器，禁止使用 href 链接，禁止引用外部文件， **禁止执行 JavaScript** 。本文完成的认证页面只是「图一乐」，如果需要大面积部署到生产环境，请务必尽最大可能遵循这几条原则。

***

同文件夹下还有一个 `status.html` ，用来告诉设备「你已经连上了，不用尝试连接了」，文章完成时我还没有动它，如果有兴趣的话可以折腾折腾。

## 5. 搞定！

如此，我们就完成了一个 ~~电信诈骗~~ 访客 Wi-Fi。 ~~快去诈骗你的朋友们吧！~~

***

**参考与感谢：**

1. 灵感来源：[https://t.me/CyanCh/855](https://t.me/CyanCh/855)
2. Nodogsplash Documentation: https://nodogsplash.readthedocs.io/

