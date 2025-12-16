import os
import argparse
import pandas as pd
import pyarrow.ipc as ipc
from collections import defaultdict

# Mapping dictionary
mapping = {
    "1_Hip-EC": "Hippocampus", "2_Amygdala": "Amygdala", "3_Lingual-gyrus":
    "Lingual Gyrus", "4_Insula": "Insula", "5_PCC": 
    "Posterior Cingulate Cortex", "6_IPL-SMG": "Inferior Parietal Lobule", 
    "7_OFC": "Orbitofrontal Cortex", "8_STG": "Superior Temporal Gyrus", 
    "9_ITG": "Inferior Temporal Gyrus", "10_LTG": "Lateral Temporal Gyrus", 
    "11_IFG": "Inferior Frontal Gyrus", "12_Cuneus": "Cuneus", "13_ACC": 
    "Anterior Cingulate Cortex", "14_LOC": "Lateral Occipital Cortex", "15_SPL": 
    "Superior Parietal Lobule", "16_SFG-rmPFC": 
    "Superior Frontal Gyrus and Rostromedial", "17_DLPFC": 
    "Dorsolateral Prefrontal Cortex", "18_Pons": "Pons", "19_CB": "Cerebellum", 
    "20_Thalamus": "Thalamus", "21_Spinal-cord": "Spinal Cord", "22_Midbrain": 
    "Midbrain", "23_Watershed-ACA-MCA": "Midfrontal Anterior Watershed", 
    "24_Watershed-White-matter-ACA": "White Matter Anterior Watershed", 
    "25_Watershed-MCA-PCA": "Posterior Watershed", "26_PVWM": 
    "Periventricular White Matter", "27_Cingulum": "Cingulum", "28_Fornix": 
    "Fornix", "29_CC": "Corpus Callosum", "30_PHG": "Parahippocampal Gyrus", 
    "31_EC": "Entorhinal Cortex", "32_SMG": "Supramarginal Gyrus", 
    "33_Fusiform-gyrus": "Fusiform Gyrus", "34_PRCU": "Precuneus", "35_MTG": 
    "Middle Temporal Gyrus", "36_OB": "Olfactory Bulb", "37_CP": 
    "Choroid Plexus", "38_Leptomeninges": "Leptomeninges", "39_MCA": 
    "Middle Cerebral Artery", "40_ACA": "Anterior Cerebral Artery", "41_BA.CoW": 
    "Basilar Artery / Circle of Willis", "Arteriole": "Arteriole", "Artery": 
    "Artery", "Astrocyte": "Astrocyte", "Capillary_1": "Capillary", 
    "Capillary_2": "Capillary", "Capillary_3": "Capillary", "EndoMT1": 
    "Endothelial", "EndoMT2": "Endothelial", "Epithelial_1": "Epithelial", 
    "Epithelial_2": "Epithelial", "Epithelial_3": "Epithelial", 
    "Fenestrated_EC": "Fenestrated Endothelial", "Fibroblast_1": "Fibroblast", 
    "Fibroblast_2": "Fibroblast", "Fibroblast_3": "Fibroblast", "Fibroblast_4": 
    "Fibroblast", "Fibroblast_5": "Fibroblast", "Large_Artery": "Large Artery", 
    "Microglia_Macrophage_T": "Microglia Macrophage or T Cell", "Neuron": 
    "Neuron", "OPC": "Oligodendrocyte Precursor", "Oligodendrocyte": 
    "Oligodendrocyte", "Pericyte_1": "Pericyte", "Pericyte_2": "Pericyte", 
    "Pericyte_3": "Pericyte", "SMC_1": "Smooth Muscle", "SMC_2": 
    "Smooth Muscle", "SMC_3": "Smooth Muscle", "SMC_4": "Smooth Muscle", "Vein": 
    "Vein", "Venule": "Venule"
}

def read_arrow_files(directory):
    all_tables = []
    for filename in os.listdir(directory):
        if filename.endswith(".arrow"):
            try:
                with open(os.path.join(directory, filename), "rb") as f:
                    reader = ipc.open_stream(f)
                    for batch in reader:
                        all_tables.append(batch.to_pandas())
                print(f"✅ Read: {filename}")
            except Exception as e:
                print(f"❌ Failed to read {filename}: {e}")
    return pd.concat(all_tables, ignore_index=True) if all_tables else pd.DataFrame()

def apply_mapping(df):
    for col in ['cell_type', 'tissue']:
        if col in df.columns:
            df[col] = df[col].map(lambda x: mapping.get(x, x) if isinstance(x, str) else x)
    return df

def aggregate_cell_sentences(group_df, top_n=200):
    gene_score = defaultdict(float)
    for sentence in group_df['cell_sentence']:
        genes = sentence.split()
        for rank, gene in enumerate(genes):
            gene_score[gene] += 1 / (rank + 1)
    sorted_genes = sorted(gene_score.items(), key=lambda x: x[1], reverse=True)
    return [gene for gene, _ in sorted_genes[:top_n]]

def expand_and_save(grouped_df, group_cols, output_path, top_n=200):
    rows = []
    for name, group in grouped_df:
        genes = aggregate_cell_sentences(group, top_n=top_n)
        for rank, gene in enumerate(genes, start=1):
            row = {'gene': gene, 'rank': rank}
            if isinstance(name, tuple):
                for i, col in enumerate(group_cols):
                    row[col] = name[i]
            else:
                row[group_cols[0]] = name
            rows.append(row)
    ranked_df = pd.DataFrame(rows)
    ranked_df.to_csv(output_path, index=False)
    print(f"✔️ Saved ranked gene output to: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Read, map, aggregate, and rank gene mentions from Arrow files.")
    parser.add_argument("arrow_dir", help="Directory containing Arrow files")
    parser.add_argument("--max_genes", type=int, default=200, help="Max genes per group")
    args = parser.parse_args()

    df = read_arrow_files(args.arrow_dir)
    if df.empty:
        print("⚠️ No valid Arrow data found.")
        return

    df = apply_mapping(df)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    ranked_dir = os.path.join(script_dir, "200")
    os.makedirs(ranked_dir, exist_ok=True)

    # Expand by cell_type
    if "cell_type" in df.columns:
        expand_and_save(df.groupby("cell_type"), ["cell_type"], os.path.join(ranked_dir, "c2s_c.csv"), args.max_genes)

    # Expand by tissue
    if "tissue" in df.columns:
        expand_and_save(df.groupby("tissue"), ["tissue"], os.path.join(ranked_dir, "c2s_t.csv"), args.max_genes)

    # Expand by cell_type + tissue
    if "cell_type" in df.columns and "tissue" in df.columns:
        expand_and_save(df.groupby(["cell_type", "tissue"]), ["cell_type", "tissue"], os.path.join(ranked_dir, "c2s_ct.csv"), args.max_genes)

if __name__ == "__main__":
    main()