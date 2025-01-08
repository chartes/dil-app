import argparse
import pandas as pd

# usage : python convert_csv_to_tsv.py data/tables_to_migrate/tables_to_migrate.csv data/tables_to_migrate/tables_to_migrate.tsv

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert CSV to TSV')
    parser.add_argument('input', help='Input CSV file')
    parser.add_argument('output', help='Output TSV file')
    args = parser.parse_args()

    df = pd.read_csv(args.input, sep=';', encoding='utf-8')
    df.to_csv(args.output, sep='\t', index=False)
