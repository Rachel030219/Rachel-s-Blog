---
title: 手把手教你搭建 Hexo 到 VPS
date: 2017-04-29 19:56:42
tags: [Hexo, VPS]
---

> *Hexo* is a fast, simple & powerful blog framework powered by Node.js.
> ——摘自 [Hexo 官网](https://hexo.io)

Hexo 是一个强大的静态 Blog 框架，它具有极高的可扩展性，同时入门也十分简单，像是正在阅读的这篇文章，本身也就是 Hexo 托管，我每次写完文章甚至只需要输入一行代码就可以将其推送到服务器上。由于使用静态文件搭建主体， Blog 的启动尤其迅速，
~~只要不像本咸鱼一样写垃圾代码~~
一般可以在 500ms 内加载完毕。
~~坏 WordPress 坏 Typecho~~

> 鉴于网络上能够找到的大部分中文快速入门质量参差不齐，有些逻辑混乱有些表意不清，本咸鱼就自己来写一个辣

说了这么多，快跟着下面的操作步骤，
~~入教~~
开始使用吧！
<!-- more -->
***
### 0x00 基本要求
**0. PC**
Windows, Linux, macOS 随便选一个吧，能跑得动 Git 和 Node.js 就行，本文以 Windows 10 为例。
**1. VPS**
这一点就只能看个人喜好啰，像我这种咸鱼买的是 Vultr 的 $5 主机。
~~有 $2.5 乞丐机的话谁买 $5~~

> 如果自己要买的话，戳这个链接然后充值 $10+ 可以给 Rachel 带来  $10 收益！
> ~~反正都是要买的不如多花点钱是吧~~
> [Vultr 邀请链接](http://www.vultr.com/?ref=7148744)

### 0x01 本地 - 搭建 Git 和 Node.js 环境
我们需要一个 Git 客户端，用来在 Windows 上使用 Git 命令行。
[Git - Downloads](https://git-scm.com/downloads)
或者，如果是在 Linux 上的话，也可以使用包管理器来安装 `git` 包。
在 Git 配置完之后，紧接着我们就需要装 Node.js ， Hexo 的基础，一个轻量的 JavaScript 运行时。
[Node.js - Downloads](https://nodejs.org/en/download)
当然，你也可以用包管理器 install `nodejs` 。
一切完成之后，进入下一步。
### 0x02 本地 - 使用 Node.js 安装 Hexo
我们需要随便找个地方开启 Terminal (Git Bash) ，然后进入想要安装 Hexo 的那个文件夹。当然，也可以选择在建好文件夹之后右键 Git Bash Here 。
总之，在进入文件夹之后，我们需要
```sh
npm install hexo-cli -g
```
在安装完成后，新建 Hexo 仓库
```sh
hexo init
```
直到你看见
```
INFO  Start blogging with Hexo!
```
说明 Hexo 已经配置完毕，下一步
```sh
npm install
```
完成之后， Hexo 文件夹下面大概是这样的结构
```
.
├── _config.yml
├── package.json
├── scaffolds
├── source
|   ├── _drafts
|   └── _posts
└── themes
```
接着，我们输入
```sh
vim _config.yml
```
开始编辑 Hexo 的配置，或者使用 Notepad++ 等工具编辑而不用对初学者来说狗屎一样的命令行。请务必记住，在 YAML 文件中， **冒号后面有空格** 。
```yaml
…
# Site
title: Hexo               # 页面标题
subtitle: Subtitle        # 子标题
description: Here we go!  # 页面描述，在一些主题中可以省略
author: John Doe          # 作者
language: zh              # 语言，依主题而定
timezone: Asia/Shanghai   # 时区
…
```
```yaml
…
# URL
## If your site is put in a subdirectory, set url as 'http://yoursite.com/child' and root as '/child/'
url: http://yoursite.com               # 域名
root: /                                # 在域名中的文件夹，如果不是主/子域名的话就需要填这项
…
```
完成之后，保存并退出，运行 Hexo 看看效果
```sh
hexo g && hexo s
```
这个时候，访问 http://localhost:4000 如果出现了 Hexo 页面，说明已经配置成功了，去终端 Ctrl + C 停止然后继续下一步吧。
### 0x03 VPS - 安装 `git-core` 和 `nginx`
在 VPS 端，使用包管理器安装 `git-core` 和 `nginx` 。之后，在用户的主目录新建一个空的 Git 仓库。
```sh
cd ~
mkdir hexo.git
cd hexo.git
git init --bare
```
以 root 用户的身份进入 `/var/www` ，然后新建一个文件夹，就名为 `blog` 好了，最后授予 user 这个用户完整的权限。
```sh
su
cd /var/www
mkdir blog
chmod 0755 blog
chown user:user -R /var/www/blog
```
### 0x04 本地 (可选) - 建立到 VPS 的链接

> 本步骤为可选，若 VPS 没有修改默认的端口并且没有使用 SSH Key ，或者已经有了远程 SSH 服务器，请跳过这一步。

首先，我们需要在本地用户的目录下，建立一个 `.ssh` 文件夹，然后向里面写入 `config` 。
```sh
cd ~
mkdir .ssh
chmod 0755 .ssh
vim .ssh/config
```
在里面输入如下内容：
```
Host 127.0.0.1             # VPS 的 IP
HostName 127.0.0.1         # VPS 的 IP
User user                  # 用户
Port 1270                  # SSH 端口
IdentityFile ~/.ssh/id_rsa # SSH Key
```
然后，重启 Git Bash ，试试看下面的代码能否正常运行
```sh
ssh user@127.0.0.1
```
若输入密码后能够进入终端页面，请进入下一步。
### 0x05 VPS - 配置更新事件 (hook)

> 这里的更新事件，指的是 Git hooks 中的 post-receive ，在我们向 VPS 推送更新的时候会被作为一个 sh 文件触发，因而语法与 sh 相同。

使用 `ssh` 命令登陆上 VPS 之后，输入如下命令
```sh
vim ~/hexo.git/hooks/post-receive
```
再将文件内容替换为
```sh
!/bin/bash

GIT_REPO=~/hexo.git                      # 空 Git 仓库的文件夹，触发 hook 时已经存入了内容
TMP_GIT_CLONE=/tmp/hexo                  # 缓存文件夹，存在 /tmp 下可以随意读写
PUBLIC_WWW=/var/www/blog                 # 之前创建的 blog 文件夹，用作网站主目录
rm -rf ${TMP_GIT_CLONE}                  # 删除缓存的全部内容
git clone $GIT_REPO $TMP_GIT_CLONE       # 将 Git 仓库被上传的内容写入缓存
rm -rf ${PUBLIC_WWW}/*                   # 删除网站主目录全部内容
cp -rf ${TMP_GIT_CLONE}/* ${PUBLIC_WWW}  # 将缓存目录所有内容复制到主目录
```
### 0x06 VPS - 配置 NGINX

> NGINX 是一个功能强大的 HTTP 反向代理服务器，支持负载均衡等等特性，
> ~~当然这篇文章不会讲~~
> ~~而且语法特别垃圾~~
> 是现在搭建 Web Server 的首选。

切换到 root 用户，进入到 NGINX 的配置目录，编辑默认配置文件
```sh
su
cd /etc/nginx/sites-available
vim default
```
在这个文件中，你可以看到 NGINX 默认的配置，我们则需要把这个默认的配置全部删掉改成自己的。
~~正所谓 把别人做的巧克力融化了再凝固 就是自己做的巧克力了~~
```nginx
server {
        listen 80;
        listen [::]:80;
        # ====== 1 ======
        server_name yoursite.com;
        # ====== 1 ======
        return 301 https://$server_name$request_uri;
}
server {
        # SSL configuration

        listen 443 ssl;
        listen [::]:443 ssl;

        # Self signed certs generated by the ssl-cert package
        # Don't use them in a production server!
        #
        # include snippets/snakeoil.conf;

        # ====== 2 ======
        root /var/www/blog;
        # ====== 2 ======

        # ====== 3 ======
        ssl_certificate /etc/letsencrypt/live/yoursite.com/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/yoursite.com/privkey.pem;
        # ====== 3 ======

        ssl_session_timeout 1d;
        ssl_session_cache shared:SSL:50m;
        ssl_session_tickets off;

        # intermediate configuration. tweak to your needs.
        ssl_protocols TLSv1 TLSv1.1 TLSv1.2;

        # HSTS (ngx_http_headers_module is required) (15768000 seconds = 6 months)
        add_header Strict-Transport-Security max-age=15768000;

        # OCSP Stapling ---
        # fetch OCSP records from URL in ssl_certificate and cache them
        ssl_stapling on;
        ssl_stapling_verify on;
  
        # Add index.php to the list if you are using PHP
        index index.html index.htm index.nginx-debian.html;

        # ====== 1 ======
        server_name yoursite.com;
        # ====== 1 ======

        location ~* ^.+\.(ico|gif|jpg|jpeg|png)$ {
                # ====== 2 ======
                root /var/www/blog;
                # ====== 2 ======
                access_log   off;
                expires      1d;
        }
        location ~* ^.+\.(css|js|txt|xml|swf|wav)$ {
                # ====== 2 ======
                root /var/www/blog;
                # ====== 2 ======
                access_log   off;
                expires      10m;
        }
        location / {
                # ====== 2 ======
                root /var/www/blog;
                # ====== 2 ======
                if (-f $request_filename) {
                        rewrite ^/(.*)$  /$1 break;
                }
        }
}
```

> 注：
> 1: 域名
> 2: 网页主目录，就是之前创建的 blog 文件夹
> 3: 你的 SSL 证书和 SSL key
> 又及：如果有能力，推荐使用 Mozilla 的 [SSL 配置生成器](https://mozilla.github.io/server-side-tls/ssl-config-generator)

如果没有 SSL 证书或者不愿开 https ，以下是 http 的配置方案：
```nginx
server {
        listen 80;
        listen [::]:80;

        # Self signed certs generated by the ssl-cert package
        # Don't use them in a production server!
        #
        # include snippets/snakeoil.conf;

        # ====== 2 ======
        root /var/www/blog;
        # ====== 2 ======

        # Add index.php to the list if you are using PHP
        index index.html index.htm index.nginx-debian.html;

        # ====== 1 ======
        server_name yoursite.com;
        # ====== 1 ======

        location ~* ^.+\.(ico|gif|jpg|jpeg|png)$ {
                # ====== 2 ======
                root /var/www/blog;
                # ====== 2 ======
                access_log   off;
                expires      1d;
        }
        location ~* ^.+\.(css|js|txt|xml|swf|wav)$ {
                # ====== 2 ======
                root /var/www/blog;
                # ====== 2 ======
                access_log   off;
                expires      10m;
        }
        location / {
                # ====== 2 ======
                root /var/www/blog;
                # ====== 2 ======
                if (-f $request_filename) {
                        rewrite ^/(.*)$  /$1 break;
                }
        }
}
```
完成之后，保存退出，重启 NGINX 。
```sh
/etc/init.d/nginx restart
```
### 0x07 本地 - Hexo deploy 设置
是的，转了这么一大圈我们又回到了开始时的 `_config.yml` 。这一次，我们改动的不是那个页面设置，而是 Hexo 的上传配置。
不过，在开始改动之前，我们先要安装一个用于 Git 上传的模块： `hexo-deployer-git` 。
```sh
npm install hexo-deployer-git --save
```
完成之后，进入 `_config.yml` 的编辑。
```yaml
…
deploy:
  type: git                      # 设置上传模块为 Git
  repo: user@127.0.0.1:hexo.git  # 连接到 127.0.0.1 （换成 VPS 的 IP），使用 user 用户登录，上传到 hexo.git
  branch: master                 # 存储在 master 分支（主分支）
…
```
保存，退出，然后再次进入 Git Bash ，向半个小时的劳动做一个总结。
### 0x08 本地 - 上传！
同样在我们可爱的 Hexo 本地安装文件夹，输入
```sh
hexo clean && hexo g
```
这样，清除缓存文件后，生成静态页面，然后
```sh
hexo s
```
进入 http://localhost:4000 ，最后看一眼预览。当确保一切无误……
```sh
hexo d
```
输入密码……
当完成后，打开你的网页吧！
### 0x09 完成之后
Hexo 的基本使用非常简单，只需要 `hexo new "New Post"` 就能新建一篇文章，写完之后 `hexo clean && hexo g` 再 `hexo d` 上传，期间可以 `hexo s --debug` 测试。想要使用主题的话，只需把主题文件夹丢到 Hexo 本地文件夹的 `themes` 然后在 `_config.yml` 里 `theme: ` 后面改成主题就可以了。若有任何问题，请随时在下方评论区提出。
***
References:

1. https://munen.cc/tech/Hexo-in-VPS.html
2. https://hexo.io/docs/setup.html
3. https://hexo.io/docs/deployment.html
4. https://www.digitalocean.com/community/tutorials/how-to-create-a-blog-with-hexo-on-ubuntu-14-04

Thanks to:

1. kotomei
2. neoFelhz
3. LetITFly
4. Simonsmh
5. **AND YOU**

> 注：排名不分先后。

***

EOF.