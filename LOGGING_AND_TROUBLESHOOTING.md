# 日志输出和问题排查指南

## 增强的日志功能

从最新版本开始，程序会输出详细的调试信息，帮助您了解歌词下载的过程。

### 日志内容包括：

1. **使用的API源** - 显示正在使用哪个音乐平台（NetEase、KuGou、QQ Music）
2. **原始元数据** - 从音乐文件中提取的Artist和Title
3. **标准化搜索词** - 实际发送给API的搜索关键词
4. **搜索API端点** - 完整的搜索URL和参数
5. **搜索结果评分** - 显示前10个候选歌曲及其匹配分数
6. **歌词API请求** - 显示尝试获取歌词的具体API调用
7. **成功/失败状态** - 每个步骤的结果

### 日志示例：

```
=== NetEase Music API ===
Original metadata: ARTIST='周杰伦' | TITLE='青花瓷'
Normalized search: '周杰伦 青花瓷'
Search URL: https://music.163.com/api/v1/search/get
Search params: {'s': '周杰伦 青花瓷', 'type': 1, 'limit': 20}

Found 20 songs, top 10 scores:
  1. [ 18] 沈幼楚 - 青花瓷周杰伦（正式版）
  2. [ 15] 周杰伦, 李玟 - 刀马旦
  3. [ 10] 刘芳 - 青花瓷
  ...

Attempting to get lyrics from top matches:
  Trying song #2733603631: 沈幼楚 - 青花瓷周杰伦（正式版） (score: 18)
    Lyrics API: https://music.163.com/api/song/lyric?id=2733603631&lv=1
    ✓ SUCCESS: Found lyrics for: 沈幼楚 - 青花瓷周杰伦（正式版）
```

## 匹配分数系统

程序使用智能评分算法来选择最匹配的歌曲：

- **标题完全匹配**: +20分
- **标题部分匹配**: +10分
- **艺人完全匹配**: +30分（最高优先级）
- **艺人部分匹配**: +15分
- **艺人完全不匹配**: -10分（惩罚）
- **翻唱/伴奏/卡拉OK版本**: -8分
- **混音/现场版**: -8分

分数越高，匹配度越好。程序会尝试前8个得分最高（≥5分）的歌曲。

## 常见问题排查

### 1. 下载了错误的歌曲（翻唱版本）

**原因：** 真正的原唱版本可能因为版权限制不在搜索结果中。

**示例：**
- 元数据显示：周杰伦 - 青花瓷
- 实际下载：沈幼楚 - 青花瓷周杰伦（正式版）

**解决方案：**
1. 查看日志中的"Found X songs, top 10 scores"部分
2. 如果原唱不在列表中，说明该平台没有这首歌的歌词（版权限制）
3. 程序会自动尝试其他平台（KuGou、QQ Music）
4. 如果所有平台都失败，可能需要手动查找歌词

**受影响的艺人（版权保护严格）：**
- 周杰伦
- 林俊杰
- 某些国际艺人

### 2. 找到了正确的歌曲但没有歌词

**日志示例：**
```
Found 20 songs, top 5 scores:
  1. [ 40] 周杰伦 - 青花瓷
  
Attempting to get lyrics from top matches:
  Trying: 周杰伦 - 青花瓷 (score: 40)
    Lyrics API: https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric_new.fcg?songmid=...
    ✗ No lyrics available
```

**原因：** 歌曲在平台上存在，但歌词数据不可用（版权限制或纯音乐）

**解决方案：** 程序会自动尝试下一个平台

### 3. 完全没有搜索结果

**日志示例：**
```
=== KuGou Music API ===
...
✗ No songs found in KuGou results
```

**可能原因：**
- API暂时不可用
- 网络连接问题
- 搜索关键词在该平台没有结果
- 平台限制（IP封禁、反爬虫）

**解决方案：** 程序会自动切换到下一个平台

### 4. macOS Mach Port错误

**错误信息：**
```
Python[78046:14791268] error messaging the mach port for IMKCFRunLoopWakeUpReliable
```

**原因：** 这是PyQt6与macOS输入法框架(IMK)交互的已知问题

**影响：** 不影响程序功能，只是一个警告信息

**解决方案：** 已在代码中添加环境变量来抑制这个警告：
```python
os.environ['QT_MAC_WANTS_LAYER'] = '1'
os.environ['QT_LOGGING_RULES'] = '*.debug=false;qt.qpa.*=false'
```

## API源优先级

程序按以下顺序尝试各个平台：

1. **NetEase (网易云音乐)** - 中文歌曲库较全，但某些艺人有版权限制
2. **KuGou (酷狗音乐)** - 备选平台
3. **QQ Music (QQ音乐)** - 歌曲很全，但歌词经常不可用（版权保护）

## 测试工具

提供了两个测试脚本来帮助调试：

### 测试单个歌曲
```bash
python3 test_logging.py
```

### 测试所有平台
```bash
python3 test_all_sources.py
```

这些脚本会显示完整的调试信息，帮助您了解为什么某些歌曲无法下载。

## 建议

1. **检查元数据质量** - 确保音乐文件的Artist和Title标签准确无误
2. **理解版权限制** - 某些热门艺人的歌词可能在所有平台都无法获取
3. **查看完整日志** - 日志会告诉您程序尝试了什么，以及为什么失败
4. **批量处理** - 程序会自动跳过失败的歌曲并继续处理下一个
5. **手动补充** - 对于无法自动下载的歌曲，可以手动从其他来源获取LRC文件

## 版权声明

本工具仅供个人学习和研究使用。请尊重音乐版权，不要用于商业用途。
