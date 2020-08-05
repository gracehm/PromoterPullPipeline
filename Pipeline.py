import pandas as pd
from Bio import SeqIO
from Bio.Seq import Seq
from pathlib import Path



"""
Description: when invoked, the main method will parse through a user input FASTA gene list including the protein FUNCTION exactly as seen in the annotation file, as well as the 
protein sequence for each gene of interest.  It will also parse the .xls and contigs file associated with the PATRIC annotation service for a genome.  These should have the same
prefix (before the file type) and be stored in a directory separate from the genelist. 

The program will pull all promoter sequences (500bp or until end of contig) and report out for each gene and each genome in a FASTA format. 

See below where to input your paths for your input files, and see code comments if you wish to change the number of base pairs pulled.
"""
def main (genelist, annotation, contigsfilepath):
    df=pd.read_excel(annotation, header=0, usecols= "A,E,F,G,H,O") #read annotation file
    with open(genelist) as genelist: #read gene list
        id = []
        seq = []

        for seqs in SeqIO.parse(genelist, 'fasta'): #go through FASTA file and separate the ID from the sequence, store in lists.
            id.append(seqs.description)
            seq.append(seqs.seq)

    filtered=df[df['function'].isin(id)] #extract the genes of interest
    neg = filtered[filtered['strand'] == '-']
    pos = filtered[filtered['strand'] == '+']

    with open("promoterseq.fasta", 'a') as write:  #output file is created here, can name it however you wish.  The file will be appended, so you will need to remove or clear the file
                                                    # each time you run this code if you do not want the results appended, or change the permission to 'w'.

        with open(contigsfilepath) as contigs: #opens the contigs files as "contigs"
            for seqs in SeqIO.parse(contigs, 'fasta'):
                for i in range(0, neg.shape[0]):
                    if seqs.id == neg.iloc[i]['contig_id']:
                        start = neg.iloc[i]['start']
                        if start+500<=len(seqs.seq):   #change the 500 to however many bp upstream of the coding region you would like

                            promoter=str(seqs.seq[start:start+500]) #change the 500 to however many bp upstream of the coding region you would like
                            promoter=Seq(promoter)
                            promoter=promoter.reverse_complement()
                            write.write('>'+seqs.id+' '+id[i-1]+'\n'+str(promoter)+'\n')
                        else:
                            promoter = str(seqs.seq[start:start+len(seqs.seq)])
                            promoter=Seq(promoter)
                            promoter = promoter.reverse_complement()
                            write.write('>'+seqs.id+' '+id[i-1]+'\n'+str(promoter)+'\n')
                for j in range(0, pos.shape[0]):
                    if seqs.id == pos.iloc[j]['contig_id']:
                        start = pos.iloc[j]['start']
                        if start-500>=0:    #change the 500 to however many bp upstream of the coding region you would like
                            promoter = seqs.seq[start - 500:start]   #change the 500 to however many bp upstream of the coding region you would like
                            write.write('>' + seqs.id + ' ' + id[j] + '\n' + str(promoter)+'\n')
                        else:
                            promoter = seqs.seq[0:start]
                            write.write('>' + seqs.id + ' ' + id[j] + '\n' + str(promoter) + '\n')



base_dir= Path('D:\\Example_folder') #insert your path to the genome FASTAs and .xls files here
gene_list = Path('D:\\genelist_changeme.fasta') #insert path to the gene list FASTA file.
fasta_paths = base_dir.glob('*.fasta')
xls_paths = base_dir.glob('*.xls')
for fasta, xls in zip(fasta_paths, xls_paths):
    main(gene_list, xls, fasta)

