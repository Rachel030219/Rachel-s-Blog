---
title: 色彩可视化：从图片制作 CIE 1931 色谱
date: 2024-01-04 23:42:26
tags: [摄影, 色彩科学]
---

一直以来，针对色彩的讨论都是「玄学」重地。无论是手机还是相机、镜头，评测里绝对少不了大谈特谈一番「色彩」，却又鲜有人真能说出个门道。若设备有明显色彩倾向，或许还能用上个「偏黄」「发绿」之类字眼，对于「佳能拍人像、尼康拍风景」，或者「苹果真实而寡淡、小米浓郁而偏暖」，听着就只是一种刻板印象了。

但这又确实是一个，长久以来一直都可以严谨量化的领域。哪怕以 1931 年国际照明委员会提出 CIE RGB / XYZ 色彩空间作为起点，至今也已有八十余年，甚至比现行使用最广泛的 JPEG (ISO/IEC 10918-1:1994) 标准都要早半个世纪。到今天，几乎所有图片都会附带一个 ICC 文件，专门用来完成色彩管理工作；无论是还原到线性 gamma，还是从线性 gamma 转换至 CIE / PCS XYZ 再进一步绘出 CIE 1931 色谱，哪怕不是非常简单，至少也有标准可循。

这也是一个，长久以来一直欠缺严谨量化的领域。1931 年画出的那个舌形图至今仍具有相当理论价值，可即使是 DXOMARK 这类专业评测，都鲜有针对镜头色彩的测试；DPReview 曾经有 [相关对比](https://www.dpreview.com/reviews/nikond2x/13) ，给出 CIELUV 的色域分布，但它最多只能算是同一相机不同输出模式的比较，不具备太多参考意义。至今可能只有先看走得最远，他们在 [视频](https://www.bilibili.com/video/BV1yG411r7Gk/) 里提到，日后将与中国计量科学研究院合作，把色彩表现能力纳入评测内容。尽管视频中的评测方式不一定适用于计算摄影，如果他们后续开始对色彩进行客观评价，那也是评测行业一个不小的进步。

触动我的则主要是群友的博客： [《「所谓玄学」Part I：给色彩，打上花火》](https://www.wavechaser.xyz/optics-imaging-zh/2020/1/abyss-p1-hanabi) 。在这篇博客里，群友波波通过限定环境标板测试与实拍测试，证明了色彩的可量化性，并且通过标板的测试结果，成功解释了不同镜头在实拍测试中的表现。然而，中国计量科学研究院、标板、严格到色温的光照条件，这些名词离普通人都太远了。有没有办法直接从照片获得色彩分布呢？

<!-- more -->

当然有。我做了一个 Python 脚本，只要喂进图片就能生成对应的色谱图：

![Python script screenshot](python-screenshot.webp)

## 常见问题与太长不看

### 咋整啊？

我将小工具开源在 [Gist](https://gist.github.com/Rachel030219/1bdf6c6eb63115a9a61eb27618ecb579) ，可遵循 GPLv2 协议自由分发使用，也可直接下载文件 [picture_to_cie_diagram.py](picture_to_cie_diagram.py) 。本地准备好 Python 3 环境，安装 [ExifTool by Phil Harvey](https://exiftool.org/) ，运行 `python3 -m pip install numpy matplotlib colour-science imageio PyExifTool` ，再执行 `python3 picture_to_cie_diagram.py <图片路径>` 即可。如果 `<图片路径>` 是 `test.jpg` ，那么生成的色谱图会被保存到 `test_diagram.jpg` 。

这个小工具可以读写绝大多数图片文件，但更推荐使用 TIFF ，尽量避免使用 JPG 和 PNG，以最大化保留信息、还原色彩。

### 整这些有啥用啊？能让 XX 拍照比 YY 强吗？

没用，不能。在影响镜头成像的因素中，和锐度等因素比起来，色彩终究是一个比较靠后的选项，或者说，鲜少听说因为镜头 B 全方位拉胯、唯独色彩比 A 好，就会从 A 换到 B 的情况。对于手机来说更是如此，且不说根本没有镜头可以更换，在高度风格化的计算摄影中，能保留多少镜头色彩，还要打一个大大的问号。

但它依然有所意义。波波博客证明了「色彩可以被量化」，而我想解决的是「色彩如何量化」。通过这套方案，所有人都能够从任意 RGB 图片绘制 CIE 1931 色谱图，前期环境有多么严格受控，结果就多么符合实际。哪怕只是将两台手机拍的照片放在一起，也能看出它们色彩倾向的差异。

话又说回来，「色彩倾向」没有优劣，只有偏好。工具不会说话，也不提供目标；具体如何解释它产出的结果，就要交给使用工具的人了。

***

接下来，如果还有兴趣，我们讨论一些硬核内容：

## 先从色彩原理说起

> 本文默认读者具有中国大陆大学理工科的基本数学知识，作者并非数字图像处理、数字传媒或相关专业学生，本部分仅希望粗略且尽量浅显地普及前置知识，若有偏颇还请指正。
>

色彩原理，很大程度上是线性代数的魔法。如我们所熟知的那样，任何颜色基本都由三维构成：在颜料这种减色系统中，我们有红黄蓝，以及印刷工业里常见的青、品红、黄 (CMY)，它们和黑 (K) 一起组成了 CMYK；在光这种加色系统中，我们听得最多的是红绿蓝 (RGB)，博学多闻的读者会知道 YCbCr、L\*a\*b*、HSL。对于人眼，大部分人感知色彩的视锥细胞也是三种：L、M 和 S，它们是「三维」的本质。

光是知道有三维还不够。一位老前辈，Grassmann，告诉我们色彩感知大体上是线性的。通俗地说，假设一束光 A 和一束光 B 混合后，人看到的颜色和一束光 Z 相同，我们把它写为：

```
Z = A+B
```

如果此时两边同时混入一束光 C，人对它们的感知仍然相同，即：

```
Z+C = A+B+C
```

> 注意，这里的 `+` 并不是简单加和，而是「颜色混合」。

这个定律就如同数学里 1+1 = 2 一样基本，它表示无论何种色彩感知，最终都可以变成由三个值描述的、色彩空间里的某一个点，并且通过线性变换，就能够在不同色彩系统之间转换。

好学的读者会问：但是三维系统下所有人眼可见不可见的颜色都有，那也太不直观了，不是要作一张图吗？能不能使用一个二维坐标系就把色彩表示出来呢？

这就要请出 CIE XYZ 坐标系了。简单来说，这个坐标系抽象出了三个维度，其中 Y 轴严格遵循人眼对明度的感知函数 `V(λ)` 设置，X 和 Z 轴则可以保证坐标系中所有值都大于 0，方便在 1931 年进行计算，除此之外的规定不再赘述。总之，一旦拥有了 XYZ 坐标系，我们就成功地将明度 Y 从色度中分离。接着，我们可以对整个坐标系进行归一化：

```
x = X / (X + Y + Z)
y = Y / (X + Y + Z)
z = Z / (X + Y + Z) = 1 - x - y
```

容易看出，只需要有 xyz 其二，再加上 XYZ 其一，就能完整表示整个 XYZ 坐标系。考虑到只有 Y 是独立的明度，将它和 xy 组合起来，就形成了 CIE xyY 色彩空间，而这 xy，就是我们所需、完整且好看的二维色度了。

## 理论懂了，实际操作呢？

为了获得 xy，首先要获得 XYZ。Python 的 colour-science 包提供了很多有用的工具，不仅有从不同色域 RGB 转换至 XYZ 的矩阵，甚至还可以直接对 numpy 矩阵进行运算。这还不够，我们知道，图片通常都会经历一个 gamma 编码过程。这一过程非线性，它会不可避免地影响色彩，所以在转换前，我们还需要将 gamma 编码后的图像解码至线性。

简单来说，gamma 编码是一个高效利用码率的机制，通过在编码的时候，将更多空间用在人眼敏感的暗色区间，这样就能使用同样大小的文件，记录更多人眼可见的信息。

![Gamma correction](gamma-correction.webp)

绝大部分情况下，图片文件使用 gamma 2.2，如上图所示。原始图像文件是对角线，通过 gamma 编码得到蓝色曲线，这样更多码值就被分配到了阴影部分。后续如果需要处理，例如从中提取色彩，则再通过橙色曲线变换，将蓝色曲线解码得到原始对角线。用公式来描述就是一个这样的过程：

````
O = I^(1/2.2)
````

其中 O 是输出，I 是输入。由于 JPEG 文件中已经是 gamma 编码后的 O，为了得到 I，我们可以像这样进行运算：

```
I = O^2.2
```

这样就得到了原始的线性图像。当然，由于目前大部分图片文件都会附带一个 ICC 描述文件，我们可以直接从 ICC 里面得到 TRC 函数、转换矩阵 (matrix) 以及中间色彩空间 (PCS, 通常是 XYZ) 。借助图片和显示设备的 ICC 描述文件，通常正确的颜色管理过程如下：

![Color management](color-management.webp)

最终得到 device：在显示器上准确的 RGB 值。我们的工作只需要前一半，通过图片中编码的 RGB 值，经由 TRC 函数得到线性的 RGB (linear) ，最后通过转换矩阵得到 XYZ (connection) 。TRC 代表 Tone Reproduction Curve，意为「色调再现曲线」，处理输入到输出之间的亮度关系，它可以是一个描述了 `[0.0, 1.0]` 区间的矩阵，也可以是一个函数，具体内容可以参见 ICC.1: 2022 标准。

当然，阅读源码可以知道，经过 TRC 转换后，我们并没有进一步使用 matrix 计算得出 PCS XYZ。这是因为它作为 profile connection space，虽然与 CIE XYZ 大致相同，不过白点是 D50，而非常用的 D65；为了控制变量，我们忽略 ICC 提供的转换矩阵，直接统一使用 colour-science 提供的计算方法。

除此之外，ICC 标准还定义了许多种不同的转换模型，例如 LUT 以及多个转换方式混合使用的方案。这个工具仅对最典型的 RGB 下矩阵 / TRC 模型给出支持，主要是因为我在使用中没有碰到使用其他模型的情况，难以测试。如果遇到使用 LUT 的 ICC 描述文件，也可以贴在评论区，以便进一步提供支持。

总之，借助 TRC 和 colour-science ，我们现在成功将 RGB 转换到了 CIE XYZ，接下来就是计算 xy。这一步很简单，能够直接使用 numpy 进行，但为了优化及控制变量，我们依旧使用 colour-science。

终于可以绘图了！这一步使用 matplotlib，功能非常全面的绘图库，优化做得也不错，绘制一张两千四百万个散点的图片，即使是 8GB RAM 的 Mac 也毫无压力。从维基百科找到 SVG 的 CIE 1931 色度图后，可以很方便地从中提取出图片的 path，进行亿点点简单的坐标变换，就能将它塞进 `[0.0, 1.0]` 的坐标系中。当然也可以自己转换自己画，只是开发时偷了点懒。

> 原型开发过程中，本来使用的是 R，它的 brew 版调用 Quartz 绘图，直接吃爆了 40GB RAM 被杀掉；R Studio 画不出结果，Windows 下能出结果但卡得要命，所以惨遭弃用，好在群友给出了初版 Python 代码，详见感谢部分。

最后，我们还需要为点着色。为了得到好看、直观、准确的色谱图，我们不使用原像素颜色，而是自己指定点亮度，或者说 xyY 中的 Y，再将 xyY 转换至 XYZ 后映射到 sRGB 空间。

## 那么，前期该如何控制呢？

实验设计的关键是控制变量。以下将给出两个使用例，仅供参考。

### 测试不同镜头的色彩表现

参考波波博客，可以将镜头转接至同一款相机，在受控（或相同）光照条件、相同视角、相同白平衡与曝光下，对相同被摄物进行拍摄，将 RAW 使用相同工具，例如 [dcraw](https://github.com/ncruces/dcraw) 或者 [Apple SIPS](https://ss64.com/mac/sips.html) 转制成相同色域的 16 bit TIFF，再使用这个工具进行对比。这里照搬一段波波的博客：

> 限定环境下使用 3200K 钨灯作为主光源，搭配 Full CTB 高温滤纸矫正色温至 5500K Daylight；辅助使用 6200K 氙电弧闪光灯补全高温光谱，使用 -3EV 引闪程序补偿。
>
> 拍摄目标为 x-rite ColorChecker Classic 24-Patch  Target，面对它的 18% 灰色块人工锁定白平衡并确立 EV±0。拍摄时均采用 f/4.0 光圈，以改善画质、减少暗角并增大景深。
>
> ……
>
> 后期统一使用 RawDigger（基于 dcraw）转制 16bit TIFF，Debayer 目标色域 Adobe RGB，不加载任何矫正 Profile（包括内含的强制 Profile 也被绕过），不使用厂商提供的 CCM。之后所有 TIFF 均被统一映射到 Linear Gamma，再统一通过提供的转换矩阵保形映射到 CIE XYZ 制作 Chromaticity 图表。所有图片均会被二次校正曝光，以排除通光量差异或闪光灯可能造成的照明差异的影响。

前期控制变量自然是越严格越好。例如，尽管光度并不影响色度，前期不同曝光却会实实在在影响相机所能接收到的色彩，具体可以参考波波博客，这里就不再赘述。

### 测试不同手机的色彩倾向

与上面针对镜头的单项测试不同，色彩倾向反映了整个色彩系统的综合表现。考虑到大部分手机的输出都有 ISP 与相机应用内算法的协同处理，这一项通常使用不同手机的默认相机，在相同光照环境、相同视角、相同画幅下拍摄相同被摄物，随后导出 `jpg` 文件进行处理。

当然，可以参考波波博客，对手机镜头的色彩表现进行对比。由于目前手机的 ISP 都喜欢对图像进行处理，软件拿到的 RAW 就有概率已经是处理后的图像，这么做参考性不太高，不过图一乐也无妨。

## 感谢、参考与延伸阅读

[初版 Python 脚本](https://gist.github.com/Anthony-Hoo/b1630f320f990444d485ca0de6a52c10) 来自某位不愿透露姓名的嚯姓群友 [@Anthony Hoo](https://github.com/Anthony-Hoo/) ，没有他的贡献就不会有这个工具。除此之外，在完成转换工具以及写作本文的过程中，我还参考了下列书目、标准或文章，若读者感兴趣，也可进行拓展阅读：

> Wyman, C., Sloan, P. P., & Shirley, P. (2013). [Simple analytic approximations to the CIE XYZ color matching functions](https://jcgt.org/published/0002/02/01/paper.pdf). *J. Comput. Graph. Tech*, *2*(2), 11.
>
> Kerr, D. A. (2010). [The CIE XYZ and xyY color spaces](https://graphics.stanford.edu/courses/cs148-10-summer/docs/2010--kerr--cie_xyz.pdf). *Colorimetry*, *1*(1), 1-16.
>
> Schwartz, M. D. (2016). [Lecture 17: color](https://scholar.harvard.edu/files/schwartz/files/lecture17-color.pdf).
>
> International Color Consortium. (2022). [Specification ICC.1:2022](https://www.color.org/specification/ICC.1-2022-05.pdf).
>
> Phil Green. (2019). [Guidelines on the use of negative PCSXYZ values](https://www.color.org/technotes/Guidelines_on_the_use_of_negative_PCSXYZ_values.pdf).
>
> [Math | EasyRGB](http://www.easyrgb.com/en/math.php) & [RGB/XYZ Matrices](http://www.brucelindbloom.com/index.html?Eqn_RGB_XYZ_Matrix.html)
>
> Wikipedia - [Gamma correction](https://en.wikipedia.org/wiki/Gamma_correction) & [CIE 1931 color cpace](https://en.wikipedia.org/wiki/CIE_1931_color_space)
>
> 知乎专栏 - [色彩科学](https://www.zhihu.com/column/c_1602295156237197312) & [色彩科学学习笔记](https://www.zhihu.com/column/c_1129083002797633536)

在此一并表示感谢。
