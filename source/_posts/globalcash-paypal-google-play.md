---
title: 用 PayPal 拯救你的 GlobalCash ，在 Google Play 完成付款
date: 2017-06-23 11:04:23
tags: [GlobalCash,PayPal,支付,Google]
---

最近 Google 对于 VCC (Virtual Credit Card) 的打击越来越沉重也越来越频繁，同时 EntroPay 对香港签发的 MasterCard 停止了支持，导致 GlobalCash 在 Play 中的付款处于长期用不了的状态。我曾经试着用 PayPal 绑定 GlobalCash 并试着在 Play 中进行付款而结果仍然是被拒绝。经过一番摸索，最后，我终于找到了一种能够绕过 Google Play 复杂检验机制的方法。
<!-- more -->
> 虽然 Google Play 应用无法使用 GlobalCash 支付，但令人意外的是， Google Payments 仍然能用，而且 Google Play 的电影也能购买。如果没有特别需要， **不推荐** 使用本文介绍的方法。

# 用 PayPal 拯救你的 GlobalCash ，在 Google Play 完成付款

## Step 0. 注册一个 PayPal 绑定 GlobalCash
因为我们需要使用 PayPal 中的余额完成付款，所以我们当然需要一个 [PayPal](https://paypal.com) 。

![Screenshot01](https://img.vim-cn.com/37/88d7b1ab50b28db57a6784208cbc6917431cbe.png)

然后，点击右上角的 [**Sign up**](https://www.paypal.com/us/webapps/mpp/account-selection) ，开始注册一个 PayPal 账户。

![Screenshot02](https://img.vim-cn.com/45/7fb1513e567324421c0e084668565f4ecf8e36.png)

请选择对于账户的控制不算太严的个人账户。

![Screenshot03](https://img.vim-cn.com/77/5fe0de7e849c1b913e0911f42ea28ef921ce53.png)

输入个人信息后，因为 PayPal 的验证机制，无法在注册时绑定 GlobalCash ，那么就只能先跳过。
此外，请务必注册美国区的 PayPal ，中国区会出现各种各样奇怪的问题甚至注册到 贝宝 ，这样的话哭都来不及。

> 在注册的时候会请求手机号码，这里如果有手机号可以填入，没有的话可以到 [TextNow](https://textnow.com) 注册，记得两个号码之间要经常发个短信什么的来保证号码不被收回。

![Screenshot04](https://img.vim-cn.com/bd/f6e3975be9c0466f6f1890f46cec3b0ac3ae75.png)

在注册完之后，点击左下角的 [Link a bank or card](https://www.paypal.com/myaccount/wallet) ，输入 GlobalCash 的信息，完成绑定。图上我已经绑定好了。

## Step 1. 注册另一个 PayPal 空账户 
然后，和上面一样的流程，注册一个 PayPal 空账户。账户中不需要绑定卡。

![Screenshot05](https://img.vim-cn.com/09/bc3de82469747a123d0dd561e206a8d67c9143.png)

像这样。

## Step 2. 在两个 PayPal 账户之间倒腾钱
Google 的机制不允许没有绑定卡的 PayPal 账户进行付款， PayPal 也不能从银行卡直接充值进去，因此我们需要把钱从绑了卡的账户转到另一个没绑卡的账户，然后再转回来。
进入 [Send & Request](https://www.paypal.com/myaccount/transfer) ，然后选择 [Send to friends and family in the US](https://www.paypal.com/myaccount/transfer/send) 。

![Screenshot06](https://img.vim-cn.com/5c/b8dadffb123dfba45282ac19fdf332818c7340.png)

输入另一个帐号的邮箱，点击 Next ，并输入金额。完成之后，点击 Continue ，钱就会自动飞到另一个账户。
这里如果 Web 端没有办法发送一直报错，请试试使用 PayPal Android 客户端。

![Screenshot07](https://img.vim-cn.com/a3/54140e5b976920dd0d812b22a9df481dfae8db.jpg)

支付完毕后，另一个 PayPal 的零钱就多了所选择的数额。然而，  PayPal 从银行卡转账的手续费同样奇高无比，因此请避免多次小额转账。
登入另一个 PayPal ，当收到零钱之后，使用同样的方法再转回去。
这样，像 Step 0 的最后一张截图，绑定了 GlobalCash 的 PayPal 账户就能得到一些零钱。
然后，就试试在 Google Play 中购买应用吧！

![Screenshot08](https://img.vim-cn.com/2a/a484695b905d9ec5141b6a07352e9cdacbab4d.jpg)