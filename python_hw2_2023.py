from python_hw2_2022 import Parse_File, Find_Location, Split_Lower, Split_Upper, Append_TO_Dataframe, DataName
import pandas as pd

def main():
    path = "spliced+UTRTranscriptSequence_Y40B10A.2a.1.fasta"
    parsed_data = Parse_File(path)

    cds_data = Split_Upper(parsed_data[0])
    intron_and_utr_data = Split_Lower(parsed_data[0])

    cds_location = Find_Location(parsed_data[0], cds_data)
    utr_location = Find_Location(parsed_data[0], intron_and_utr_data)
    utr5 = [utr_location[0]]
    utr3 = [utr_location[1]]

    output_frame = pd.DataFrame(columns= ['名稱', '起始位置', '結束位置', '長度'])

    output_frame = Append_TO_Dataframe(output_frame, utr5, 3)
    output_frame = Append_TO_Dataframe(output_frame, cds_location, 5)
    output_frame = Append_TO_Dataframe(output_frame, utr3, 4)

    output_frame.to_csv("2023hw2_output.csv")



if __name__ == "__main__":
    main()
