'''
文件说明：这里加载./modules/criterias/下的体验点分类标准，并加载到POINTS字典中。
'''
import pandas as pd



POINTS = {}
df = pd.read_csv('./modules/criterias/mock_criteria.csv', sep=None, engine='python')
POINTS['mock'] = dict(zip(df['体验点二级分类英文'], df['英文描述']))

if __name__ == '__main__':
   print(POINTS.keys())