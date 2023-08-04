import pandas as pd
import time


def ParseGeneFile(file_path):
    data = {}
    file = open(file_path)
    for readline in file:
        if readline.startswith(">"):
            name = readline.replace(">", "").strip().split(" gene=")
            data[name[0]] = name[1]
    return data


def Transform_To_Result_Format(Data):
    result_dict = {}
    for key, value in Data.items():
        if value not in result_dict:
            result_dict[value] = [key]  # 如果值不在字典中，則將值作為鍵，對應的鍵作為列表的值
        else:
            result_dict[value].append(key)
    return result_dict

start = time.perf_counter()
path = "/home/cosbi2/py_project/summer_training/c_elegans.PRJNA13758.WS289.mRNA_transcripts.fa"
GeneData = ParseGeneFile(path)
ResultData = Transform_To_Result_Format(GeneData)
SortedData = dict(sorted(ResultData.items(), key=lambda item: len(item[1]), reverse=True))

output_frame : pd.DataFrame = pd.DataFrame(columns=["Gene_ID", "transcript_ID", "# of transcripts"])

for keys, values in SortedData.items():
    output_frame.loc[len(output_frame)] = {"Gene_ID" : keys, "transcript_ID" : values, "# of transcripts" : str(len(values))}

output_frame.to_csv("hw1_output.csv", index= False)
end = time.perf_counter()
print( end-start )