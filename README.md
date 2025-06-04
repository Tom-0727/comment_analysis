# comment_analysis
## 环境配置
```bash
bash env_prepare.sh
```

## 大模型API Key
- 新建一个yaml文件，比如就叫 openai_keys.yaml
- 在文件里面以下面的格式填充内容：
```text
openai:
  key: 'sk...'
deepseek:
  key: 'sk...'
api2d:
  key: 'fk...'
qwen:
  key: 'sk...'
```

## 文件目录解释 
- ```./inference_scripts/``` 下都是执行脚本，其中包括：
  - ```./inference_scripts/run_comment_analyze_set.sh``` 对一个文件夹下所有评论集文件做好差评提取+评论分析
  - ```./inference_scripts/run_comment_analyze.sh``` 对指定的一个评论集文件做好差评提取+评论分析
  - ```./inference_scripts/run_points_extract.sh``` 对指定的一个评论集文件做好差评提取
  - ```./inference_scripts/run_data_analyze.sh``` 对指定一个好差评提取结果文件做数据分析
  - ```./inference_scripts/run_criteria_make.sh``` 对一个样本集做无分类标准的体验点提取并聚类
- ```./modules/``` 下是算法实现，有具体的模块，其中入口可以看 ```agent.py```
- ```./points_extract.py``` 是好差评提取代码；```data_analyze.py```是数据分析代码；```criteria_make.py```是样本体验点抽取并聚类代码
## 执行评论分析
- 修改 ```./inference_scripts/run_comment_analyze.sh``` 中的文件路径即可执行