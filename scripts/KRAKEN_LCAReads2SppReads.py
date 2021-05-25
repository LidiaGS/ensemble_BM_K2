import argparse, csv

parser = argparse.ArgumentParser(prog='ARGUMENTS', usage='%(prog)s [options]')
parser.add_argument('-i',     '--input',           type=str,    required = True,     help='Input file (K2_r2lca_taxID.txt) obtained with command: kraken2 --db Kraken2_DB --threads 12 --output K2_r2lca_taxID.txt query.fastq')
parser.add_argument('-t',     '--input_report',    type=str,    required = True,     help='Input file (K2_report.txt) obtained with command: kraken2 --db Kraken2_DB --threads 12 --use-names --report K2_report.txt query.fastq')
parser.add_argument('-o',     '--output',          type=str,    required = True,     help='Output file containing only species')
options = parser.parse_args()

def get_species_taxId():
  speciesList = list()

  f = open(options.input_report,"r")
  
  for line in f:
    lineParts = line.split('\t')
    sciLevel = lineParts[3]

    if sciLevel == 'S': speciesList.append(lineParts[4])
  
  f.close()
  return(speciesList)


def main():

  #print('\n---------------------------------------------------------------------------')
  #print('             KRAKEN2 output the individual assignment of reads with ')
  #print('             LCA, so, only reads assigned to species rank are retained')
  #print('---------------------------------------------------------------------------')

  taxIdSppList = get_species_taxId()

  f = open(options.input, "r")
  reader = csv.reader(f, delimiter='\t')

  csvoutput = open(options.output, 'w')
  writer = csv.writer(csvoutput, delimiter='\t', quoting=csv.QUOTE_NONE, escapechar='\\')

  for line in reader:
    if line[2] in taxIdSppList: writer.writerow(line)

  csvoutput.close()
  f.close()
  return

main()
