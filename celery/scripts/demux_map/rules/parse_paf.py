import argparse, csv
from Bio import SeqIO
from collections import Counter

def read_barcoding_summary(barcoding_summary_file, reads_dict: dict):
    # barcoding_summary_file = 'PAE36018_pass_96513dd9_1468_barcoding_summary.txt'
    fi = open(barcoding_summary_file)
    reader = csv.DictReader(fi, delimiter='\t')
    for row in reader:
        read_id = row['read_id']
        barcode = row['barcode_full_arrangement'] if not row['barcode_arrangement'] == 'unclassified' else 'none'
        reads_dict.setdefault(read_id, ['none', 'none'])[0] = barcode.split('_')[0]
    fi.close()


def read_fastq(fastq_file, reads_dict: dict):
    for record in SeqIO.parse(fastq_file, "fastq"):
        header = dict()
        for i in str(record.description).split(' '):
            if i.find('=') == -1: continue
            info = i.split('=')
            header[info[0]] = info[1]
        reads_dict.setdefault(record.id, ['none', 'none'])[1] = header.get('start_time', 'none')


def take_appropriate_cigar_action(counter, last_symbol, number):
    if last_symbol == ":":
        counter[last_symbol] += int(number)
    elif last_symbol == "*":
        counter[last_symbol] += 1
    else:
        counter[last_symbol] += len(number)


def parse_cigar_for_matches_and_mismatches(cigar):
    cigar_counter = Counter()
    cigar = cigar[5:]  # removes the cs:Z: from the beginning of the cigar
    last_symbol = None
    number = ''
    for i in cigar:
        if i in [":", "*", "+", "-"]:
            symbol = i

            if last_symbol:
                take_appropriate_cigar_action(cigar_counter, last_symbol, number)
                last_symbol = symbol
                number = ''
            else:
                last_symbol = symbol
        else:
            number += i
    take_appropriate_cigar_action(cigar_counter, last_symbol, number)
    matches = cigar_counter[":"]
    mismatches = cigar_counter["*"]
    return matches, mismatches


def calculate_genetic_identity(cigar):
    matches, mismatches = parse_cigar_for_matches_and_mismatches(cigar)
    return mismatches, matches / (matches + mismatches)


def check_identity_threshold(mapping, min_identity):
    if float(min_identity) < 1:
        min_id = float(min_identity)
    else:
        min_id = float(min_identity) / 100

    if mapping["identity"] >= min_id:
        return True
    else:
        return False


def parse_line(line, reads_dict):
    values = {}
    tokens = line.rstrip('\n').split('\t')
    values["read_name"], values["read_len"] = tokens[:2]
    if values["read_name"] in reads_dict:
        values["barcode"], values["start_time"] = reads_dict[
            values["read_name"]]  # if porechop didn't discard the read
    else:
        values["barcode"], values["start_time"] = "none", "?"  # don't have info on time or barcode
    values["query_start"] = tokens[2]
    values["query_end"] = tokens[3]
    values["ref_hit"], values["ref_len"], values["coord_start"], values["coord_end"], values["matches"], values[
        "aln_block_len"] = tokens[5:11]
    if values["ref_hit"] != "*":
        mismatches, identity = calculate_genetic_identity(tokens[-1])
        values["mismatches"] = mismatches
        values["identity"] = identity
    else:
        values["mismatches"] = 0
        values["identity"] = 0
    return values


def write_mapping(report, mapping, counts, min_identity):
    if mapping["ref_hit"] == '*' or mapping["ref_hit"] == '?':
        # '*' means no mapping, '?' ambiguous mapping (i.e., multiple primary mappings)
        mapping['coord_start'], mapping['coord_end'] = 0, 0
        if (mapping["ref_hit"] == '*'):
            counts["unmapped"] += 1
        else:
            counts["ambiguous"] += 1
    if check_identity_threshold(mapping, min_identity):
        counts["total"] += 1
        mapping_length = int(mapping['matches']) + int(mapping['mismatches'])
        report.write(f"{mapping['read_name']},{mapping['read_len']},{mapping['start_time']},"
                     f"{mapping['barcode']},{mapping['ref_hit']},{mapping['ref_len']},"
                     f"{mapping['coord_start']},{mapping['coord_end']},{mapping['matches']},{mapping_length}")
    else:
        counts["unmapped"] += 1
        report.write(f"{mapping['read_name']},{mapping['read_len']},{mapping['start_time']},"
                     f"{mapping['barcode']},*,0,0,0,0,0")
    report.write("\n")


def parse_paf(paf, report, reads_dict, min_identity):
    # This function parses the input paf file
    # and outputs a csv report containing information relevant for RAMPART and barcode information
    # read_name,read_len,start_time,barcode,best_reference,start_coords,end_coords,ref_len,matches,aln_block_len,ref_option1,ref_option2
    counts = {
        "unmapped": 0,
        "ambiguous": 0,
        "total": 0
    }

    with open(str(paf), "r") as f:
        last_mapping = None
        for line in f:

            mapping = parse_line(line, reads_dict)

            if last_mapping:
                if mapping["read_name"] == last_mapping["read_name"]:
                    # this is another mapping for the same read so set the original one to ambiguous. Don't
                    # set last_mapping in case there is another mapping with the same read name.
                    last_mapping['ref_hit'] = '?'
                else:
                    write_mapping(report, last_mapping, counts, min_identity)
                    last_mapping = mapping
            else:
                last_mapping = mapping

        # write the last last_mapping
        write_mapping(report, last_mapping, counts, min_identity)

    try:
        prop_unmapped = counts["unmapped"] / counts["total"]
        print("Proportion unmapped is {}".format(prop_unmapped))
        if prop_unmapped > 0.95:
            print("\nWarning: Very few reads have mapped (less than 5%).\n")
    except:
        print("Probably can't find the records.")  # division of zero the error


def parse_args():
    parser = argparse.ArgumentParser(description='Parse barcode info and minimap paf file, create report.')
    parser.add_argument('-p', '--paf', help="paf file")
    parser.add_argument('-f', '--fastq', help="fastq file")
    parser.add_argument('-s', '--summary', help="barcoding summary file")
    parser.add_argument('-r', '--report',  help="report file(csv)")
    parser.add_argument('-m', '--min_identity', default=0.8, type=float, help="minimum identity")
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    print(args)
    with open(str(args.report), "w") as csv_report:
        read_dict = dict()
        read_barcoding_summary(args.summary, read_dict)
        read_fastq(args.fastq, read_dict)
        csv_report.write(
            f"read_name,read_len,start_time,barcode,best_reference,ref_len,start_coords,end_coords,num_matches,mapping_len\n")
        parse_paf(args.paf, csv_report, read_dict, args.min_identity)
