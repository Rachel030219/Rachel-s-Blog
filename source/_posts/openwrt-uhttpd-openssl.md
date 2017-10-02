---
title: OpenWrt uHTTPd 与 OpenSSL 初探
date: 2017-06-05 10:00:35
tags: [OpenWrt,uHTTPd,OpenSSL]
---

前些日子家里的 Phicomm K2 刷上了 OpenWrt ，苦于闪存剩余空间严重不足，只能玩玩已经有的那些个软件包，正好最近着迷于 Web Server ，于是便 ~~又~~ 折腾了起来——

### Introduction / 介绍

> **uHTTPd** is a web server written from scratch by OpenWrt/LuCI developers. It is aimed towards being an **efficient** and **stable** server, suitable for **lightweight tasks** commonly used with embedded devices and proper integration with OpenWrt's configuration framework (UCI). In particular, it is configured by default for the [LuCI](https://wiki.openwrt.org/doc/techref/luci) web interface to administer OpenWrt. **In addition, it provides all the functionality expected of present day web servers.**
> —— 摘自 OpenWrt Wiki - [uHTTPd](https://wiki.openwrt.org/doc/howto/http.uhttpd)

划一下重点： uHTTPd 是一个小巧精干的 Web 服务器，适合轻量任务，通常与嵌入式设备一起使用，而且提供了现在 Web 服务器的全部功能。
### Configuration / 配置
<!-- more -->
uHTTPd 的默认配置存放于 `/etc/config/uhttpd` ，非常简单，如下：
```
config uhttpd 'main'
        list listen_http '0.0.0.0:80'
        list listen_http '[::]:80'
        list listen_https '0.0.0.0:443'
        list listen_https '[::]:443'
        option redirect_https '0'
        option home '/www'
        option max_requests '3'
        option max_connections '100'
        option cert '/etc/uhttpd.crt'
        option key '/etc/uhttpd.key'
        option cgi_prefix '/cgi-bin'
        option http_keepalive '20'
        option tcp_keepalive '1'
```
uHTTPd 的配置，比 ~~垃圾~~ NGINX 要简单得多，我们来逐行看看：
第一行， `config uhttpd 'main'` ，说明了这个配置是设置给 uHTTPd ，名字为 `main` ，即主设置
然后， `list listen_http` 和 `list listen_https` 则是分别声明了监听 HTTP 和 HTTPS 的位置以及端口， `0.0.0.0` 表示监听本设备的 IPv4 请求。
`option redirect_https` 表示将 HTTP 80 端口访问的请求重定向到 HTTPS 443 端口，在 NGINX 中复杂的设定 uHTTPd 一行就能搞定 ~~所以说 NGINX 垃圾~~ ，然而，我们没有办法给 OpenWrt 签发一个不会被拒绝的证书，因此这个设置除非是在本地（访问 LuCI 的客户端）安装了证书或者有特殊的需要，抑或者花钱找了 CA ，基本无用。
`option home` 指定了 Web 服务器的根文件夹，相当于 NGINX Server 块中的 `root` 。当收到数据包并建立连接时， uHTTPd 会读取这个文件夹中的文件并发送出去。
`option max_requests` 和 `option max_connections` 则指定了最大并发请求数量和最大并发连接数量，这个数字越大，对 OpenWrt 的（可能）负载也就越大。当超过这个阀值时，请求和连接将被放入队列中等候。
`option cert` 和 `option key` 则定义了网站签发的证书和私钥。 uHTTPd 默认使用的是自带的，虽然省心但是自带证书内含的信息还是太少而且总是提醒安全问题 ~~说得好像自己证书的不会一样~~ ，在这里就可以使用自己的证书。 
`option cgi_prefix` 指的是使用 CGI 的时候脚本的前缀，是 `option home` 的相对路径。在本例中，因为 `option home` 指向 `/www` ，因此前缀就是 `/www/cgi-bin` 。

> In computing, **Common Gateway Interface** (**CGI**) offers a standard protocol for web servers to execute programs that execute like Console applications (also called Command-line interface programs) running on a server that generates web pages dynamically.
> ——摘自 Wikipedia - [Common Gateway Interface](https://en.wikipedia.org/wiki/Common_Gateway_Interface)

`option http_keepalive` 和 `option tcp_keepalive` 定义了 HTTP 连接和 TCP 连接的常驻连接，以在需要时提高效率。这个数值的大小会直接影响到 OpenWrt 的负载。
### Trying / 实战

接下来，让我亲自试试使用 OpenSSL 和 uHTTPd 来生成自己的一套证书并使用。
```shell
opkg install openssl-util luci-ssl
```
首先，安装 `openssl-util` 和 `luci-ssl` 包，总共不到 191 KB 。

```shell
cd /tmp
mkdir ./cert
cd ./cert
```
然后，切换到 `/tmp/cert` ，我们就在这里大干一场吧。

```shell
openssl genrsa -des3 -out server.key 1024
openssl rsa -in server.key -out server.key
```
这样， OpenSSL 会自动生成一个 server.key ，这就是我们用到的服务端私钥。在生成的过程中，会要求我们输入一个 pass phrase ，也就是这个私钥的密码。在之后的操作中，只要用到了这一步生成的 server.key 就会需要这个私钥。
~~此外，如果不想要密码的话，可以通过 `openssl rsa -in server.key -out server.key` 去除。~~
由于需要私钥密码的话我们自己需要在本地也安装好所生成的证书，因此我们 **必须** 移除密码。当然，最开始我们也可以直接 `openssl genrsa 1024 -out server.key` 来避免输入密码。

```shell
openssl req -new -key server.key -out server.csr
```
这一步是生成我们给 CA 签名，或者自己签名所需要的 csr 文件。在这一步中， OpenSSL 会请求很多信息，照填即可，像我的是这样：
```shell
Country Name (2 letter code) [AU]:CN
State or Province Name (full name) [Some-State]:Hunan
Locality Name (eg, city) []:Shaoyang
Organization Name (eg, company) [Internet Widgits Pty Ltd]:Pandora Box
Organizational Unit Name (eg, section) []:LuCI
Common Name (e.g. server FQDN or YOUR name) []:192.168.13.1
Email Address []:tangrui003@gmail.com
```
完成后，我们就生成了自己的服务端证书 server.csr 。

```shell
openssl req -x509 -days 365 -key server.key -in server.csr -out server.crt
```
因为 server.csr 必须要 CA 的签名才可使用，我们就来自己给自己签一个名。当然，如果有钱，也可以把这个 server.csr 下载下来丢到可信任的 CA 那里签。这里我们选择比较偏激的一种方法，直接使用我们的 server.key 和 server.csr 文件充当 CA 证书，用这两个文件给 server.csr 签名（就是自己签自己）。虽然说肯定不能用，但是自己玩玩还是够了。
`-days` 后面接的是证书的有效期，我这里选择的是一年，以天为单位。
这个时候，我们的证书原文件 server.csr 签名完成，并生成了一个 server.crt ，新的经过签名的证书文件。

```shell
cd ../
mv ./cert /etc/cert
```
接下来，我们把 `cert` 文件夹移动到 `/etc` 下……

```shell
vim /etc/config/uhttpd
```
编辑 uHTTPd 的配置文件，并把
```
        option cert '/etc/uhttpd.crt'
        option key '/etc/uhttpd.key'
```
改成
```
        option cert '/etc/cert/server.crt'
        option key '/etc/cert/server.key'
```
并保存。

```shell
/etc/init.d/uhttpd restart
```
最后，重启 uHTTPd ，看看效果吧！

![ERROR_CONNECTION_NOT_PRIVATE](https://ooo.0o0.ooo/2017/06/05/5935172200e5e.png)

**真(sang)是(xin)悲(bing)伤(kuang)**
好吧，这也就是我们想要的效果……
~~管他娘的私密不私密~~
在这里也要提醒一句， **自己签名的证书 100% 会报不安全** ，这也是无可避免的。当然，我本人也没有尝试过带私钥密码的证书连接，所以这个 100% 也有可能不靠谱。
***

#### References:
1. https://wiki.openwrt.org/doc/uci/uhttpd
2. http://www.huangcheng.name/read.php?156

***

**EoF.**