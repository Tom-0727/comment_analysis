'''
文件说明：这里加载./modules/criterias/下的体验点分类标准，并加载到POINTS字典中。
'''
import pandas as pd



POINTS = {}
df = pd.read_csv('./modules/criterias/standing_desk_criteria.csv', sep=None, engine='python')
POINTS['standing_desk'] = dict(zip(df['体验点二级分类英文'], df['英文描述']))
df = pd.read_csv('./modules/criterias/banshi_desk_criteria.csv', sep=None, engine='python')
POINTS['banshi_desk'] = dict(zip(df['体验点二级分类英文'], df['英文描述']))
df = pd.read_csv('./modules/criterias/gangmu_desk_criteria.csv', sep=None, engine='python')
POINTS['gangmu_desk'] = dict(zip(df['体验点二级分类英文'], df['英文描述']))
df = pd.read_csv('./modules/criterias/ceiling_fan_criteria.csv', sep=None, engine='python')
POINTS['ceiling_fan'] = dict(zip(df['体验点二级分类英文'], df['英文描述']))

if __name__ == '__main__':
   print(POINTS.keys())