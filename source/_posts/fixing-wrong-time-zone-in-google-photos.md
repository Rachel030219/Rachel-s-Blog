---
title: 解决 Google Photos 备份照片的时区异常
date: 2023-02-11 12:05:10
tags: [备份, Google, 摄影]
---

如 [我的数据备份方案](https://blog.rachelt.one/articles/my-way-of-backing-up/) 所述，我的照片通过 Pixel XL 上传至 Google Photos，以便随时随地翻阅。这一方案体验一直很好，直到我先后购入了两台发布于 2010~2015 年的相机。不知为何，它们直出的照片在 Google Photos 网页端顺序混乱且没有规律，还常有显示日期错误，点开详情看时间却正常的问题，而手机拍摄的照片与经过 Photoshop 后期的照片则相当正常。经过一番探索，我发现问题主要出现在时区上，我上传的照片时区从 GMT-8 到 GMT+8 都有，导致照片排序混乱不堪。

![Google Photos 的时区错乱](https://blog.rachelt.one/articles/fixing-wrong-time-zone-in-google-photos/wrong-time-zone.png)

一番折腾后，我最终以较优雅的方式解决了这个问题，以下是我的探索过程与解决方案：

## 定位问题

已知是时区问题，首先就要弄清楚 Google Photos 如何确定时区。根据 Google 到的相关资料，Google Photos 会优先使用照片的 GPS 位置来确定时区，其次是照片 Exif 中包含的时区信息。然而，发布于 2016 年的 [Exif v2.31](https://www.cipa.jp/std/documents/download_e.html?DC-008-Translation-2016-E) 才正式加入时区偏移值，2016 年以前发售的相机自然不会支持。在没有 GPS 也没有时区的情况下，Google Photos 会使用多个办法估计照片的预计位置，例如其它设备的位置、具有相似内容的照片的拍摄位置等，没有启用预计位置时，它的时区判断依据就变成了 **上传 IP** 。

<!-- more -->

由于 *特殊的网络环境* ，国内用户访问 Google Photos 免不了要使用一些特殊的网络魔法，而网络魔法的 IP 可能在全世界乱跳，这也正是我所上传的照片时区混乱的原因。

既然已经知道原因，解决办法显而易见：

1. 在上传前，给所有照片加上时区；
2. 在上传前，去掉所有照片的时区与位置信息；
3. 使用固定 IP 上传。

> 这里探索、解决的思路均参考了 Medium 作者 [@nontavit](https://medium.com/@nontavit) 的两篇博客，分别是 [Google Photos sorting and time zone issue](https://medium.com/@nontavit/google-photos-and-time-zone-issue-b2e2d20645b0) 以及 [part 2](https://medium.com/@nontavit/google-photos-sorting-and-timezone-issue-season-2-15f46917e091) ，在此表示感谢。

其中，方案 3 最简单，只需要使自己的 IP 固定在 GMT+8 的时区即可，这里不再赘述；方案 2 简单暴力，虽然能让所有照片的顺序统一，但代价未免也有点大；下面着重来说说方案 1，也就是我给所有照片加上时区的探索，以及最终能够工作的方案。

## 探索方案

问题定位部分参考的博客中，作者提到可以使用 [GeoSetter](https://geosetter.de/en/main-en/) 设置图片的位置。尽管可行，但照片拍摄的位置不一定一致，而逐个手动指定或批量设置成同一位置显然不够优雅。我没有实际尝试过，也不确定 GeoSetter 能否批量仅设置时区，因此一开始打算方案 1 摆烂。

就在此时，摄影群的群友给了我新的思路。如果 Photoshop 编辑过的图片能够识别，那是否可以通过 [ExifTool](https://exiftool.org/) 找出实际发生变化的参数，然后手动通过命令行批量设定呢？通过对比时间相关的 tag，我的确找到一些蛛丝马迹：

![编辑后与原图的参数对比](comparison-between-raw-and-edited.webp)

然而，经测试， `Date/Time Created` 这一项不能编辑，它是由 `Time Created` 以及 `Date Created` 组合出来的，而且即使手动指定这两个参数，最后 Google Photos 仍然会以上传 IP 作为时区依据；尽管 `Metadata Date` 可以编辑，手动拆出 Exif 数据再进行字符串拼接，未免也有点不太优雅。这当然也是一种可行方案，只是我发现这一项时甚至快要写完全文，没有测试，尚不确定能否生效。

差一点万念俱灰的我，翻着 ExifTool 论坛时突然发现，其实早有人提过 [修改时区的相关问题](https://exiftool.org/forum/index.php?topic=13170.0) ，版主在下方的回复给出了一种修改 Exif v2.31 中所增加的三个时区偏移值参数的方法：

> `TimeZoneOffset` is a non-standard tag that was made before the EXIF standard actually added time zone tags. There are three time zone tags, `EXIF:OffsetTimeOriginal` , `EXIF:OffsetTime` , and `EXIF:OffsetTimeDigitized` , which correspond to `EXIF:DateTimeOriginal` , `EXIF:ModifyDate` , and `EXIF:CreateDate` respectively. You can set all three at once with a command like
> `-EXIF:OffsetTime*=+02:00`

也就是说，只需要一个 `*` 即可同时设定三个时区参数。TA 同时还给出了此前对 Google Photos 的测试：

> It's been a while since I've checked, so I don't know if Google Photos will read the above EXIF time zone tags. I do have in my notes from Nov 2019 that Google Photos would read the time zone if it was included in an XMP date/time tag such as `XMP:DateCreated` and `XMP:DateTimeOriginal` . But if there were GPS coordinates in the file, Google would figure out  the actual time zone at that location at that time and use that, overriding anything else.

从中可以得出，Google 读取时区的优先级是 GPS > 时区参数 > 内嵌时间，根据上面获取到的原图数据，相机记录的内嵌时间确实已经加上时区的偏移，因此只需要设置这三个时区参数就能够使 Google Photos 的时区正常，测试也印证了这一点。万事俱备，接下来是动手开始写代码。

## 解决问题

为了方便解决问题，我决定搓一个 Windows 下可用的批处理脚本，当我把待处理的文件拖放上去时，这个脚本自动帮我向所有拖放上去的图片加上系统时区，然后删除原图。拆分开来需要做三件事：首先，获取形似 `+08:00` 的系统时区（或者说，时区偏移值）；其次，对拖放上去的文件进行遍历，仅对 `.JPG` 的图片进行处理；最后，删除 ExifTool 留下的原图，仅保留处理后的图片。

### 第一步：获取系统时区

据我所知，Windows 下有两种方式获取时区偏移值，一种是使用 `systeminfo` 获取全部系统信息，然后手动截出其中的 `UTC+08:00` 字段，但由于 `systeminfo` 需要时间搜集，无法手动指定需要加载的信息，这种方式略显低效。参考 Stack Overflow 的提问 [Extracting timezone in windows](https://stackoverflow.com/questions/52567087/extracting-timezone-in-windows) ，我选择的是第二种方式，通过 Windows Management Instrumentation 的 command-line 管理工具 `wmic` 主动请求时区说明，再截出其中的偏移值。

```cmd
……
for /F "eol=; tokens=2 delims=^(^)" %%I in ('wmic timezone get caption /format:list') do (
   set "UTCTimeZone=%%I"
)
set "UTCTimeZoneOffset=%UtcTimeZone:UTC=%"
……
```

for 循环中，我们将 `wmic timezone get caption /format:list` 的执行结果拆出，以 `(` 或 `)` 为分隔符，取字符串拆分后的第二部分赋值给变量 `UTCTimeZone` ，也就是将形似 `Caption=(UTC+08:00) Beijing, Chongqing, Hong Kong, Urumqi` 的字符串，拆到只剩 `UTC+08:00` 。随即，我们对这个变量进行分割，取 `UTC` 之后的部分，这样就把 `+08:00` 赋值给 `UTCTimeZoneOffset` 。

### 第二步：遍历拖放文件

Windows 处理拖放文件的方式，其实是将拖放文件的路径当作执行程序的命令行参数，简单地 `%*` 即可获取到所有被拖放到脚本上的文件。为避免给非图片文件塞进时区参数，我们来一点小小的 for each 魔法：

```cmd
……
for %%x in (%*) do (
   if "%%~xx" == ".JPG" (
      exiftool.exe -EXIF:OffsetTime*=%UTCTimeZoneOffset% "%%~x"
   )
)
……
```

在这个 for 循环中，我们对传入的参数进行逐个处理，如果参数的后缀名是 `.JPG` ，那么调用 ExifTool 给它加上时区偏移值。

### 第三步：删除备份原图

ExifTool 默认会将原文件以 `.XXX_original` 的形式备份，由于对时区做改动相对安全且可逆，我们可以直接将未添加时区的原图删除。

```cmd
……
for %%x in (%*) do (
   del "%%~x_original"
)
……
```

这应该算是不需要额外解释的直白 for 循环。在这里不做后缀名判断的原因是，大多数时候不会有 `.XXX_original` 这种文件存在，而删除文件时文件不存在的报错不影响脚本执行，就是强迫症可能需要忍忍。

## 太长不看：最终方案

我将最终的脚本开源在了 [GitHub Gist](https://gist.github.com/Rachel030219/0f098e561f413e67e9d17298a6e66461) ，可以直接下载下来使用。

<script src="https://gist.github.com/Rachel030219/0f098e561f413e67e9d17298a6e66461.js"></script>

在应用这个脚本后，我的工作流从 `暂停 Syncthing -> 导入图片至同步文件夹 -> 修图 -> 启动 Syncthing` 变成了 `导入图片至临时文件夹 -> 全选拖放到脚本上 -> 修图 -> 移动所有图片至同步文件夹` ，没有增加太多麻烦的同时，大大提高了通过网页端 Google Photos 阅览图片的幸福度，这对于我的主要图片管理设备 Surface Pro X 来说尤为重要，希望对你也有帮助。
