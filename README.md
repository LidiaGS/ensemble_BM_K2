# ensemble_BM_K2

## 1. Introduction
Metagenomic classifiers used to assign reads to species are generally run with default parameters; such an approach does generate false positive detections (i.e., detects species that are not in a sample). 

Below there are the commands for the classification of reads to species with two metagenomic classifiers: <a href="https://www.sciencedirect.com/science/article/abs/pii/S0022283605803602?via%3Dihub" rel="nofollow" >BLASTn</a> followed by <a href="https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1004957">MEGAN6</a> (BM) and <a href="https://genomebiology.biomedcentral.com/articles/10.1186/s13059-019-1891-0">Kraken2</a> (K2). The final output of the pipelines are several files used to evaluate the results when the classifiers are used alone and also to ensemble the results from both classifiers.


## 2. Setup

### 2.1. Software

* Blast v2.10.0
* Kraken2 v2.0.8-beta
* MEGAN6 v6.18.11
* Python 3.7

### 2.2. Download and installation

Software can be downloaded using the following commands:

* This GitHub repository

```shell
git clone --recursive https://github.com/LidiaGS/ensemble_BM_K2.git ensemble_BM_K2

cd ensemble_BM_K2

mkdir tools && cd tools

export TOOLS_PATH=$(pwd)
```

* BLAST 

```shell
cd $TOOLS_PATH

wget https://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/2.10.0/ncbi-blast-2.10.0+-x64-linux.tar.gz

tar zxvpf ncbi-blast-2.10.0+-x64-linux.tar.gz

export PATH=$PATH:$TOOLS_PATH/ncbi-blast-2.10.0+/bin
```

* MEGAN6 

```shell
cd $TOOLS_PATH

wget https://software-ab.informatik.uni-tuebingen.de/download/megan6/MEGAN_Community_unix_6_18_11.sh

chmod +xrw MEGAN_Community_unix_6_18_11.sh

./MEGAN_Community_unix_6_18_11.sh

export PATH=$PATH:$TOOLS_PATH/MEGAN_Community_6_21_12/tools/
```

* Kraken2 

```shell
cd $TOOLS_PATH

wget https://github.com/DerrickWood/kraken2/archive/refs/tags/v2.0.8-beta.tar.gz

mv v2.0.8-beta.tar.gz kraken2-2.0.8-beta.tar.gz

tar zxvpf kraken2-2.0.8-beta.tar.gz

cd kraken2-2.0.8-beta

./install_kraken2.sh $TOOLS_PATH/kraken2-2.0.8-beta/kraken2-2.0.8-beta

export PATH=$PATH:$TOOLS_PATH/kraken2-2.0.8-beta/kraken2-2.0.8-beta
```


## 3. Pipelines command-lines and options

### 3.1. BLASTn + MEGAN6 classifier

For <code>blastn</code>, all reference genomes may be stored in a single file (<code>$BLAST_DB</code>). Importantly, the header of every sequence has to include a taxonomy identifier (taxID) to work with <code>MEGAN6</code>. For example, the header for a <i>Drosophila melanogaster</i> reference sequence may be “>Drosophila_melanogaster_taxid_7227”. All sequences’ identifier along with their taxID have to be stored in the taxid.txt file. The taxid.txt file is required during the database construction.

```shell
makeblastdb -in $BLAST_DB -parse_seqids -blastdb_version 5 -taxid_map taxid.txt -title "${BLAST_DB}.db" -out ${BLAST_DB}.db -dbtype nucl
```

To match the query samples (<code>query.fasta</code>) to <code>$BLAST_DB</code> use the following command:
```shell
blastn -db ${BLAST_DB}.db -query query.fasta -num_alignments 10 -out BLASTn.tab -outfmt 6 -num_threads 12
```

To parser the <code>blastn</code> output with <code>MEGAN6</code> using the lower-common ancestor (LCA) algorithm, use the following command:
```shell
blast2rma -f BlastTab -bm BlastN -alg naive -i BLASTn.tab -o MEGAN.rma
```

The <code>MEGAN6</code> output may be saved with three different output types using the following commands:
```shell
rma2info -c2c Taxonomy -r -n True -i MEGAN.rma > MEGAN_c2c_sciNames.txt

rma2info -c2c Taxonomy -r -n False -i MEGAN.rma > MEGAN_c2c_taxID.txt

rma2info -r2c Taxonomy -n False -i MEGAN.rma > MEGAN_r2c_taxID.txt
```

To retained only the assignments at the species level, use out the in-house python scripts with the following commands: 
```shell
python3.7 MEGAN_LCACounts2SppCounts.py -i MEGAN_c2c_sciNames.txt -o MEGAN_c2c_sp.txt

python3.7 MEGAN_LCAReads2SppReads.py -i MEGAN_r2c_taxID.txt -t MEGAN_c2c_taxID.txt -o MEGAN_r2c_spTaxID.txt
```

The <code>MEGAN_c2c_sp.txt</code> file contains the list of detected species and the total number of assigned reads to every species; the <code>MEGAN_r2c_spTaxID.txt</code> file contains the list of assigned reads to species and associates every read to the species' taxID. 


### 3.2. Kraken2 classifier

For Kraken2 custom database building, use the commands indicated below. Importantly, <code>Kraken2_DB</code> refers to the database name, <code>$REF_PATH</code> is the path to the folder where reference sequences are stored. The headers of the reference sequence must contain the taxID following the structure “>NNNN|kraken:taxid|XXXX”, where NNNN and XXXX are replaced by the accession number and species taxID code from NCBI, respectively. For example, the header of the mitogenome NC_024511.2 of <i>Drosophila melanogaster</i> is “>NC_024511.2|kraken:taxid|7227”.

```shell
kraken2-build --download-taxonomy --use-ftp --db Kraken2_DB --threads 12

for ref in ${REF_PATH}/*fna; do 
   kraken2-build --threads 12 --add-to-library $ref --db Kraken2_DB; 
done

kraken2-build --build --threads 12 --db Kraken2_DB
```

To clasify FASTQ samples (<code>query.fastq</code>) to the LCA use the following two commands: 
```shell
kraken2 --db Kraken2_DB --threads 12 --use-names --output K2_r2lca_sciNames.txt --report K2_report.txt query.fastq

kraken2 --db Kraken2_DB --threads 12 --output K2_r2lca_taxID.txt query.fastq
```

<code>K2_r2lca_sciNames.txt</code> file contains the list of reads together with their LCA assignment using the scientific names; the <code>K2_r2lca_taxID.txt</code> file contains the list of reads together with their LCA assignment using the taxID code; and <code>K2_report.txt</code> file contains the summary report.

To retain only the assignments at the species level, use our in-house python scripts with the following commands:

```shell
python3.7 KRAKEN_report2SppCount.py -i K2_report.txt -o K2_report_sp.txt

python3.7 KRAKEN_LCAReads2SppReads.py -t K2_report.txt -i K2_r2lca_taxID.txt -o K2_r2lca_spTaxID.txt
``` 

The <code>K2_report_sp.txt</code> file contains the list of detected species and the total number of assigned reads to that species; the <code>K2_r2lca_spTaxID.txt</code> file contains the list of assigned reads to species together with the taxID of that species. 


## 4. Authors
* Lidia Garrido-Sanz [lidia.garrido@uab.cat] 
* Miquel Àngel Senar
* Josep Piñol

## 5. Reporting bugs
All reports and feedbacks are highly appreciated. Please report any suggestion on GitHub or by email to lidia.garrido@uab.cat. 

## 6. Disclaimer
The authors provided the information and software in good faith. Under no circumstance shall authors and the Universitat Autònoma de Barcelona have any liability for any loss or damage of any kind incurred as a result of the use of the information and software provided. The use of this tool is solely at your own risk.

## 7. Citation
Coming soon.

