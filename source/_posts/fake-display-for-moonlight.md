---
title: 使用 Indirect Display 虚拟显示器，全屏 Moonlight 串流
date: 2021-10-18 19:17:32
tags: [串流, 应用, Windows, Moonlight]
---

前几天终于用上了极为先进的 Moonlight，体验到了在移动端低延迟畅玩 3A 大作（主要是躺在床上推《魔夜》），却也遇到了一些不爽的地方，比如目前移动端设备千奇百怪，常规电脑渲染的 16:9 的画面，几乎不能在 2021 年的移动设备上铺满屏幕。怎么办呢？极客湾选择把用不上的输出接口与用不上的显示器接口连接起来，调整这个不存在的显示器的大小；市面上也有很多 HDMI 诱骗器，几十甚至十几块就能解决问题；我在看过蚊子大佬的博客后，选择动手折腾一个 Indirect Display，试试在不依赖外部设备的情况下，虚拟出第二个显示器用来串流。

因为不同设备的屏幕分辨率、刷新率不尽相同，使用 Indirect Display 还得信任签名时使用的证书，因此本文不会提供编译好的版本。不过编译并不复杂，具备计算机基础知识即可。

<!-- more -->

## 环境准备

前提条件当然是一台运行 Windows 10 的电脑。都这年头了，能用 Moonlight 串流这个条件不可能不满足吧……？

接下来安装的是 [Visual Studio 2019 社区版](https://visualstudio.microsoft.com/downloads/) 。打开安装程序，勾选「使用 C++ 的桌面开发」这个工作负荷。除此之外，还应当在「单个组件」里勾选你电脑指令集架构对应的，用来缓解 Spectre 影响的编译库，使用英文时它通常就在某个已经勾选的 MSVC 的下方，使用中文时搜索「MSVC 最新」可以很快找到。例如，在我的电脑上，默认勾选了 `MSVC…x64/x86 build tools (Latest)` ，那么只要再勾选上 `MSVC…x64/x86 Spectre-mitigated libs (Latest)` ，如图所示。

![install-spectre-mitigated-libs](install-spectre-mitigated-libs.png)

> 如果你安装 Visual Studio 的时候没有安装 Spectre 缓解库，可以打开安装程序补上，或在编译时无视 Spectre 警告和安全风险，尽管我个人不推荐这么做。

等待安装程序下载 Visual Studio 的这段时间，可以用来获取 GitHub 上 [微软官方提供的 Indirect Display 示范程序](https://github.com/microsoft/Windows-driver-samples/tree/master/video/IndirectDisplay) 。对 Git 和 Subversion 熟悉的话随意，不熟悉可以点击 [GitHub - IddSample.zip](https://github.com/microsoft/Windows-driver-samples/releases/download/159399/IddSample.zip) 或者 [备用镜像 - IddSample.zip](https://hub.fastgit.org/microsoft/Windows-driver-samples/releases/download/159399/IddSample.zip) 下载打包好的 zip 文件。它只有 20KB 大，下载下来后解压到任意一个能找到的地方就行。

Visual Studio 安装完毕后，我们还缺了编译驱动程序所需的 [Windows 驱动程序工具包](https://docs.microsoft.com/zh-cn/windows-hardware/drivers/download-the-wdk) (WDK)。官方提供的版本已经更新到了 Windows 11，跟着官方步骤走不会出问题，但 Windows 11 的软件开发工具包（SDK）尚未在 Visual Studio 中提供，得单独下载，而且还没有本地镜像…… [其他 WDK 下载](https://docs.microsoft.com/zh-cn/windows-hardware/drivers/other-wdk-downloads) 里的 [适用于 Windows 10 版本 2004 的 WDK](https://go.microsoft.com/fwlink/?linkid=2128854) 就能够满足需求了。WDK 安装完毕之后会提示安装 Visual Studio 扩展，保持默认设置。

## 代码改动

打开 Visual Studio，点击「打开项目或解决方案」，找到存放代码的地方，打开 `IddSampleDriver.sln` ，Visual Studio 会自动加载整个项目。接着，在右边「解决方案资源管理器」里，展开 `IddSampleDriver - Source Files` ，打开 `Driver.cpp` ，先不管 `Driver.tmh` 的报错（生成的时候会自动解决），改动下面几个地方：

##### Line 27

```c++
static constexpr DWORD IDD_SAMPLE_MONITOR_COUNT = 3;
```

这一行意思是创建的虚拟显示器数量。默认是 3 个，按需修改吧。

##### Line 52~54

``` c++
{ 2560, 1440, 144 },
{ 1920, 1080,  60 },
{ 1024,  768,  60 },
```

这里就是虚拟显示器的显示模式了，三个数字分别代表了宽度、高度和刷新率。可以直接修改已有的数字，如果需要更多显示模式，得将 `Header Files` 里 `Driver.h` line 42 的 `szModeList` 改为相对应的数值（默认是 3）。

##### Line 58~75

这十几行定义了另一个虚拟显示器，用不上可以直接删除。

##### Line 772~781

你应该能够看到数十行像这样的代码：

```c++
TargetModes.push_back(CreateIddCxTargetMode(3840, 2160, 60));
```

这些是驱动向 Windows 汇报的显示模式，三个数字也是宽度、高度和刷新率，它们会出现在显示适配器的「列出所有模式」中。在类似代码后新建一行，把 line 52~54 中自定义的内容以类似格式添加在此。

## 编译，安装！

修改完毕，在上方把 Debug 改成 Release，选择你电脑的指令集架构（一般是 `x64` ），再打开「生成」菜单，点击生成解决方案。等待进度条走完，出现类似 `生成: 成功 2 个，失败 0 个，最新 0 个，跳过 0 个` 的输出后，编译好的驱动就已经在 `IddSampleDriver.sln` 所在的文件夹中，指令集架构对应的文件夹里了（例如 `x64` 在 x64 文件夹下）。

为了顺利安装上自制驱动，首先要信任自动生成的证书。打开 `IddSampleDriver.cer` ，点击「安装证书」，「本地计算机」，「将所有的证书都放入下列存储」然后「受信任的根证书颁发机构」，安装。安装完毕后，关闭证书再打开，会显示这个证书已经受信任。

![install-certificate](install-certificate.png)

接下来就可以安装设备了。打开「设备管理器」，随便选一项，打开上方「操作」里的「添加过时硬件」，手动安装，一路下一步到「从磁盘安装」，定位到 `IddSampleDriver` 里面的 `IddSampleDriver.inf` （外面 `Release` 文件夹里那个是没签名的装不上），安装。如果一切顺利，打开显示设置就能看到添加的显示器了！卸载也很简单，从设备管理器中移除设备完事。

<img src="results.png" alt="results" style="width:50%; height:auto;" />

当然，在我的试验中，Windows 这个特性的稳定性还…不够让人满意，可能会碰到设备管理器中出现了 IddSampleDriver Device 却找不到第二个显示器的情况，此时你也可以试着以管理员身份运行 `Release` 文件夹中的 `IddSampleApp.exe` 或者其它可能行得通的办法，只要能够识别一次，以后就都不会出现问题。Enjoy！

## 如果不巧发生问题…

![when-signability-test-failed](when-signability-test-failed.png)

这个问题最常见的原因是签名工具签名时使用当前时间（中国标准时间是 UTC+8），验证时使用 UTC 时间，导致 0:00~8:00 期间无法以默认设置签名（无法签发未来的证书），通过修改签名设置可以解决这一问题，不过最优解是先睡一觉再继续， **早睡早起身体好！**

![when-sign-denied](when-sign-denied.png)

那么大个 `Access is denied` 告诉我们，签名工具没有驱动的访问权限（例如丢进了某个磁盘的根目录），将项目文件夹整个移动到用户文件夹（例如桌面）后重新编译就能解决。磁盘已满也会出现这个问题，试试清理一下？

## 结果如何？

在我尝试使用这个显示器串流时，遇到了一点问题…Moonlight 无法选择串流的显示器，会抓取默认显示器的视频流，我们看不到创建的这个显示器的画面，要把这个显示器换成默认几乎不可能。那么如果像极客湾一样把原有的线拔掉呢？

![performance](performance.png)

就…这样了。低得离谱的帧率、码率（实际感受比这还要卡）和高得离谱的输入延迟兼具，《地平线 4》就算了，连《魔夜》主菜单都卡，显卡的性能被直接腰斩（未测试…甚至全靠 CPU 也有可能？），这就是 HDMI 诱骗器好用的原因吧。不管如何，如果你有类似的需求并且使用的软件支持选择显示器，Indirect Display 的方案或许还挺值得一试的。

***

#### 参考资料

- 虚拟显示器终极解决方案 IndirectDisplay | https://qwq.moe/ultimate-virtual-monitor-solution-indirect-display
- How to run Parsec without monitor? Here’s a virtual monitor solution for you (Indirect Display) | https://archeb.medium.com/how-to-run-parsec-without-monitor-heres-a-virtual-monitor-solution-for-you-indirect-display-ecba5173b86a
- Indirect display driver model overview - Windows drivers | Microsoft Docs | https://docs.microsoft.com/en-us/windows-hardware/drivers/display/indirect-display-driver-model-overview
- Download the Windows Driver Kit (WDK) - Windows drivers | Microsoft Docs | https://docs.microsoft.com/en-us/windows-hardware/drivers/download-the-wdk
- visual studio 2012 - Int2Cat - DriverVer set to incorrect date - Stack Overflow | https://stackoverflow.com/questions/14148500/int2cat-driverver-set-to-incorrect-date