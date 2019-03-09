---
title: 从 Travis CI 开始，迈入持续集成的大门
date: 2019-03-10 00:43:09
tags: [Continuous Integration]
---

此前，我们曾在 [这篇文章](https://blog.stfw.info/hexo-completely-tutorial/) 中探讨过使用 Hexo 和 Git 实现 VPS 上博客更新的方法，而对于搭建在 GitHub Pages 上的博客，尤其是各位正在阅读的文章所属的、将源代码丢在 GitHub 上的，每次都手动先 `deploy` 到 `gh-pages` 再把程序 `push` 上去……各位感觉如何咱不知道，但是咱肯定坚持不下去，这肯定不是什么省心省力的好办法。

好在， `持续集成 (Continuous Integration)` 给了我们一个可行性相当高的方法。点一下，玩一年，开源项目不收一分钱的 [Travis CI](https://travis-ci.org) ，因其方便性与高可扩展性，自然就成为了我们的首选。

> 对于已经使用 Travis 进行持续集成的公有项目