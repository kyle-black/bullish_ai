import pandas as pd

data1 = pd.read_csv('p022_names.txt', delimiter=',')


dataframe1 = pd.DataFrame(data=data1)

print(dataframe1)
