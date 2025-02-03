import pandas as pd

file_path = "PC_Cyan_data_processed.csv"  #
data = pd.read_csv(file_path)

data['Intensity'] = data['Intensity'] * 3

data.to_csv(file_path, index=False)

print("Intensity double")