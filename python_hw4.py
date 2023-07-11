import json
from python_hw2_2022 import Parse_File, Split_Upper

def load_codon_table():
    with open('codon_table.json', 'r') as file:
        codon_table_data = json.load(file)
    return codon_table_data


def translationToProtein(cds_sequence: str, codon_dict: dict):
    cds_sequence = cds_sequence.replace("T", "U")
    # 從檔案中得到的資料是DNA的ATCG含氮鹼基，須將T轉換成U才是能夠轉譯的RNA序列。
    unit_set: list = [cds_sequence[i : i+3] for i in range(0, len(cds_sequence), 3)]
    # 將cds的序列每三個鹼基做切割並存入list中。
    result_list: list = [codon_dict[unit] for unit in unit_set]
    # 將切割完成的單元作為輸入找到在codon_table中的對應的胺基酸。
    result_list.pop(result_list.index("STOP"))
    # 將結果中代表中止的STOP訊號從胺基酸序列中刪除。
    result = "".join(result_list)

    return result


def main():
    codon_table = load_codon_table()

    path = "spliced+UTRTranscriptSequence_Y40B10A.2a.1.fasta"
    parsed_data = Parse_File(path)

    cds_data = Split_Upper(parsed_data[0])
    result = translationToProtein(cds_data[0], codon_table)
    
    print(result)
    print(len(result))


if __name__ == "__main__":
    main()