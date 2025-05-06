import os
import pandas as pd

top = r'D:\Academics\Sem_2\EE_691_RnD_Project\Git\96171d81-6aab-4a58-bdf4-2de8fa3e48f3\CSVS'

data_record = {'path':[], 'slide_name':[],'label':[]}
for root, directories, files in os.walk(top, topdown=False):
    for name in files:
        print(root)
        print(name)
        data_record['slide_name'].append(name)
        data_record['path'].append(os.path.join(root, name))
        data_record['label'].append(root.split('/')[-1])

df = pd.DataFrame(data_record)

#df.label[df.label=='Benign']=0
df.label[df.label=='Immune Cells']=0
#df.label[df.label=='Stroma']=1
df.label[df.label=='Tumor']=1
#df.label[df.label=='Necrosis']=3
#df.label[df.label=='Debris']=3
#df.label[df.label=='Inflammatory']=4
#df.label[df.label=='Muscle']=5


df.to_csv('data_target_test.csv',index=False)

        