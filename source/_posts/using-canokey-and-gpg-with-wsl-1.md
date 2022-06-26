---
title: 优雅地在 WSL 1 上使用 CanoKey 进行 PGP 认证
date: 2022-06-26 17:38:25
tags: [PGP, CanoKey, Windows, YubiKey]
---

六月初，苦苦等待许久的 CanoKey Pigeon 终于上线第二批，拿到之后，我非常兴奋地用它绑定了一大堆常用网站的 <ruby><rb>两步验证</rb><rt>2 Factor Authorization (2FA)</rt></ruby> ，折腾半天后发现一个问题：如果对 OpenPGP 和 PIV 没有需求，仅仅把它作为 2FA 工具使用，我好像还不如直接用 Apple Watch 上的 Authy 来得安全、方便。

而且我有很多个理由拒绝 OpenPGP / PIV。两者在不同平台上需要各种配置，至少对于坚定的 Windows + WSL 用户如此；文件形式密钥备份起来非常不方便，尤其是出于安全性考虑，还有多介质备份 + 脱机条件一次性操作 + 主密钥、三个子密钥、撤销凭证备份、有效期、使用方法不同等等要求；各种操作都需要不同长度、不同作用的 PIN，我能记住超过三个 PIN 就很不错了，可能对于许多用户，需要的密码越多，越可能使用雷同密码或弱密码；最重要的是无法保证跨平台可用性，万一某一天出门在外突然有认证需求，却只有 iOS 设备，那直接完蛋；比起记住一次到处通用，数据、设备全部丢失也不会掉的密码（体系），实在是脆弱、复杂太多。

但当我百无聊赖坐在电脑前，望向放在桌上吃了两周灰的 CanoKey，我又感觉可以试试看。就算不把它作为主要认证方式，至少玩玩看嘛。于是，在我花费大半个上午生成 key，再将 Windows 的 `gpg-agent` 塞进不支持访问 USB 设备更别说 CanoKey 的 WSL 1 之后，我写下这篇文章作为记录，以便此后能随时回顾，希望能帮助到同样有需求的人。

> **⚠注意⚠** ：本文记录的方法仅推荐在可信系统上使用。任何情况下，跨系统共用私钥的行为都具有较大的安全隐患。若您有强烈的安全性需求，请您关闭本文，不考虑在 WSL 中使用 CanoKey，并 / 或安装一个单独的 Linux 系统。

## 生成密钥

关于如何将 CanoKey 变成存储密钥的智能卡，已经有许多资料，本文不再赘述。我参照是 Editst 大佬的 [Canokey 指南：FIDO2，PGP 与 PIV](https://editst.com/2022/canokey-guide/) ，在 Windows 中安装好 [Gpg4win](https://gpg4win.org/download.html) 和 [win-gpg-agent](https://github.com/rupor-github/win-gpg-agent) ，将三个子密钥写入了 CanoKey。对 OpenPGP 还有疑问的话，也可以参考 UlyC 的 [2021年，用更现代的方法使用PGP](https://ulyc.github.io/2021/01/13/2021%E5%B9%B4-%E7%94%A8%E6%9B%B4%E7%8E%B0%E4%BB%A3%E7%9A%84%E6%96%B9%E6%B3%95%E4%BD%BF%E7%94%A8PGP-%E4%B8%8A/) 系列教程。

继续前，请确认在 Windows 的 PowerShell 中输入 `gpg --card-status` 能够正常输出 CanoKey 中存储的，用于签名、加密和认证的三个 key、指纹及 ID。

## SSH in WSL 1

启动 `agent-gui.exe` 后，在 PowerShell 中，输入 `ssh-add -L` ，应当能够看到如图所示的信息：

```powershell
PS C:\Users\Rachel> ssh-add -L
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIP5ZT7970edpOEIoZTR7JaPdHNNKxmHG4qrHnz68BzSg cardno:F1D0 XXXXXXXX
```

输出的这一行是 CanoKey 中 OpenPGP 附带的 SSH 公钥，如 [Canokey 指南：FIDO2，PGP 与 PIV](https://editst.com/2022/canokey-guide/) 中所说，将其塞进服务器、GitHub 之类的地方，每当调用对应的私钥时，输入 PIN、触摸 CanoKey（如果启用了 [CanoKey Management Tool](https://console.canokeys.org) 中 OpenPGP 的 Touch Policies）即可授权 SSH 访问。

这是在 Windows 下。WSL 1 倒也大差不差，只需将 SSH 的认证交给 `agent-gui.exe` 提供的 socket 即可：

首先确保 WSL 1 中存在 SSH，一般都有，没有的话 `sudo apt update && sudo apt install openssh-client` （以 Debian 系为例）也能解决问题。

打开 Windows 托盘栏中的 `agent-gui` 的 Status，里面应该有一个 agent-gui AF_UNIX and Cygwin sockets directory ，它下面的文件夹，通常是 `%LocalAppData%\gnupg\agent-gui` ，有数个不同用途的 `gpg-agent` ，其中 `S.gpg-agent.ssh` 即为我们要找的 `SSH_AUTH_SOCK` 。在我的例子中，我的用户名为 `Rachel` ，`%LocalAppData%\gnupg\agent-gui\S.gpg-agent.ssh` 对应的文件是 `C:\Users\Rachel\AppData\Local\gnupg\agent-gui\S.gpg-agent.ssh` ，转换到 WSL 下就是 `/mnt/c/Users/Rachel/AppData/Local/gnupg/agent-gui/S.gpg-agent.ssh` 。试试看吧！

```bash
$ export SSH_AUTH_SOCK=/mnt/c/Users/Rachel/AppData/Local/gnupg/agent-gui/S.gpg-agent.ssh
$ ssh-add -L
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIP5ZT7970edpOEIoZTR7JaPdHNNKxmHG4qrHnz68BzSg cardno:F1D0 XXXXXXXX
```

 输出的公钥与 Windows 下一致，说明没有问题。现在，如果已经将这个公钥添加到 GitHub 的公钥库，可以试试看：

```bash
$ ssh -T git@github.com
Hi Rachel! You've successfully authenticated, but GitHub does not provide shell access.
```

一切 OK。

## GnuPG in WSL 1

相比 SSH，GPG 的配置有亿点点坑。

### 那你能帮帮我吗？

相比 `openssh` ， `gnupg` 和 `socat` 不一定安装在所有系统中，所以我们先确定他俩都在： `sudo apt update && sudo apt install gnupg socat` （以 Debian 系为例）。

GnuPG 无需多言， `socat` 是一个 Linux 下的多用途中继工具，可以连接到文件、设备、pipe、socket 等，我们需要使用它监听对 WSL 下 `S.gpg-agent` 的访问，并转发至 `agent-gui` 提供的 `S.gpg-agent` ：

```bash
$ [ -f "/home/rachel/.gnupg/S.gpg-agent" ] && echo "Deleting old GPG agent.." && rm "/home/rachel/.gnupg/S.gpg-agent" || [ -d "/home/rachel/.gnupg" ] || mkdir /home/rachel/.gnupg && chmod 700 /home/rachel/.gnupg
$ socat UNIX-LISTEN:/home/rachel/.gnupg/S.gpg-agent,fork UNIX-CONNECT:/mnt/c/Users/Rachel/AppData/Local/gnupg/agent-gui/S.gpg-agent &
```

这两句命令，第一句是检测用户目录下是否存在 GnuPG 生成的 `S.gpg-agent` ，若有则将其删除（否则 `socat` 无法创建自己的监听），否则检测是否有 GnuPG 目录，没有则创建 + 设置对应权限。

第二句是使用 `socat` 开始监听 Linux 下 GnuPG 自动生成的 `S.gpg-agent` ， `fork` 是监听多次访问，然后 `UNIX-CONNECT` 转发至 `agent-gui` 创建的 `S.gpg-agent` 。行末的 `&` 将 `socat` 放入子线程中异步运行，防止阻塞当前 shell。

此时，在 WSL 1 中调用 `gpg` 看看吧：

``` bash
$ gpg --card-status

Reader ...........: canokeys.org OpenPGP PIV OATH 0
（省略一长串 CanoKey 信息）
```

成功！不过我们只是读取了 CanoKey，还没有导入密钥，如果现在 `git commit -S` ，很可能会提示

```bash
$ git commit -S
error: gpg failed to sign the data
fatal: failed to write commit object
```

要解决也很简单，跟着 [Canokey 指南：FIDO2，PGP 与 PIV](https://editst.com/2022/canokey-guide/) 来，我们更新本地的密钥库，首先导入公钥：

```bash
$ gpg --import public-key.pub
gpg: key XXXXXXXXXXXXXXXX: public key "Rachel T <13704467+Rachel030219@users.noreply.github.com>" imported
```

从 CanoKey 导入私钥：

```bash
$ gpg --edit-card

Reader ...........: canokeys.org OpenPGP PIV OATH 0
（省略一长串 CanoKey 信息）

gpg/card> fetch

gpg/card> q
```

接下来，我们使用 `gpg --fingerprint --keyid-format long -K` 查看签名 key 的 ID：

```bash
$ gpg --fingerprint --keyid-format long -K
/home/rachel/.gnupg/pubring.kbx
-------------------------------
sec#  ed25519/XXXXXXXXXXXXXXXX 2022-06-26 [C]
      Key fingerprint = (主密钥指纹)
uid                 [ unknown] Rachel T <13704467+Rachel030219@users.noreply.github.com>
ssb>  cv25519/EEEEEEEEEEEEEEEE 2022-06-26 [E]
ssb>  ed25519/AAAAAAAAAAAAAAAA 2022-06-26 [A]
ssb>  ed25519/SSSSSSSSSSSSSSSS 2022-06-26 [S]
```

`[S]` 前 `ed25519/` 后的十六个字符是签名 key 的 ID，将它设置为 `git` 的签名 key，再 `git commit -S` 看看：

```bash
$ git config --global user.signingkey SSSSSSSSSSSSSSSS
$ git commit -S
```

现在应该没有问题了。

### 这么简单，有什么坑？

首先，由于我英语及 Linux 水平糟糕，可能没能正确意会 [win-gpg-agent 的 GitHub README](https://github.com/rupor-github/win-gpg-agent) ，但一开始不会 `socat` 的我，确实没有找到一个 WSL 1 能直接用的办法，只在 `sorelay.exe` 下看到一个给 WSL 2 用的、利用到 `socat` 的 socket 转换，这也是我最终找到办法的来源、写下本文的直接原因。

其次，如 [win-gpg-agent 的 issue #5](https://github.com/rupor-github/win-gpg-agent/issues/5) 所说，理论上可以将 `GNUPGHOME` 设置为指向 `%LocalAppData%` 下的 `gnupg` 文件夹，或者使用软链接 `ln -s` 使 `~/.gnupg` 指向那个 `gnupg` ，但在我的测试中，不仅由于链接及文件系统的限制，始终没能成功修改 `.gnupg` 或 `GNUPGHOME` 文件夹及文件的权限，导致 GnuPG 一直报 WARNING，而且一通操作下来，我也没能使 `gpg --card-status` 正确显示 CanoKey 信息，浪费许多时间。

最后，理论上应当将 WSL 1 下的 `pinentry` 由 `win-gpg-agent` 提供的 `pinentry.exe` 接管，也就是在 `~/.gnupg/gpg-agent.conf` 中加入 `pinentry-program /(win-gpg-agent 的存放路径)/pinentry.exe` ，不过经过测试，即使没有指定 `pinentry` 也没问题，弹出的是 Windows 风格的 PIN 输入框，所以大概问题不大…吧？

## 最后，来点自动

如果以上操作都没有问题，我们可以让一系列操作自动完成。

对于 `agent-gui.exe` ，我们创建一个快捷方式，将快捷方式放到自启动文件夹 `%AppData%\Microsoft\Windows\Start Menu\Programs\Startup` ，每次开机都会自动启动。

然后，我们将 SSH 和 GPG 的配置都加入 WSL shell 的 rc 文件，比如 `.bashrc` 中：

```bash
export SSH_AUTH_SOCK=/mnt/c/Users/Rachel/AppData/Local/gnupg/agent-gui/S.gpg-agent.ssh

[ -f "/home/rachel/.gnupg/S.gpg-agent" ] && echo "Deleting old GPG agent.." && rm "/home/rachel/.gnupg/S.gpg-agent" || [ -d "/home/rachel/.gnupg" ] || mkdir /home/rachel/.gnupg && chmod 700 /home/rachel/.gnupg

socat UNIX-LISTEN:/home/rachel/.gnupg/S.gpg-agent,fork UNIX-CONNECT:/mnt/c/Users/Rachel/AppData/Local/gnupg/agent-gui/S.gpg-agent &
```

复制粘贴时，务必修改上面命令行的用户文件夹。

最后，我们开启 `git commit` 默认 GPG 签名：

```bash
$ git config --global commit.gpgsign true
```

如此，我们完成了 WSL 1 环境下 CanoKey 的 OpenPGP 配置。

***

#### 参考与感谢

除本文内提到的数篇文章外，在撰写本文的过程中，我还得到了以下（及其它可能未及时记录的）内容的帮助，在此一并表示感谢。

[Testing your SSH connection - GitHub](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/testing-your-ssh-connection)

[Getting started with socat, a multipurpose relay tool for Linux | Enable Sysadmin](https://www.redhat.com/sysadmin/getting-started-socat)

[Why is "fork" needed by socat when connecting to a web server?](https://stackoverflow.com/questions/9596594/why-is-fork-needed-by-socat-when-connecting-to-a-web-server)
