---
title: 补遗：色彩空间，ICC 与颜色管理
date: 2024-03-21 12:47:45
tags: [摄影, 色彩科学]
---

如标题所述，这是一篇针对 [《色彩可视化：从图片制作 CIE 1931 色谱》](https://blog.rachelt.one/articles/converting-image-to-cie-1931-diagram) 的补遗。若尚未阅读前述文章，推荐先行阅读，它粗略地描述了利用 ICC 文件进行颜色管理的流程；本文意在对前文中「不一定正确」的说法进行纠正、补足及扩展。

> 本文 **不是** 一个校色教程，也 **不会** 事无巨细地描述某一步中具体的操作，而是一篇理论小记，全文字数约 6000，偶尔有图。
>
> 与前文相同，阅读本文需要读者具有至少中国大陆大学理工科的基本数学知识。作者并非数字图像处理、数字传媒或相关专业学生，作为补遗，本文希望 **尽可能准确** 地描绘出色彩科学的真实图景，但势必仍有疏漏与错误，若有偏颇还请指正。

## 色彩空间转换、色度适应变换

在前文中，色彩空间转换的章节有如下一段：

> 当然，阅读源码可以知道，经过 TRC 转换后，我们并没有进一步使用 matrix 计算得出 PCS XYZ。这是因为它作为 profile connection space，虽然与 CIE XYZ 大致相同，不过白点是 D50，而非常用的 D65；为了控制变量，我们忽略 ICC  提供的转换矩阵，直接统一使用 colour-science 提供的计算方法。

理论很美好，对吧？但实际的实现却很矬：

<!-- more -->

```python
colorspace = icc_profile.get_profile_description()
colorspace_split = colorspace.split(' ')
for i in range(len(colorspace_split), 0, -1):
    if ' '.join(colorspace_split[:i]) in colour.RGB_COLOURSPACES:
        colorspace = ' '.join(colorspace_split[:i])
        break
try:
    pixels_xyz = colour.RGB_to_XYZ(pixels_corrected, colour.RGB_COLOURSPACES[colorspace])
except KeyError:
    pixels_xyz = colour.RGB_to_XYZ(pixels_corrected, colour.RGB_COLOURSPACES['sRGB'])
```

用自然语言描述，这段代码从 ICC 文件中获取「文件描述」，用它查询是否存在对应转换矩阵，没有则从后向前缩一个词；没有查询到时，则会回落到 `sRGB` 。光是听起来都很矬吧。实际使用时，很多 ICC 文件的确会使用色彩空间作为描述，像是 `Display P3` 、 `Adobe RGB (1998)` 等，这样可以正确执行转换，问题是，许多厂商喜欢用自己的 ICC 文件，例如来自小米和 Google 的 `sRGB EOTF with DCI-P3 Color Gamut` 、 `Display P3 Gamut with sRGB Transfer` ，对它们如此操作，会分别匹配到最前面的 `sRGB` 和 `Display P3` ，以错误的参数映射至错误的空间。

解铃还须系铃人，要完成真正科学的转换，还得请出 ICC 文件。对于显示设备，ICC.1 标准定义了 *N-component LUT-based* 、 *Three-component matrix-based* 和 *Monochrome* 三种不同的转换方式。最后的 *Monochrome* 属于单色设备暂且不提，第一个 *N-component LUT-based* 应当是最完备的转换方式，利用数个映射表将颜色映射至任意指定的 <ruby><rb>描述连接空间 (PCS)</rb><rt>profile connection space</rt></ruby> ，不过实际使用中非常少见。最常见的是 *Three-component matrix-based* ，它是前文中提到并使用的、所谓「正确的颜色管理过程」：通过变换函数得到线性 RGB 值，再进行矩阵乘法将 RGB 映射至 PCS，它通常可以是 CIE XYZ 或 CIE LAB，均为绝对色彩空间，不受显示设备等因素影响，同时足够大，可以方便地作为中转，在不同输入输出之间转换。对于 *Three-component matrix* 定义的描述文件，PCS 只能是 CIE XYZ、通常使用 D50 白点，这就是常说的 PCSXYZ。但它使用的是 D50 白点，最终的 CIE 1931 色谱使用 sRGB 绘制，是 D65 白点。直接使用 PCSXYZ 值绘制色谱，纯白色对应的点会落在黄色上。怎么解决呢？

一个简单的办法是，既然 D50 的 XYZ 坐标是 `(0.96422, 1.00000, 0.82521)` ，D65 是 `(0.95047, 1.00000, 1.08883)` ，那我直接把 X 轴和 Z 轴缩放，X 轴所有坐标乘上一个 0.95047/0.96422，对 Z 轴同理，不就转换过来了嘛？**别，千万别。**这么做 **完全得不到** 正确的颜色，因为 X 和 Z 只在数学上具备意义，对它们缩放反而会导致各色彩的分配出现问题。

那是否可以缩放具备实际生理意义的坐标呢？这就不得不提 <ruby><rb>色度适应变换 (CAT)</rb><rt>Chromatic Adaptation Transform</rt></ruby> 了。 [von Kries 系数定律](https://en.wikipedia.org/wiki/Von_Kries_coefficient_law) 告诉我们，某一光照条件对视锥细胞产生的刺激，可以通过调节视锥细胞在另一个光照条件下的敏感度（即「系数」）得到。结合前文：

> 对于人眼，大部分人感知色彩的视锥细胞也是三种：L、M 和 S，它们是「三维」的本质。

不难得出，只要我们将 D50 下的 XYZ 映射到视锥细胞的色彩空间，在这个色彩空间里进行 D50 至 D65 的转换，最后把结果映射回来，不就得到 D65 的 XYZ 了吗？这就是 von Kries 变换的基本原理。它不够完善，却足够有效，成为许多现代 CAT 模型的基础。ICC.1 标准出于减少冲突的考虑，推荐如无特定理由，均使用线性 Bradford 变换，它是现代 CAT 模型的一种，基于 von Kries 变换改进视锥细胞的响应曲线，减少色彩重叠，因其足够优秀而被广泛应用。

总而言之，在改进之后，通过读取 PCSXYZ 的转换矩阵及白点，可以将 RGB 转换至 XYZ 空间，随后执行基于线性 Bradford 的色度适应变换，得到 D65 白点下的 CIE XYZ 值，如图所示：

![Conversion process with CAT](conversion_with_cat.webp)

基于这一过程的色谱绘制脚本已更新到 [GitHub Gist](https://gist.github.com/Rachel030219/1bdf6c6eb63115a9a61eb27618ecb579) ，欢迎下载使用。

> 细心的读者会发现，ICC 标准中还有一个 Chromatic Adaptation Tag，为什么不直接使用这个 tag 记录的矩阵做转换呢？这是因为这个矩阵并不用于「转换至某个标准」，仅仅只是用来记录「原始色彩如何转换至 D50」，并没有规定具体的原始色彩。实践中，尽管通过这个矩阵确实可以将图片还原至 Media White Point 记录的颜色，但这些 tag 并非强制标准，因此最终选择对所有输入统一进行 Bradford 变换——希望这里不要衍生出另一个《补遗》。

## 关于颜色管理

这又是一个众所周知，却又通常没人认真了解的话题。它的门槛低到买过电脑的人都多少会评判 ΔE 的好坏，也知道苹果笔记本的颜色比普通笔记本更好，追求高一些的用户还会利用专业设备对自己的屏幕进行校色；可哪怕是这些用户里，都鲜有人能说出其中一二。

> 甚至还有人提出过「显示器的颜色配置是对输出色域的控制，选中 sRGB 的描述文件是将色域限缩到 sRGB」这种明显与实际截然相反的观点。一路读到这里的读者想必已经明白，ICC 不过是一个色彩空间转换过程，使用标准色彩空间 ICC 文件作为显示器 ICC，意思就是告诉系统「我的显示器色彩只有这个范围」。
>
> 假设一台广色域显示器上 sRGB 红对应的像素颜色是 `(0.7, 0, 0)` ，对它指派 sRGB 的文件，系统会认为这台显示器只有 sRGB 色域，传过来 sRGB `(1.0, 0, 0)` 就会按照 `(1.0, 0, 0)` 显示，不仅没有正确限缩色域，而且使颜色更加浓艳。

作为补遗，这里会从概念开始说明，并且相对详细地对不同系统的颜色管理实现展开描述。

### 色准与校色

我们知道，色彩是一个三维空间。既然是空间，两点之间自然就会有距离，那将这两点之间的<ruby><rb>距离</rb><rt>欧几里得距离</rt></ruby>计算出来，不就是颜色之间的差异吗？这是色准计算的基本原理，计算出来的值即是大家耳熟能详的 ΔE。

说起来简单做起来难。在不同的色彩空间中，颜色的坐标也千差万别，到底应该以谁计算出来的距离为准呢？事实上，的确存在针对不同色彩空间的不同 ΔE，而校色软件 DisplayCAL 用来计算的标准，基于国际照明委员会 (CIE) 在 1976 年提出的 CIELAB (*L\*a\*b\**) 色彩空间。这个色彩空间的目的是，通过 *L\** 、*a\** 和 *b\** 三条非线性的坐标轴，模拟视觉系统的非线性响应。在 CIELAB 空间中，坐标变化的量一定时，人感知到的色彩变化量也一定，这使它很适合用来计算颜色之间的距离或差异。

总之，对于色准测量过程，当接上色度计或光度计后，DisplayCAL 这类软件会在屏幕上显示颜色值，并且获取仪器测量到的色彩，将它们转换至 CIELAB 空间，并计算单个颜色的 ΔE；逐个测量完成后，即可计算平均 ΔE 和最大 ΔE；校色过程也类似，也是显示颜色、测量偏差，不同的是这里会进行进一步计算，从而得出准确还原所需要的 TRC 与转换矩阵，将它们写入 ICC 文件，并且交给系统，便完成了一次校色。

***

理解前文再来看，会发现颜色管理其实也就是那个由 ICC 文件主导的过程。假设系统没有参与颜色管理，那么对于具备 ICC 文件的图片，聪明的图片查看器会利用 ICC 文件，按照前文说的流程，将 RGB 转换至 XYZ 空间；随后，再使用显示器的 ICC 文件，将 XYZ 空间转换至显示器上准确的 RGB。这里再请出这张图：

![Color management process](color_management_corrected.webp)

这里没有魔法，只有数学。由于不像前文制作的脚本那样，需要将 XYZ 空间的色彩值移动至特定白点并完成比较，只需借助 XYZ 这一绝对空间完成转换，甚至比色彩可视化还要更简单。

然而，并不是所有屏幕上的内容都有 ICC 文件。一个应用告诉系统，我这里要 `#FF0000` 的大红，这来自什么色彩空间？我们不知道，系统也不知道。比较安全的做法是，把这个颜色当作 sRGB，先转换至线性、随后至 XYZ，再利用显示器的 ICC 完成后续转换。

事情却没有这么轻松。我详细了解常见系统的颜色管理模式后发现，相同的思路可能受不同的实现、相异的生态、厚重的历史包袱等因素影响，带来完全相反的结果。

### Windows

在臭名昭著的 Windows 上，应用的显示内容会被提交至 <ruby><rb>桌面窗口管理器 (DWM)</rb><rt>Desktop Window Manager</rt></ruby> 进行渲染与<ruby><rb>组合</rb><rt>混成</rt></ruby>，然后再转交给<ruby><rb>显示内核</rb><rt>display kernel</rt></ruby>，由它负责管理显示器输出。一直以来，Windows 的默认行为都是无论何种色彩空间，交给 DWM 时统一默认当作 8 bit sRGB，不经过色域转换，直接交给显示内核输出到显示器。

> 这个显示过程理应不涉及颜色管理。可是，用过 Windows 的各位都知道，哪怕是默认设置的 SDR 显示器，在经过校色后也会有明显的色彩变化。为什么呢？
>
> 我并没有 Windows 应用开发经验，询问开发者后得知，原生 API 的确全都不会跟随 ICC。据此我推测，虽然 Windows 并没有在系统层面进行颜色管理，但诸如 explorer 等组件，在渲染时还是会执行最低限度的色彩转换，进而导致色彩变化。
>

Windows 10 1703 为 HDR 显示器添加了 [<ruby><rb>高级颜色</rb><rt>Advanced Color</rt></ruby>](https://learn.microsoft.com/en-us/windows/win32/direct3darticles/high-dynamic-range) 支持，Windows 11 22H2 将这一支持扩展到 SDR 显示器，Windows 第一次拥有了全局颜色管理能力。启用高级颜色后，DWM 使用中间色彩空间混成应用，对不同应用的颜色进行管理，再由显示内核将中间色彩空间转换至目标并输出。具体来说，这里有三个值得描述的部分：

![Windows display process](windows_display_process.webp)

首先是色彩空间。Windows 定义了一个概念， <ruby><rb>规范合成颜色空间 (CCCS)</rb><rt>canonical composition color space</rt></ruby> ，即 DWM 混成时使用的中间色域。为了减少颜色损失、留足余量，同时尽可能减轻显示器压力，启用高级颜色时，Windows 使用 16 bit scRGB 作为 CCCS。它由 sRGB 的 primaries 组成，可以最大程度兼容老应用，同时允许超出 [0, 1] 的色彩值，相当宽广，覆盖范围超过整个 CIE 1931 色谱图，满足一切需要；

然后是混成过程。支持高级颜色的应用具有显式声明色彩空间的能力，老应用则会直接按照 sRGB 处理，这些不同的颜色与空间，会被 DWM 统一转换至 scRGB；

最后是显示输出。对于 HDR 显示器，显示内核会将 scRGB 转换为 HDR10 / BT.2100；对于支持高级颜色的 SDR 显示器，Windows 会读取显示器 ICC 里包含峰值亮度等参数的 `MHC2` tag，再利用这些参数进行色彩空间及亮度的映射。

听起来很美好是吧？然而，不管是高级颜色还是普通模式，Windows 似乎都有很多事情没有拎清楚。例如，除非使用微软推出的 UWP 或 WinUI 3 等官方框架，否则仅当应用主动使用 DirectX 输出时才支持高级颜色。而且，哪怕应用主动选择 DirectX，现阶段用来输出的接口 [IDXGIOutput6](https://learn.microsoft.com/en-us/windows/win32/api/dxgi1_6/nn-dxgi1_6-idxgioutput6) 也 [只能识别 HDR 显示器](https://learn.microsoft.com/en-us/windows/win32/direct3darticles/high-dynamic-range#idxgioutput6) 。更糟糕的是，在 Windows 历史上 *浩如烟海* 的官方 UI 框架中，绝大部分死透的同时，还拉着老一批做了颜色管理的 app 以 8 bit sRGB 的形式一起陪葬。精度上限卡在这里，只能度过相对失败的 app 生；机关算尽太聪明，反被 Windows 一刀砍进 sRGB。除此之外，激活高级颜色依赖显示器的 `MHC2` tag，不兼容现有的 DisplayCAL 校色流程。其中很多都是转型期必然发生的阵痛，微软也提供了临时回退方案，可这一阵痛的终点，至今仍遥遥无期。何苦呢，还是看看远处的 macOS 吧。

### macOS / iOS

苹果阵营的状况，比 Windows 好太多。自 1993 年推出 [ColorSync](https://developer.apple.com/library/archive/technotes/tn2313/_index.html#//apple_ref/doc/uid/DTS40014694-CH1-ACTIVECOLORMGMTCOLORSYNC) 起，Mac OS / OS X / macOS 就支持了 <ruby><rb>主动颜色管理</rb><rt>active color management</rt></ruby> ，提供 [Core Image](https://developer.apple.com/documentation/coreimage/) 、 [AV Foundation](https://developer.apple.com/documentation/avfoundation/) 等一系列支持颜色管理的组件，原生具备全链路的颜色管理能力。这里借用一张苹果官方的图：

![macOS color management process](tn2313_whathappensinappall.webp)

> 相机拍下一张照片，经过 Color Sync 处理后传输至应用，应用通过 Quartz 混成、输送给 Color Sync 转换至显示器色彩再输出，到最后使用 CUPS 打印出来时 Color Sync 将照片转换至打印机的 CMYK，对应到 ICC 标准的 Input - Display - Output，每一个步骤都被正确管理。

对应用来说，加入这一链路也非常简单，只要应用窗口声明了色彩空间，或者给输出缓冲区加上色彩空间标记，即可享受苹果爸爸的关怀。哪怕应用什么都不做，它也会被当成 sRGB 处理，而不会像 Windows 那样直接向显示器输出。

起源于 macOS 的 iOS 应该从娘胎起就有完整的颜色管理，对吧？还真不是。苹果官方的早期资料说，iOS 应用采用 [<ruby><rb>目标颜色管理</rb><rt>targeted color management</rt></ruby>](https://developer.apple.com/library/archive/technotes/tn2313/_index.html#//apple_ref/doc/uid/DTS40014694-CH1-TARGETEDCOLORMGMT) ，显示的所有东西都应该以 sRGB 为目标调校，换句话说：

<img src="./humphrey.webp" alt="Humphrey: look you'd do something and do nothing" style="max-width: 50%;" />

好在 iPad Pro 9.7 引入 True Tone 时，也把完善的 CGColorSpace 和 ColorSync 带到 iOS，迭代数年从 iOS 16 开始提供现代 ColorSync API。在此期间，iPhone 与 iPad 的生态也逐渐丰富，从只有 LumaFusion、iMovie 和手机修图 app，到现在 Final Cut Pro、DaVinci Resolve、Affinity Photo、Adobe Photoshop 等一应俱全，苹果的号召力自然显著，iPhone 与 iPad 优秀的硬件素质也有助益，完善的系统级颜色管理更是功不可没，这一套组合拳把 Android 远远甩在脑后。

### Android

如今 Android 面临的困境，与初期 iOS 类似。针对手机开发的操作系统，要考虑的东西和电脑大不相同，大部分时候都只有那一块屏幕，也没有什么打印机扫描仪或者媒体创作生态，更何况一开始的手机屏幕连覆盖完整 sRGB 都很勉强，何必费劲做颜色管理呢？因此，直到今天，Android 设备上都和传统 Windows 保持一样的逻辑：应用说我要 `(255, 0, 0)` ，屏幕就把这一个像素的红色拉到最亮。

Oreo (8.0, 26) 后，Android [正式支持广色域](https://developer.android.com/training/wide-color-gamut) 。此前，表示颜色使用的是 Color int，一个形似 `0xFF00FFFF` 的数字，刚好是 32 bit 的无符号 int，每两位代表一个 8 bit 的颜色值，对应了 ARGB 四个通道。Oreo 后引入了 Color long，利用 Color 类新增的 `pack` 方法，将颜色值连带色彩空间一起打包进 Color long 中，最大支持到 16 bit 浮点数，同时 Color int 全部默认位于 sRGB 中，以提供最大兼容。

听起来很好，但非常搞笑的事情是， **几乎所有的 Android 组件都只支持 Color int** ，根本没有使用 Color long 或者 Color <ruby><rb>类</rb><rt>对象</rt></ruby> 的机会。Color 对象提供的 `toArgb` 方法能够将 Color long 转换为 int，也考虑了色彩空间的转换，可是最后 **超出 sRGB 色域的颜色会被直接舍掉** ；而且，自己使用 Color long 的时候，其颜色值的范围是个非常不明不白的 [-65504.0, 65504.0]，让人丈二和尚摸不着头脑。非要使用原生控件的话，手动调用 Canvas 和 Paint 绘制时，才能够使用 Color long。官方呢，官方不救一下吗？官方在推荐 [Vulkan](https://developer.android.com/training/wide-color-gamut#vulkan) 和 [OpenGL](https://developer.android.com/training/wide-color-gamut#opengl) 。

总结起来，Android 的颜色管理是「如做」：系统里处处透露出努力了的气息，却没有真的努力；应用自己若是想做，还得处处碰系统的壁。

这一生态还有个最大的问题：碎片化。各家厂商都喜欢做所谓「原色模式」，却鲜有文档记载工作原理；他们还喜欢声称所谓「全链路 XX 能力」，实际一看却仅限于原装寥寥几个应用中有限的输入、显示与编辑功能，而且哪怕是同厂商、同系列中的不同机型，功能与表现可能都有差异。我一路哐哐写到这里，查阅了各平台从老到新无数开发者文档、指南等资料， **唯独 Android 厂商的说明是死活找不到** ，三星、小米、华为和 OV 在这方面都是一坨，找到的不是新闻稿就是第三方新闻稿，我很怀疑厂商自己知不知道自己拉出来的是什么东西。

当然，厂商摆烂很大程度上也和生态有关。说白了，没人在乎。拍照发朋友圈、拍视频发抖音都没问题，为啥要费劲不讨好，面向十年后超前优化？Google 没有打造系统级的颜色管理，自己做到时候还要推倒重来，何必费这个工夫？足够在发布会上吹两句就好，为 1% 的需求完善 99% 的用户都感知不到的底层设计，确实浪费精力。

### Linux

说实话，这部分我心里着实没底。Linux 的生态过于开放、庞大而复杂，不同的搭配组合还可能带来完全不一样的结果。而且，不像 Windows 和 macOS，创意工作方面 Linux 的选择极少，大都伴随着妥协。一定要的话，Gentoo Wiki 的 [Color management](https://wiki.gentoo.org/wiki/Color_management) 以及 Wikipedia 的 [Linux color management](https://en.wikipedia.org/wiki/Linux_color_management) 都可以作为不错的参考，在此不再展开。

***

最后，如何才能知道设备或应用是否进行了正确的颜色管理呢？这里有一张照片：

![Photo with profile](RQ_profile.jpg)

如果它看起来是常规街头，说明颜色管理工作正常；反之，如果它上半部分一片黑，斑马线还泛着粉红的光，像这样：

![Photo without profile](RQ_noprofile.webp)

这是一个去除掉 ICC 文件的范例，如果上面那张照片和这张看起来一样，那颜色管理可能就有点问题了。很多网站也提供了类似的功能，比如 [Wide Gamut](https://www.wide-gamut.com/test) 。

> 一些读者知道，Google 官方有一张 [全红色的机器人 PNG](https://android-developers.googleblog.com/2019/05/wide-color-photos-are-coming-to-android.html) ，插入了 Display P3 的 ICC 描述文件，却没有给出太详细的解释。事实上，这张图的目的是判断设备是否具有广色域支持，使用这张图的 **前提是正确进行颜色管理** 。这张图的中间是 `(255, 0, 0)` 的大红色 Android 机器人，背景是 `(237, 0, 0)` 这种稍暗的红色，在颜色管理正确的应用上显示时，如果设备的目标色域是 sRGB，那么这两种颜色都会转换到溢出；只在设备能够处理溢出的颜色，或目标色域大于 sRGB 时，才能正确显示出机器人。 **如果根本没有颜色管理，直接按照颜色值渲染，同样看得出区别** ，这是一些文件管理器的缩略图能看到机器人，点开大图却看不到的原因。

## 尾、参考与延伸阅读

至此，终于结束了这一篇似乎有点过长的「小记」或「补遗」，感谢在这一过程中帮助我搜集、验证资料与想法的朋友们。除此之外，我还大量参考了下列内容，可以作为延伸阅读：

> International Color Consortium. (2022). [Specification ICC.1:2022](https://www.color.org/specification/ICC.1-2022-05.pdf).
>
> Chong, H. Y., Gortler, S. J., & Zickler, T. (2007, October). [The von Kries hypothesis and a basis for color constancy](https://doi.org/10.1109/ICCV.2007.4409102). In *2007 IEEE 11th International Conference on Computer Vision* (pp. 1-8). IEEE.
>
> Mokrzycki, W. S., & Tatol, M. (2011). [Colour difference∆ E-A survey](https://www.researchgate.net/publication/236023905_Color_difference_Delta_E_-_A_survey). *Mach. Graph. Vis*, *20*(4), 383-411.
>
> DirectX Developer Blog | [Advancing the State of Color Management in Windows](https://devblogs.microsoft.com/directx/auto-color-management/)
>
> Microsoft Learn | [Use DirectX with Advanced Color on high/standard dynamic range displays](https://learn.microsoft.com/en-us/windows/win32/direct3darticles/high-dynamic-range), [ICC profile behavior with Advanced Color](https://learn.microsoft.com/en-us/windows/win32/wcs/advanced-color-icc-profiles), [Windows hardware display color calibration pipeline](https://learn.microsoft.com/en-us/windows/win32/wcs/display-calibration-mhc)
>
> Farseerfc的小窝 | [桌面系统的混成器简史](https://farseerfc.me/zhs/brief-history-of-compositors-in-desktop-os.html)
>
> Apple Developer Documentation | [TN2115: Image Color Management](https://developer.apple.com/library/archive/technotes/tn2115/_index.html), [TN2313: Best Practices for Color Management in OS X and iOS](https://developer.apple.com/library/archive/technotes/tn2313/_index.html), [TN2227: Video Color Management in AV Foundation and QTKit](https://developer.apple.com/library/archive/technotes/tn2227/_index.html)
>
> Jeffrey Friedl's Blog | [So Much For That Glorious iPad Screen: iOS and its Apps are Not Even Color Managed](http://regex.info/blog/2012-03-27/1964)
>
> Android Developers Blog | [Wide Color Photos Are Coming to Android: Things You Need to Know to be Prepared](https://android-developers.googleblog.com/2019/05/wide-color-photos-are-coming-to-android.html)
>
> Android Developers | [Enhance graphics with wide color content](https://developer.android.com/training/wide-color-gamut)
>
> Android Open Source Project | [Color management](https://source.android.com/docs/core/display/color-mgmt)
