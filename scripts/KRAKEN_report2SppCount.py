import argparse, csv, time

parser = argparse.ArgumentParser(prog='ARGUMENTS', usage='%(prog)s [options]')
parser.add_argument('-i',     '--input',     type=str,    required = True,    help='Input file (K2_report.txt) obtained with command: kraken2 --db Kraken2_DB --threads 12 --use-names --output K2_r2lca_sciNames.txt --report K2_report.txt query.fastq')
parser.add_argument('-o',     '--output',    type=str,    required = True,    help='Output file with species count and their relative abundances.')
options = parser.parse_args()

def main():

  #print('\n---------------------------------------------------------------------------')
  #print('             Turn KRAKEN2 report output to species counts ')
  #print('             and relative proportion')
  #print('---------------------------------------------------------------------------')

  f = open(options.input,"r")

  outDic = dict()  
  for line in f:
    lineParts = line.split('\t')

    count = lineParts[1]
    ref = lineParts[len(lineParts)-1].strip('\n\r').strip(' ')
    sciLevel = lineParts[3]
    if sciLevel == 'S': outDic[ref] = int(count)
    if ref == 'unclassified': unclassified = int(count)
    if ref == 'root': root = int(count) 
  f.close()

  total_assign_reads = sum(int(val) for val in outDic.values())

  csvoutput = open(options.output, 'w')
  writer = csv.writer(csvoutput, delimiter=';', quoting=csv.QUOTE_NONE, escapechar='\\')
  writer.writerow(['unclassified (taxid 0)', int(unclassified+root-total_assign_reads), 0]) # Write first line with unclassified reads at species level
  
  for key, val in sorted(outDic.items()):
    writer.writerow([key, val, '%.5f' % float(float(val)/float(total_assign_reads))])
  
  csvoutput.close()
  return

main()
