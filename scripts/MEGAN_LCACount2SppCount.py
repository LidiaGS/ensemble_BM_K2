import argparse, csv, os

parser = argparse.ArgumentParser(prog='ARGUMENTS', usage='%(prog)s [options]')
parser.add_argument('-i',     '--input',     type=str,    required = True,    help='Input file (MEGAN_c2c_sciNames.txt) obtained with command: rma2info -c2c Taxonomy -r -n False -i MEGAN.rma > MEGAN_c2c_taxID.txt')
parser.add_argument('-o',     '--output',    type=str,    required = True,    help='Output file containing only species')

options = parser.parse_args()

def main():

  #print('\n---------------------------------------------------------------------------')
  #print('             Turn MEGAN count output to species counts ')
  #print('             and relative their proportion')
  #print('---------------------------------------------------------------------------')

  speciesList = list()
  total_assign_reads = 0

  f = open(options.input, "r")  
  for line in f:
    lineParts = line.split('\t')

    if lineParts[0] == "S": 
      speciesName = lineParts[1]
      assign_reads = float(lineParts[2].strip('\n\r'))
      total_assign_reads += assign_reads
      speciesList.append([speciesName, assign_reads])
  f.close()

  csvoutput = open(options.output, 'w')
  writer = csv.writer(csvoutput, delimiter=';', quoting=csv.QUOTE_NONE, escapechar='\\')
  for species in speciesList:
    writer.writerow([species[0], species[1], '%.5f' % float(float(species[1])/float(total_assign_reads))])
  csvoutput.close()

  return
 
main()
