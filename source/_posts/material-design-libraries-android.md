---
title: 这些库，推进了 Material Design 的普及 - Android
date: 2017-06-20 21:41:14
tags: [Material Design, Android]
---

Material Design 自 2014 年在 I/O 大会上与 Android Lollipop 一同发布以来，如今已经经历过三个春秋了。其以简洁的整体设计，质感与扁平相结合的风格，以及在平面设备上创新地进行 3D 变换（引入 Z 轴），对统一各平台用户体验作出了巨大的贡献。

在 Android 端，为了使应用 Material Design 化更加便捷，各种库更是层出不穷。从 Google 的官方支持，到对 Material Design 的全面覆盖；从小小的状态栏，到一整个 RecyclerView ……这些库，推进了 Material Design 的普及。

我不愿列出一张冗长的清单，我也不愿只是单纯地介绍我的使用经历，我将从易用性、 UI 和推荐度这三方面，详细地叙述我所想到的一切。

<!-- more -->

## [Android Design Support Library](https://developer.android.com/training/material/design-library.html) - Google

易用性：★★★★

Google 官方的 Android Design Support Library （以下简称 ADSL ）是现在，仅论集成，最好用的 Library 。 Android Studio 对于 ADSL 的支持十分完善，新建工程时会自动导入， Android Studio 安装 SDK 时默认安装了 ADSL ，而且 ADSL 中所包含的大部分控件操作都比较简便。

然而如果有人说 ADSL 的易用性能够打满分，我绝对不敢苟同。虽然从第一个版本推出到现在已经过了两年， ADSL 的 bug 仍然不少。更糟糕的是，因为 Google 搜索得到的教程所使用的 ADSL 版本参差不齐，许多人也没有看更新记录的习惯，导致要么很多当前版本出现的 bug 没法解决，要么曾经出现而当前版本已经解决的 bug 被重新解决一遍影响代码可读性…… ADSL 的使用，还是乖乖地看官方文档吧。

UI：★★★★★

作为 Google 官方的支持库， ADSL 当然会完全按照 Material Design 来设计，配合 Google 的其它 V7 库可以使应用完全地装备好 Material Design 后对外发布，塑造超赞的 Material Design 体验（只要开发者按照 Material Design Guidelines 来）。

推荐度：★★★★★

## [Material Design Android Library](https://github.com/navasmdc/MaterialDesignLibrary) - Ivan Navas

易用性：★★★★☆

虽然是第三方库， Material Design Android Library （ MDAL ）的易用性不输 ADSL ，甚至在 ADSL 之上。引入同 ADSL 一样简单，甚至不需要额外的 AppCompat V7 ，在 ADSL 完善之前， MDAL 是一柄锋利的剑。对于应用体积的减小以及对代码更高度的控制， MDAL 完全能够胜任。

UI：★★★

然而 MDAL 的 UI ， **十分糟糕** 形容起来也不过分。滥用的波纹效果，不合理的间距、按钮大小，与 Material Design Guidelines 相悖的部分控件，奇怪的动画……除非 ADSL 真的无法完成需求，否则，对 MDAL 还是持保守态度吧。

推荐度：★★★

## [Material Ripple Layout](https://github.com/balysv/material-ripple) - Balys Valentukevicius

易用性：★★★★★

Material Ripple Layout （ MRL ）的使用非常方便，到了「写一行代码就能用」的地步。实际使用起来确实是这样。虽然 MRL Balys 只支持到 API 14 ，但是他同时也给出了向下兼容到 API 9 的方法。对于需要将应用做得大部分设备都可使用而又追求波纹效果的开发者而言， MRL 是他们的不二选择。

同 Robin Chutaux 的 [RippleEffect](https://github.com/traex/RippleEffect) 相比，虽然 RippleEffect 有更高的知名度和更高的人气，其易用性真的不怎么样。 MRL 虽然和 RippleEffect 相同，都要求开发者对波纹效果布局设置点击事件，但是如果点击事件设置到子控件， MRL 会延迟点击事件的触发以使波纹效果完全展示，而 RippleEffect 不会。也就是说，如果需要在一个已完成的工程上加入波纹效果， RippleEffect 未免太麻烦。

UI：★★★★☆

MRL 非常不错，它给了开发者将几乎与 L+ 完全相同的波纹效果一路兼容到 Android 2.3 的机会，可是， MRL 在一些动画的处理上略有延迟，而且若要兼容到 Android 2.3 就势必要放弃在列表中保证不会被滑动触发的措施。虽然其大体值得满分，细节上却是让人不很满意。

推荐度：★★★★☆

## [MaterialEditText](https://github.com/rengwuxian/MaterialEditText) - Kai Zhu

易用性：★★★☆

发布到公开仓库的 MaterialEditText （ MET ），曾经十分知名，在 ADSL 推出 TextInputLayout 前一度是许多开发者的首选，它的易用性却比起 TextInputLayout 稍逊一筹。 ADSL 因为需要和 AppCompat V7 联动，可以直接获取主题中所设置的 accent color ，而 MET 只能指定。除开 AppCompat V7 的部分， TextInputLayout 会直接使用内部 EditText 的 hint 作为浮动标签， MET 则必须手动指定。再加上 MET 设置项过于繁杂，虽然在一些时候这有优势，但是大部分时候繁杂的设置只会给使用带来麻烦的问题。

UI：★★★★★

MET 的设计就像 Google 自家的一样，和 ADSL 的 TextInputLayout 不相上下。简洁、美观且符合 Material Design Guidelines 的要求，大概是 MET 在 ADSL 祭出杀器前火爆的重要原因。

推荐度：★★★★

## [CircularAnim](https://github.com/XunMengWinter/CircularAnim) - XunMengWinter

易用性：★★★★★

CircularAnim （ CA ）具有值得打满分的易用性，使用起来非常简单。无论是多么复杂的动画以及交互，只需要一行代码就可以全部搞定。而且， CA 支持使用图片作波纹效果，同样也是 **一行代码的事儿** 。

UI：★★★★★

CA 的 UI 非常不错，我曾经在一个项目中试用了 CA ，结果使人满意。如果项目必须兼容 Android 5.0 以下设备而需要用到 Reveal Effect ，那么就选择 CA 吧，无须赘言。只要在 GitHub 上面看一看效果图， CA 就必然能俘获所有犹豫不定的心。这是我唯一一个肯打全五星的库。

推荐度：★★★★★

> _TO BE CONTINUED..._