import argparse, csv

parser = argparse.ArgumentParser(prog='ARGUMENTS', usage='%(prog)s [options]')
parser.add_argument('-i',     '--input',              type=str,    required = True,     help='Input file (MEGAN_r2c_taxID.txt) obtained with command: rma2info -r2c Taxonomy -n False -i MEGAN.rma > MEGAN_r2c_taxID.txt')
parser.add_argument('-t',     '--input_c2c_taxId',    type=str,    required = True,     help='Input file (MEGAN_c2c_taxID.txt) obtained with command: rma2info -c2c Taxonomy -r -n False -i MEGAN.rma > MEGAN_c2c_taxID.txt')
parser.add_argument('-o',     '--output',             type=str,    required = True,     help='Output file containing only species')
options = parser.parse_args()

def get_species_taxId():
  speciesList = list()

  f = open(options.input_c2c_taxId, "r")  
  for line in f:
    lineParts = line.split('\t')
    if lineParts[0] == "S": speciesList.append(lineParts[1])
  f.close()
  return(speciesList)

def main():
  
  #print('\n---------------------------------------------------------------------------')
  #print('             Turn MEGAN assignment output (-r2c) of LCA taxa to ')
  #print('             species-rank assignment')
  #print('---------------------------------------------------------------------------')

  taxIdSppList = get_species_taxId()

  f = open(options.input, "r")
  reader = csv.reader(f, delimiter='\t')

  csvoutput = open(options.output, 'w')
  writer = csv.writer(csvoutput, delimiter='\t', quoting=csv.QUOTE_NONE, escapechar='\\')

  for line in reader:
    if line[1] in taxIdSppList: writer.writerow(line)

  csvoutput.close()
  f.close()
  return
 
main()
