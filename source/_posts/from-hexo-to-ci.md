---
title: 用 Travis CI 配合 Hexo ，快速入门持续集成
date: 2019-04-05 00:43:09
tags: [Hexo,Travis,持续集成]
---

此前，我们曾在 [这篇文章](https://blog.stfw.info/hexo-completely-tutorial/) 中探讨过使用 Hexo 和 Git 实现 VPS 上博客更新的方法，而对于搭建在 GitHub Pages 上的博客，尤其是各位正在阅读的文章所属的、将源代码丢在 GitHub 上的，每次都手动先 `deploy` 到 `gh-pages` 再把程序 `push` 上去……各位感觉如何咱不知道，但是咱肯定坚持不下去，这肯定不是什么省心省力的好办法。

好在，「持续集成 (Continuous Integration) 」给了我们一个可行性相当高的方法。点一下，玩一年，开源项目不收一分钱的 [Travis CI](https://travis-ci.org) （下称 "Travis" ），因其方便性与高可扩展性，自然就成为了我们的首选。当然，本文所提只是 CI 相当浅显的一种用法， Travis 与 GitHub 结合还能够实现自动发布新的 snapshot 、集成多个项目一起进行编译测试等等操作，只要能本地完成的工作几乎都可以交给 Travis 。
<!-- more -->
> 对于已经在使用 Travis 的开源项目转为私有或是想在私有项目中使用 Travis 的用户，其也提供了 [付费版](https://travis-ci.com) 。

### 0x00 注册 Travis

Travis 的注册十分简单，只需要使用 GitHub 帐号登入即可，在此不多赘述。

### 0x01 部署

为了开始在 repo 中使用 Travis ，我们首先需要在 Travis 的后台启用目标 repo 。随后，  Travis 将开始监听这个 repo 的所有新 commit 。但这还不够，如果我们不使用一个默认放在其根目录下，名为 `.travis.yml` 的配置文件对编译过程进行控制，那么即使收到了 commit 也不会 trigger 这个 commit 的 build job 。幸运的是， `.travis.yml` 非常简单易懂好配置，以下给出了来自本博客的一个示范：

```yaml
language: node_js
node_js: "node"
cache: npm

branches:
  except:
  - dev

before_script:
  - npm install -g hexo
  - npm install

script:
  - hexo g
  - mkdir ./public-git
  - cd ./public-git
  - git init
  - git config --global push.default matching
  - git config --global user.email "${GitHubEMail}"
  - git config --global user.name "${GitHubUser}"
  - git remote add origin https://${GitHubKEY}@github.com/${GitHubUser}/Rachel-s-Blog.git
  - git pull origin gh-pages
  - rm -rf ./*
  - cp -rf ../public/* ./
  - git stage --all .
  - git commit -m "Travis CI Auto Builder"
  - git push --quiet --force origin HEAD:gh-pages
```

不难看出，除开前面一部分对环境的定义，后面几乎都是各位熟得不能再熟的 shell 脚本，而与真正的 shell 脚本不同的一点，就只有执行的地方位于 Travis 的服务器，而不是本机。

> 这个说法不算对。 Travis 还对脚本的运行时间等等做了一大堆限制，但是这篇文章内所谈到的内容几乎不可能触及这些限制。只要不是想在 Travis 的服务器上搭一个梯子，想必要被 Travis 强行关 build job 的情况应该还是很少见的。

~~考虑到各位已具备的相当基础，本文写到这里大可搁笔，大家再见（才不是 Rachel 懒了 哼唧）。~~

刚刚是什么东西在咕咕？总之，既然要定制自己的编译流程，就请各位继续向下阅读。

### 0x02 配置

我们回到刚刚给出的，本博客的 `.travis.yml` 。

```yaml
language: node_js
node_js: "node"
cache: npm
...
```

这几句定义了 build job 需要的环境。既然我们使用的是 Hexo ，那么自然就是 Node.js 。第二行是 Node.js 使用的版本，如果是 `node` ，编译过程将在最新的稳定版 Node.js 环境上执行。如果有特殊需求，可以将 `node` 修改为可被 `nvm` 安装的目标版本号。如果目标版本无法被安装，那么 build job 将被终止并且报错。 [文档原文](https://docs.travis-ci.com/user/languages/javascript-with-nodejs/) ：

> If you need more specific control of Node.js versions in your build, use any version installable by `nvm`. If your `.travis.yml` contains a version of Node.js that `nvm` cannot install, such as `0.4`, the job errors immediately.

如果有其它语言的需求，也可以查阅 [官方文档](https://docs.travis-ci.com/user/languages/) 。没有的话， Travis 也提供了 [添加语言](https://docs.travis-ci.com/user/languages/community-supported-languages/) 的入口，可以选择自己为这门语言提供支持。

```yaml
...
branches:
  except:
  - dev
...
```

我们不需要 trigger Travis 的 branch ，就在这里被列了出来。通常如果没有频繁对主题等大修大改，这一段大可以删除。为了方便折腾，可以像这样添加一个 `dev` branch ，防止乱七八糟的临时改动参与 `master` 的编译。默认情况下 `gh-pages` 会自动算进去，如果需要加入编译，或者将黑名单改为只编译一部分 branch 的白名单，将 `except` 改成 `only` 即可。

```yaml
...
before_script:
  - npm install -g hexo

script:
  - hexo g
  - mkdir ./public-git
  - cd ./public-git
  - git init
  - git config --global push.default matching
  - git config --global user.email "${GitHubEmail}"
  - git config --global user.name "${GitHubUser}"
  - git remote add origin https://${GitHubKEY}@github.com/${GitHubUser}/Rachel-s-Blog.git
  - git pull origin gh-pages
  - rm -rf ./*
  - cp -rf ../public/* ./
  - git stage --all .
  - git commit -m "Travis CI Auto Builder"
  - git push --quiet --force origin HEAD:gh-pages
```

就像一些卡牌游戏一个回合分很多个阶段一样， build job 也有很多个编译阶段，称为它的「生命周期 (job lifecycle) 」。一个生命周期分为 `install` 和 `script` 两个阶段，前者用来搭建环境，后者用来执行任务。同样地，这两个阶段前后（除了 `install` 后，那等价于 `script` 前）均可以手动执行一些任务。这些任务都是一个一个 shell 脚本。具体的编译流程，参见生命周期的 [官方文档](https://docs.travis-ci.com/user/job-lifecycle/) 。 `before_script` 中不需要添加 `npm install` ，因为那已经在 `install` 中被执行。本博客的部署与 `script` 中的命令有关。

首先， Hexo 被调用以生成所有的静态文件。然后，我们新建了一个文件夹，在这个文件夹中把 remote origin 源设置为了本博客的对应网址，将文件全部扒下来再删掉以确保 `git` 正常运行。最后， Hexo generate 的文件被复制进来，并被 push 到 `gh-pages` 。这样，一次完整的更新就完成了。

正如各位所见， Travis 支持环境变量的设置，并且可以选择在输出日志中隐藏（因为 Travis 的编译日志是可以随便看的）以确保安全。若要设置环境变量，直接到 Travis 里的 repo 首页，在设置页面里输入即可。

而为了方便 Travis 这类自动任务、防止密码被泄露， GitHub 提供了 personal access tokens 用来授权，每个 token 都能独立控制所能访问的内容，在 GitHub 账户设置里的 developer settings 可以找到。

### 0x03 然后…

马上运行：

```shell
git stage .
git commit
git push
```

并打开 Travis repo 页，看着 Travis 完成这一切吧！

> 其实对于部署到 GitHub Pages ， Travis 也提供了一种简便的方法：通过 Travis 内置的 deploy 实现。 [官方文档](https://docs.travis-ci.com/user/deployment/pages/) 中对其进行了描述，同样需要使用 personal access token 。虽然那样很方便，但是毕竟还是不能做到手写 `git` 命令这样高的可控性。如果各位对 Travis 足够放心，或者对各位记忆 push 步骤没信心，那么 Travis 提供的方案无疑是理想选择。

***

**EoF.**

#### References:

1. [https://blog.nfz.moe/archives/hexo-auto-deploy-with-travis-ci.html](https://blog.nfz.moe/archives/hexo-auto-deploy-with-travis-ci.html)
2. [https://docs.travis-ci.com](https://docs.travis-ci.com)
3. [https://github.com/settings/tokens](https://github.com/settings/tokens)
