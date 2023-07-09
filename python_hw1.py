import pandas as pd


def ParseGeneFile(file_path):
    data = {}
    file = open(file_path)
    for readline in file:
        if readline.startswith(">"):
            name = readline.replace(">", "").strip().split(" gene=")
            data[name[0]] = name[1]
    return data




path = "c_elegans.PRJNA13758.WS289.mRNA_transcripts.fa"
GeneData = ParseGeneFile(path)


output_frame : pd.DataFrame = pd.DataFrame(columns=["Gene_ID", "transcript_ID", "# of transcripts"])

print(1)

# test github