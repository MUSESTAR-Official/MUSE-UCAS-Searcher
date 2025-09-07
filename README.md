# UCAS专业检索工具

这是一个用于检索UCAS（英国大学和学院招生服务）专业的Python脚本，可以根据关键词搜索相关专业并按录取要求排序。

## 功能特点

-  **关键词搜索**: 输入关键词搜索相关专业
-  **智能排序**: 按A Level要求从高到低排序（AAA* > AAA > AAB等）
-  **分类输出**: 自动分离有A Level要求和仅有UCAS Tariff要求的课程
-  **JSON导出**: 将结果保存为结构化的JSON文件
-  **完整信息**: 包含专业名、学校名、学位、学习时长、录取要求和课程链接

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

1. 运行脚本：
```bash
python ucas_searcher.py
```

2. 输入搜索关键词（如："Artificial Intelligence", "Computer Science", "Medicine"等）

3. 脚本会自动搜索并生成两个JSON文件：
   - `{关键词}_a_level_sorted.json` - 有A Level要求的课程，按要求从高到低排序
   - `{关键词}_ucas_tariff_sorted.json` - 没有A Level要求的课程，按UCAS Tariff分数排序

## 输出文件格式

每个JSON文件包含以下字段：
- **专业名**: 课程名称
- **学校名**: 大学名称
- **学位**: 学位类型（如BSc (Hons), BEng (Hon)等）
- **学习时长**: 课程时长
- **录取要求**: 完整的录取要求说明
- **A Level要求**: A Level具体要求
- **UCAS Tariff分数**: UCAS分数要求
- **链接**: 课程详情页面链接

## 示例输出

搜索"Artificial Intelligence"后，可能会生成：
- `Artificial Intelligence_a_level_sorted.json` - 包含剑桥、牛津等顶尖大学的高要求课程
- `Artificial Intelligence_ucas_tariff_sorted.json` - 包含其他大学按UCAS分数排序的课程

## 注意事项

- 脚本会自动获取所有搜索结果页面，可能需要一些时间
- 课程链接格式：`https://digital.ucas.com/coursedisplay/courses/[课程id]?academicYearId=2026`
- 数据来源于UCAS官方API，确保信息的准确性和时效性

## 技术说明

- 使用UCAS官方API进行数据检索
- 智能解析A Level成绩要求格式
- 自动处理分页和错误重试
- 支持多种成绩要求格式（A Level、UCAS Tariff、国际文凭等）