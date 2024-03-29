---
title: 写给所有人的 Android 文件访问行为变更
date: 2020-11-09 00:44:50
tags: [Android, 开发, 存储, 行为变更]
---

Android 初代发布至今已有 12 年，这些年间，Android 一直因系统版本碎片化而饱受诟病。据 Google 数据，在统计范围内仍有 26.3% 的设备运行着 Android Marshmallow 及以下版本的系统，而升级到 Pie 及以上的设备更是只占了 39.5%。面对如此繁杂的系统版本，应用的兼容性是个大问题，尤其是文件访问方面的资料太杂乱分散，带来麻烦又浪费时间。本文以 Poweramp LRC Plugin 的开发为契机写就，希望能帮助此后跳进存储这个大坑里的开发者，以及想了解不同系统版本差异的用户。

<!-- more -->

> 本文探讨对象为 Android 原生 / 类原生系统，深度定制系统带来的其他问题（点名批评一些国产砍了 DocumentsUI <sup>[这是什么？ ](#Android-4-4-KitKat-19)</sup> ），不会也无法在此提及。
>
> 下文范围限于通用文件访问，访问媒体文件或作为提供者的场景仅作补充，可能不够严谨。

## Android 4.4 KitKat 以前 (~18)

众所周知，在 KitKat 以前的 Android 设备上，各路应用群魔乱舞，可谓「自启与保活齐飞，权限滥用共提权漏洞一色」，Android 4.1 之前连单独的读取权限都还没有。这一阶段，申请存储权限的应用能访问整个设备的存储空间（包括外置存储，如 TF 卡等）。那段时间的文件访问方式五花八门，应用可以通过 `GET_CONTENT` 和 `PICK` 两个 <ruby><rb>意图</rb><rt>Intent</rt></ruby> 的 <ruby><rb>行为</rb><rt>action</rt></ruby> 打开其它应用以选择文件，随后通过得到的 <ruby><rb>链接</rb><rt>URI</rt></ruby> 读取文件或对文件执行特定操作。前者获取到的 URI 只会允许应用读取内容，无法获取文件而不需要存储权限，后者则能使应用获取到指向文件本身的 URI，却并没能改变「群魔乱舞」的状况。

事实上，当时流行的解决方法（甚至被称为「正确」方法）是将 `PICK` 获取到的 URI 根据格式和来源解析并获取对应的文件路径，再通过 Java 提供的文件读写方案操作文件。获取路径的过程很复杂（也很脏），但它以添加几十行前人摸索出来的方法为代价，延续了许多开发者 Java 的操作习惯，或者单单只是绝对路径更「方便」，再加上文件系统直至 Android 10 才对应用封闭，这一方案「长盛不衰」。

> 关于 `GET_CONTENT` 和 `PICK` ，官方的表述较难理解，同时由于写下此文时找不到合适的测试设备，虚拟机镜像也早已无处可寻，以上只是大概且很可能有所疏漏，建议使用前参考 [官方 ACTION_GET_CONTENT 文档](https://developer.android.google.cn/reference/android/content/Intent#ACTION_GET_CONTENT) （只有英文）并多次测试，若有错误欢迎指出。

不过，何必非得弄得这么脏？应用已经有了整个存储的读写权限，自己造一个文件选择器也不是什么难事。除此之外，经历过那段时期的人一定忘不了 `/sdcard/` 、 `/storage/emulated/0/` 等等绝对路径。如此，花样层出不穷，用户体验严重割裂，粗放管理（以及粗放管理下积累起来的过时资料）或许就是一大堆问题的起源、今日文件存储问题的开始。谁知道呢？

## Android 4.4 KitKat (19)

从 KitKat 起，Android 引入了一套全新系统「<ruby><rb>存储访问框架</rb><rt>Storage Access Framework</rt></ruby>」，也就是 SAF，以及对应的 <ruby><rb>标准 UI</rb><rt>DocumentsUI</rt></ruby> 。 [官方描述](https://developer.android.google.cn/about/versions/kitkat#44-storage-access) 如下：

> 新的**存储访问框架**让用户能够在其所有首选文档存储提供程序中方便地浏览并打开文档、图像以及其他文件。用户可以通过易用的标准 UI，以统一方式在所有应用和提供程序中浏览文件和访问最近使用的文件。

用大白话来说，使用 SAF，应用可以打开一个文件选择界面，使用户在标准 UI 内从所有 <ruby><rb>文档提供程序</rb><rt>document provider</rt></ruby> （作为文件来源的应用，比如照片、网盘）中选择文件，并将其授权给应用。引入 SAF 统一了用户体验，增加了文件来源（以往只能从某个应用选择，现在可在一个地方看到所有应用），也不要求通过 SAF 读写文件的应用获取存储权限。标准 UI 集成了 `GET_CONTENT` 的支持，也就是说，本身并没有适配 SAF 的应用也可以 0 成本通过标准 UI 选择文件，并保持与原来相同的行为（只要没用脏方法）。同时，Android 开始收紧外置存储的访问，应用必须请求读写权限才能操作外置存储，并且 [外置存储限制不小](https://www.androidcentral.com/kitkat-sdcard-changes) 。这也造成了一揽子依赖 SD 卡的应用在系统更新到 KitKat 后停止工作，带来了不少抱怨。

KitKat 的 SAF 提供了 `CREATE_DOCUMENT` 和 `OPEN_DOCUMENT` 两个 action，分别对应创建文件和打开文件。 `GET_CONTENT` 并没有消失，它仍能像此前一样用于读入数据，而 SAF 提供给应用的是文件的「长期、持续访问权限」。例如，如果应用需要导入头像，那么它只需要 `GET_CONTENT` 即可，但若应用需要剪裁头像并保存到原文件，则必须使用 `OPEN_DOCUMENT` 。

随着 SAF 一同进入 KitKat 的，还有 <ruby><rb>内容解析器</rb><rt>ContentResolver</rt></ruby> 的新方法： [openFileDescriptor](https://developer.android.google.cn/reference/android/content/ContentResolver#openFileDescriptor(android.net.Uri,%20java.lang.String,%20android.os.CancellationSignal)) 。它返回 `ParcelFileDescriptor` ，提供来自 Java 的 <ruby><rb>文件描述符</rb><rt>FileDescriptor</rt></ruby> ，与实际的文件对应，可以使用 Java 的文件读写方案读取。文件描述符只指向文件内容，提供基础的读写，但不包含文件路径，也没有 Java 常用的 <ruby><rb>文件</rb><rt>File</rt></ruby> 的复杂功能。根据 [官方的描述](https://developer.android.google.cn/training/secure-file-sharing/request-file#OpenFile) ，

> 由于客户端应用只会收到文件的内容 URI，因此，在此过程中可确保文件的安全。由于此 URI 中不包含目录路径，因此客户端应用无法发现和打开服务器应用中的任何其他文件。只有客户端应用可以访问该文件，而且必须具有服务器应用授予的权限才能访问。

## Android 5.0 Lollipop (21)

Android 在 Lollipop 上进一步扩展了 SAF 的功能，允许应用使用新增的 action `OPEN_DOCUMENT_TREE` 请求用户授予某个目录下所有文件和文件夹的完全权限。由于标准 UI 具备外置存储的访问权限，应用可以通过这一新增特性再次取得 SD 卡权限，尽管通过 SAF 访问文件与此前有较大出入，但终归算是能用。

但是，秉着「能不做为什么做」的理念，诸多应用仍旧固守传统的文件访问方式，即便它们可以申请访问整个存储空间并获得类似的权限。

## Android 6.0 Marshmallow (23)

Marshmallow 带来了 <ruby><rb>运行时权限</rb><rt>Runtime Permission</rt></ruby> ，针对 Marshmallow 及更新的 Android 版本开发的应用，不仅需要像以前一样在清单文件中声明，还需要在使用权限的时候由用户手动许可，才能够使应用获取权限。理想很美好，但没有统一规范的结果就是应用针对的 Android 版本提高了，滥用权限还是没变。在国内最常见的是，当应用第一次启动时，弹出一堆授权窗口，用户只能选择同意，否则，有点良心的应用会好好说明为什么需要权限，中等的是重复请求授权，没良心的直接不给用。

另一项重大的改动在于 <ruby><rb>可采用的存储设备</rb><rt>Adoptable Storage</rt></ruby> ，它允许用户将 SD 卡等外置存储格式化并作为内置存储使用，从而大幅增大存储空间。这与本文主题关系不大，但值得注意的是应用通过系统方法获取到的缓存文件夹等会随着应用安装的位置而变动，一定程度上避免了应用使用绝对路径访问文件。但…真的有人将 SD 卡这么用么？随着主流设备逐渐淘汰手机的 Micro SD 卡槽，这一特性也成为历史。

## Android 7.0 Nougat (24)

Nougat 将应用间共享文件限制得更加严格，禁止将附带文件路径（ `file://` ）的 URI 暴露给任何其他应用，只能提供 `content://` URI。当然，只要一直遵循规范，无论是文档提供程序还是普通应用都不会在这里撞墙。

可能导致问题的是另一项特性： <ruby><rb>虚拟文件</rb><rt>Virtual Files</rt></ruby> 。此前的文档提供程序所提供的 URI 必须对应实际存在的文件，但在一些情况下，存储的文件或许并不能直接使用。考虑到这个问题，Nougat 提供了不需要对应实际文件的虚拟文件，其无法使用传统的文件读写方案读取，需要采取 [特殊的方法](https://developer.android.google.cn/about/versions/nougat/android-7.0?hl=zh_cn#virtual_files) 获得文件输入流。

> 虚拟文件本身概念抽象，加上官方的描述自相矛盾且 Nougat 以后就从未提及，使用到它的应用不多，相关的文章更是少之又少，能够把一切说清的几乎没有，因此本文暂且将其搁置不论。没有碰到最好，万一碰到了，可以参考这篇文章： [Virtual Files FAQ (Sorta) - CommonsWare](https://commonsware.com/blog/2016/09/06/virtual-files-faq.html) ，目前能找到的最详细的描述。

此外，Nougat 还提供了 <ruby><rb>作用域目录访问</rb><rt>Scoped Directory Access</rt></ruby> 以及一系列特定的存储目录（称为「标准外部存储目录」），例如图片、音乐等，在获得用户对这些存储目录的授权后，应用即获得了这一目录的完整权限。这有点像是 `OPEN_DOCUMENT_TREE` ，同样不需要声明权限，同样可以获得完全权限，但应用获得的路径由应用决定，免去了用户选择这一步骤。尽管如此，应用已经对完全读写权限的使用习以为常，因而这一特性的实际使用场景十分有限。其具体文档已经无处可寻，大概和下文将提到的、 Android 10 推出的 <ruby><rb>分区存储</rb><rt>Scoped Storage</rt></ruby> ，或者 Android 提供的强大的媒体文件访问脱不了干系。

## Android 8.0 Oreo (26)

SAF 在 Oreo 被进一步增强，带来了三个新特性。

针对尚未下载的云端文件，Android 允许第三方的文档提供程序提供新型「可寻址的文件描述符」，这种文件描述符以及 [新的使用方法](https://developer.android.google.cn/reference/android/os/storage/StorageManager#openProxyFileDescriptor(int,%20android.os.ProxyFileDescriptorCallback,%20android.os.Handler)) （以 `ProxyFileDescriptorCallback` 作为回调）使应用每次对文件进行操作的时候都会唤起文档提供程序并动态地加载应用所需内容，要多少就加载多少，从而避免了文件提供给应用时，文件必须全部下载到设备上。

> 事实上，虽然该特性是全新的，但文件描述符还是那个 `ParcelFileDescriptor` ，只是使用方法变了而已。

此前，媒体文件不能像文件一样被操作（例如移动、复制、删除），媒体管理器（相册、音乐播放器等）要让某个媒体文件变成可以操作的文档，只能在存储空间里面一个一个文件夹找（遍历）。Oreo [引入的新操作](https://developer.android.google.cn/reference/android/provider/MediaStore#getDocumentUri(android.content.Context,%20android.net.Uri)) 允许媒体文件的 URI 与文档的 URI 互相转换，从而为媒体管理器提供了极大的方便。尽管如此，这种操作并不会同步授予应用对应文件的权限，应用仍然需要使用 SAF 获取用户许可才能操作文件。

最后一个新特性允许应用「从文件系统的根目录中确定路径」，根据官方的描述，可以满足有如下需求的应用：

> - 您的应用使用可以显示特定文档位置的“另存为”对话框。
> - 您的应用在搜索结果视图中显示文件夹并且如果用户选择某个文件夹，应用必须加载此特定文件夹内的子文档。

之所以这个特性写得这么保守又简短，是因为 Android 开发者文档根本没有说如何利用这种路径，而且这个特性的讨论度低得吓人，貌似作用就只有展示给用户。下面附上一段个人的测试结果，仅供参考，如果用不上的话可以跳过不看。

> 根据测试，这个特性仅对通过 `OPEN_DOCUMENT_TREE` 获取到的文档树 URI 生效，如果对 `OPEN_DOCUMENT` 获取到的文档 URI 使用则会报 `java.lang.SecurityException` ，提示需要只有系统应用才能获取的 `MANAGE_DOCUMENTS` 权限。并且，这个特性有时会给出 `raw: /storage/emulated/0/XXX` ，而有时只会给出类似 `primary:XXX` 或者 `home:XXX ` 的路径（后者 `home` 估计意为文档的主目录，前者大概是「标准外部存储目录」？），挺混乱的。

## Android 9 Pie (28)

Pie 上对文件访问改动很少，唯一的差异是进一步提升了应用文件的安全性：针对 Pie 及更高版本开发的应用「无法使用所有人都可访问的 Unix 权限与其他应用共享数据」，也就是无法使应用自身存储的数据对所有应用开放。

## Android 10 (29)

Android 10 带来的「 <ruby><rb>分区存储</rb><rt>Scoped storage</rt></ruby> 」是近年 Android 更新讨论的焦点之一。从 Android 10 开始，所有针对 Android 10 及更高版本开发的应用，除非使用特殊方法，否则都无法访问传统的存储空间。应用只能访问自己的专属文件或缓存文件夹，或通过系统提供的标准方法访问位于存储空间的媒体文件，要么就必须使用 SAF 配合系统标准方法。这意味着此前所有的「脏方法」，在针对的 Android 版本提升后全部失效。为了确保开发者积极适配 Android 的新特性，Google 目前还要求新应用上架 Google Play Store 及老应用更新时，针对的 Android 版本必须为 Android 10 以上。也就是说，只要是这几个月在 Play Store 更新过的 Android 应用，基本都适配了分区存储规范。

但是，分区存储并没有从实质上解决文件和文件访问方式混乱不堪的问题。首先，Google 为了给应用更多的缓冲时间，预留了 [一个标记](https://developer.android.google.cn/training/data-storage/files/external-scoped#opt-out-of-scoped-storage) ，允许应用暂时通过老方法访问存储空间。而且 Android 作为开放的系统，不说那些直接提供安装包给用户的，大型的应用分发渠道（应用商店）远不止 Play Store 一家，虽然各家商店都有自己的规范，但各家商店审核不严格（点名批评所有国民级应用），而且这些规范都又老又旧，仿佛来自上个世纪。最后也是最重要的是，分区存储并不是类似于 iOS 或者 Windows 上 Sandboxie 的应用沙箱，至少在 Android 10 不可能是。正相反，从行为上而言，它只是 **关掉了应用的存储权限** 。

关于分区存储，在此就先按下不表。三言两语不一定能讲清楚，而若要详尽解答各个问题，可能就要另起一篇文章了。总之，对于本文，知道分区存储只是关掉存储权限即可。

除了分区存储，Android 10 在文件方面还作出了数项改进。

为了防止媒体文件在写入时被修改，Android 10 上的应用可以 [标记媒体文件为待处理](https://developer.android.google.cn/training/data-storage/files/media#pending-media-files) ，从而获取对媒体文件的独占访问权限，推测其效果大概类似于 Windows 上的「文件被占用」。

同样是写入媒体文件，Android 10 默认会按照文件类型将媒体文件存储至对应文件夹，也 [给了应用指定存放路径的自由](https://developer.android.google.cn/training/data-storage/files/media#provide-hint) 。例如，使用系统标准方法存储、不指定路径的图片默认在 `Pictures` 文件夹，应用也可以选择将其保存在 `Pictures/我的应用` 里。为了防止这个特性被滥用（比如明明是个图片却要丢进音乐里），Android [作出了相应的限制](https://developer.android.google.cn/reference/android/provider/MediaStore.MediaColumns#RELATIVE_PATH) 。

在 Android 10 上，不同的外置存储拥有各自唯一的名称。如果应用需要记录文件的来源，或者控制文件存储到哪个外置存储， [这个特性](https://developer.android.google.cn/training/data-storage/files/external#unique-volume-names) 便能派上用场。

## Android 11 (30)

文件访问及分区存储在 Android 11 上迎来了一次跃进。

Android 10 用于通过老方法访问存储空间的标记，在针对的 Android 版本提升到 Android 11 后不再可用，为了适应部分应用（比如文件管理）的需要，新的权限 `MANAGE_EXTERNAL_STORAGE` 应运而生。申请这个权限的应用和此前一样，拥有对存储空间的完整访问权限。根据观察，暂且可以把这个权限当作原来标记的替代品，其功能相差不大。当然，Google 可不是傻瓜，毕竟是自己造出来的规范，自然不会让随便什么阿猫阿狗都能挂着这个权限在 Play Store 上招摇过市。具体的使用范例、条件等可以查阅 [管理所有文件的官方文档](https://developer.android.google.cn/training/data-storage/manage-all-files) 。

在 Android 11 上，Java 提供的传统文件访问方案被部分带了回来：只要拥有媒体文件的读写权限（例如应用专属目录的文件或是应用自身创建在存储空间的媒体文件），应用就可以通过 [直接文件路径](https://developer.android.google.cn/training/data-storage/shared/media#direct-file-paths) 读取这些媒体文件。当然，这种方案受到分区存储的限制，强行访问应用不该访问的地方会导致报错。

Pie 引入的特性在 Android 11 上又进了一步：针对 Android 11 开发的应用不但不能让自己的数据对所有应用开放，也不能访问其他针对 Oreo 及以下版本的应用开放的数据。

受影响的还包括应用位于 `Android` 目录下的外部存储目录。以前，这些目录的访问限制很少，只要应用没有启用分区存储并且拥有存储权限，它就几乎能在这里肆意妄为。现在，无论是停用分区存储还是使用 SAF 请求用户授权， `Android/data` 目录都不再对应用开放（虽然它还在那里），意味着分区存储正朝着 Google 预想的方向前进，并且已取得一定成效。Android 11 的 SAF 对 `OPEN_DOCUMENT_TREE` 的限制不止于此。针对 Android 11 开发的应用无法再请求用户授予对各个存储设备（包括自带的存储空间和外置存储，例如 SD 卡）根目录以及系统下载目录的权限，提高用户的隐私安全。

***

### 尾

作为一个文笔不精阅历不深的摸鱼开发者，花了快 5500 个字，终于讲完了 KitKat 以后各个 Android 版本之间文件访问的差异，本文也从一开始的科普向逐渐转为了文末的四不像。本文不够清楚，更不够深入浅出，也没有什么深度，只是尽可能还原这些特性本貌的同时偶尔穿插个人的见闻、体验与感受，还请各位多多包涵、多多指教。

本文的资料来源主要是 Android 官方提供的行为变更文档、Stack Overflow 的诸多提问者与回答者以及 Google 找到的其他网站，特此向这些作者、开发者与网站运营者致以敬意。