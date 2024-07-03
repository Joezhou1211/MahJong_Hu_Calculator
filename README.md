# 麻将听牌计算算法

本开源算法可以计算四川麻将中的具体听牌和剩余张数

## 功能
- **听牌计算**: 计算听牌/剩余的牌数/分数
- **可定制**: 可以修改以处理完整的广东麻将或四川麻将逻辑。
- **可扩展**: 集成图像处理和机器学习以识别图像中的牌，提供最佳出牌建议。

## 安装

1. 克隆仓库：
   ```bash
   git clone https://github.com/Joezhou1211/MahJong_Hu_Calculator.git

## 部署和访问
- 在服务器中运行运行main.py文件
- 通过http://host_ip:7001访问该程序

<img src="https://github.com/Joezhou1211/MahJong_Hu_Calculator/assets/121386280/37b0d2bb-10f2-42c0-b666-711c702e4335" width="330">
<img src="https://github.com/Joezhou1211/MahJong_Hu_Calculator/assets/121386280/c41ade75-4045-4275-bbb8-6e75db2a407b" width="330">
<img src="https://github.com/Joezhou1211/MahJong_Hu_Calculator/assets/121386280/b7912ef4-d77e-4bbf-bb6b-d9fb209b8b5d" width="330">



# 自定义修改建议
### 麻将牌定义
若需将算法改写为完整的广东麻将或四川麻将逻辑，请重新定义牌如下：
- **万**: 1-9
- **条**: 11-19
- **筒**: 21-29
- **风牌 (字)**: 31（东）, 33（南）, 35（西）, 37（北）
- **箭牌 (字)**: 39（红中）, 41（绿发）, 43（白板）
- **花牌**: 根据需要添加逻辑

### 需要修改的关键函数
1. **find_hu_combinations_for_each_possible_hu**:
   - 修改记分模式为对应分数。
   - 限定清一色范围。

2. **check_hu** 和 **find_possible_hu**:
   - 适应新定义的牌（万、条、筒）。

3. **combinations_data**:
   - 适应新结构。

### 其他增强功能
- **图像处理**:
  - 集成机器学习模型以识别图像中的牌。
  - 增强算法以准确判断剩余牌数并提供最佳出牌建议。

