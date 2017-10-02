---
title: 通过 GlobalCash 和 EntroPay ，在国内轻松使用 Google Payments
date: 2017-06-23 10:00:35
tags: [GlobalCash,EntroPay,Payments,Google]
---

### 写在开头的开头
Google 一直拒绝使用 UnionPay 和绑定了 UnionPay 的 PayPal 作为付款方式，这点各位都应该知道了。像我这样喜欢折腾又乐意为心仪的应用掏腰包的人，自然会去寻找更好的付费方式。 [GlobalCash](https://www.globalcash.hk) 是一个不错的选择，但是在 Google 禁止虚拟卡的打击之下，添加卡有时会无法绑定。若 GlobalCash 无法使用，我们就需要另找一个更可靠的支付途径，因此我找到了： [EntroPay](https://www.entropay.com) 
<!-- more -->
> 本文原载于 [鱼塘](https://pondof.fish/d/23) ，因为原文发布时与现在的情况出现了较大差异，转载过来并进行修改。

***
# 通过 GlobalCash 和 EntroPay ，在国内轻松使用 Google Payments

## Step 0. 注册一个 GlobalCash
> GlobalCash 是香港易票联支付和 MasterCard 联合推出的国际通用支付账户，可以将港元和人民币使用离岸汇率转成美元付款，在允许 MasterCard 的国外渠道上特别有用。

打开 [GlobalCash](https://www.globalcash.hk) 的主页，如下图：

![Screenshot1](https://img.vim-cn.com/08/dd7cc2a2e231dae789262139aa0be3d9673fc8.png)

点击右上角的 [免費獲取](https://www.globalcash.hk/sign-reb.do) ，在弹出的页面中输入所想要的卡信息。

![Screenshot2](https://img.vim-cn.com/12/ee8c0fb209e1e75a9f300fc9c8890289f6f6b9.png)

在充值 300 CNY 之后，应该就可以在 [GlobalCash](https://www.globalcash.hk) 中登陆了。在该页面中输入卡号/手机号，密码和验证码，之后大概会出现这样的一个页面：

![Screenshot3](https://img.vim-cn.com/bb/702cb89d93af876835afab04c107515e6e8c67.png)

在上端图片的右下角，就是卡的图样。图样的左边，就是详细信息的查询入口。请务必确保除了自己和支付工具（例如 Google Payments ），没有任何人能够看到卡的详细信息。
此外， GlobalCash 或许会要求实名验证，不过至少在目前，不记名卡的正常付款还未受到影响，只不过是无法提现和转账而已。若有这方面的需求，请在 GlobalCash 卡信息页面进行实名验证。

> 在国外，只需要拥有一张 MasterCard 或者 Visa 的 CVC 和 有效期 ，就能够使用那张卡付款。提高了便利性，但也为防止盗刷提高了难度。 Google Payments 等工具，在绑定卡时不会请求卡的支付密码，因为只需要 姓名 、 CVC 和 有效期 就足以验证身份并付款了，而不是 Google 与银行有什么奇怪的交易。

在这之后，就可以尝试在 [Google Payments](https://payments.google.com) 里试着绑定 GlobalCash 的卡片了。如果可以，那么这一篇 Tutorial 就结束了。下文的 EntroPay 为无法使用 GlobalCash 时的替代方案，可以获取一个备用，不建议长期使用，手续费非常高。 GlobalCash 几乎不收手续费，汇率也经过了核对，请放心使用。

## Step 1. 使用 GlobalCash 注册 EntroPay ，并使用 EntroPay 绑定 Google Payments
> EntroPay 则是由 Ixaris 在 2003 年所创立，给予所有人（不需实名）线上交易的能力的虚拟 Visa 卡片。创立得更早，意味着 EntroPay 已经被大部分公司，例如 Google ，所接受。

[EntroPay](https://www.entropay.com) 的官网设计值得称道。 ~~反正比 GlobalCash 好~~ 

![Screenshot4](https://img.vim-cn.com/1c/b3bd45c6d4085786bbd47b4b67c677e03e6283.png)

看到了吗，就是那个大大的 **[GET STARTED NOW](https://secure2.entropay.com/processes/upopenaccountnewuser/unprot/personalinformationentry.do?referrerID=entropay)** ，点击它，然后注册 EntroPay 。

![Screenshot5](https://img.vim-cn.com/83/39a44221d167afa5b5593a008845f2e6fcef9c.png)

输入您的卡信息。完成之后，会出现这样一个需要付款（至少 $5 ）来激活 EntroPay 的页面（我这边已经激活过了，因此没有强制需要付款。若是新卡， EntroPay 左边的卡图样会显示 0000 0000 0000 0000 ）。 EntroPay 的手续费有点高，不过 ~~坑爹呢这是~~ 没啥，也就是一百美元叫你多出 $5 的样子（我认为看到这里的各位除了我都是壕）。

![Screenshot6](https://img.vim-cn.com/62/dfb1b17ceb57d8f831130cff5f2aed554c24de.png)

付款之后，卡片就被激活了，可以在管理页面看到卡的信息。这个时候，账户的身份还是 Starter ，只能绑定一个卡，且付款、转账限额较低。通过在右上角“我的账户”的升级账户入口，可以将账户等级升高到 Basic 甚至 Premium 。账户升级完全免费（只不过是要求填一大堆资料，我直接填了 Google Payments 里面的，之前我随便找的美国地址。填写中国未测试）。

![Screenshot7](https://img.vim-cn.com/d7/e690a13b62898c0f4d0d0635a65a37027b64b3.png)

现在，就能去 [Google Payments](https://payments.google.com) 绑定这张 EntroPay 了。 EntroPay 被 Google 所接受，因此可以添加并使用。图上的实际 $5.99 可用 $5.00 ，就是我在 Google Play 买了一个应用做测试的结果。

> 请务必不要买自己不用的应用！请务必不要买自己不用的应用！请务必不要买自己不用的应用！刚买之后就找不到 Refund 了都是泪啊

## Step 2. 如果已经成功注册到 EntroPay 且一切正常…
PayPal 也是国际常用的付款/收款方式，何不注册一个 PayPal ，绑定 EntroPay 并点击一下下方的按钮支持我呢？
（至少看在我为了这篇教程浪费了 $0.99 的基础上……QAQ