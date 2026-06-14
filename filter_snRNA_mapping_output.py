import pysam
import argparse
import pandas as pd

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="BS_hisat2",fromfile_prefix_chars='@',description=__doc__,formatter_class=argparse.RawTextHelpFormatter)
    #Required
    group_required = parser.add_argument_group("Required")
    group_required.add_argument("-i",dest="BAM",required=True,help="Input BAM")
    group_required.add_argument("-o",dest="output",required=True,help="Output CSV")
    group_required.add_argument("--db",dest="database",required=False,help="snRNA/snoRNA database")
    group_required.add_argument("--genelist",dest="genelist",required=False,help="gene names")
    options = parser.parse_args()

    # enst_to_name = {}
    name_to_enst = {}
    with open(options.genelist, "r") as input:
        for line in input.readlines():
            line = line.strip().split("\t")
            name_to_enst[line[1]] = line[2]
    data = {}    
    ref_to_snRNA = {} # snRNA > read > base
    with open(options.database, "r") as input:
        for line in input.readlines():
            line = line.strip().split("\t")
            ref_to_snRNA[line[0]] = line[-1]

    with pysam.AlignmentFile(options.BAM, "rb") as BAM:
        for read in BAM:
            if read.is_read1 and read.reference_start == 0:
                if "S" not in read.cigarstring and "I" not in read.cigarstring and "D" not in read.cigarstring and len(read.query_sequence) >= 35 and read.is_secondary == False:
                    if read.get_tag("AS") >= -5:
                        UMI = read.query_name.split("_")[-1]
                        if read.reference_name in ref_to_snRNA:
                            data[(UMI, ref_to_snRNA[read.reference_name])] = read.query_sequence[0]
                            # print(UMI, data[read.reference_name], read.query_sequence[0])
data_out = {}
for key in ref_to_snRNA.values():
    data_out[key] = {"A": 0, "T": 0, "C": 0, "G": 0, "N": 0}

for key, values in data.items():
    data_out[key[1]][values] += 1

DF = pd.DataFrame(data_out).T
DF["level"] = DF["A"] / (DF["A"] + DF["G"])
DF.to_csv(options.output)

