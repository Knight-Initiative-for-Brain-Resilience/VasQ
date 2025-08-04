import difflib
import json
import openai
import os
import pandas as pd
import re
import requests

# Set gloabl variables
global func_flag
global init_flag
func_flag = False
init_flag = True

# Set API key
openai.api_key = os.getenv("OPENAI_API_KEY")

### Helper Functions ###

# Call OpenAI API
def call_api(history, functions=None):
    chat_co = openai.chat.completions.create(
        model="gpt-4-turbo", messages=history,
        functions=functions, temperature=0.2, top_p=0.4
    )
    return chat_co.choices[0].message

# Update chat history
def update_history(history, role, content):
    message = {"role": role, "content": content}
    history.append(message)

# Initialize chat
def initialize(history):
    global init_flag
    
    system_prompt = "You are a neuroscience research assistant. You answer \
        scientific questions using multiple resources and should draw on prior \
        conversation history to maintain coherence. When details are \
        unspecified, infer them based on recent context (e.g., assume the same \
        cell type if the user referenced it most recently). You have access to \
        the following tools to support scientific inquiry: \n1. \
        gene_expression Function: Returns gene expression and protein \
        prevalence data for specific cell types and brain vasculature regions, \
        based on single-nucleus RNA sequencing (snRNA-seq) from the Brain \
        Resilience Laboratory at Stanford University. \n2. Biomedical \
        Knowledge Graph: A curated knowledge graph based on SPOKE (from UCSF), \
        containing molecular and disease biology relationships. \n3. Google \
        Search API: Allows web search for up-to-date biomedical information. \
        \n4. Pretrained Scientific Knowledge: You may also draw on your own \
        scientific knowledge acquired during pre-training. \nWHEN TO CALL \
        gene_expression: \n- If the user asks about gene expression or \
        protein prevalence in a cell type and/or brain region, and does NOT \
        specify a tissue type, ASSUME they mean brain vasculature and call the \
        function. \n- If the user asks: `Is gene X among the top Y expressed \
        genes in brain region Z?`, check all listed genes for each of the \
        specified brain regions using the function. \n- If the user explicitly \
        mentions vasculature (e.g., `in vasculature`, `vascular tissue`, \
        `blood vessels`), call the function. \nResponse Notes: The numbers \
        next to genes are their expression rank. Always include data numbers \
        in your response. \n- If the data returned includes some genes \
        mentioned in the user query, but not all, ASSUME the missing genes do \
        not appear in the top 1000 expressed genes for the given region and/or \
        cell type and state that in your answer. \n- If the data returned only \
        relates to a brain region, you MUST state in your response: `This \
        answer reflects all cell types across the specified brain region. \n- \
        If the data returned only relates to a cell type, you MUST state: \
        `This answer reflects the specified cell type across all brain \
        regions.` \n- If tissue type is unspecified but both cell type and \
        brain region are given, add: `Since you specified a cell type and \
        brain region but did not mention tissue type, I’ve assumed brain \
        vasculature.` \n- In all cases, include: `This answer is based on \
        single-nucleus data from the Brain Resilience Lab at Stanford \
        University.` \nWHEN NOT TO CALL gene_expression: \n- If the user \
        explicitly says `not in vasculature`, `non-vascular`, or specifies a \
        different tissue (e.g., `nervous tissue`, `gray matter`, \
        `parenchyma`), DO NOT call the function. \n- DO NOT call the function \
        for queries unrelated to gene expression levels in specific cell types \
        or brain regions, even if they mention particular genes. \n- Instead, \
        use the knowledge graph, Google web search, or your own pretrained \
        knowledge to answer. \nWHEN TO CALL query_kg_rag: \n- If the user \
        mentions any disease by name in their query you MUST call \
        query_kg_rag. \nResponse strategy: \n- Prioritize information from \
        tools in the following order: \n1. gene_expression \n2. Biomedical \
        knowledge graph \n3. Web results (Google Search API) \n4. Parametric \
        (pretrained) knowledge \n- Always include information from each tool \
        used in the response. \n- Summarize the findings from each tool so the \
        user can ask follow-up questions if needed. \n- Cite all sources when \
        using the knowledge graph or web search. (e.g., `This data is from \
        NCBI and ChEMBL` or `Visit this website for more info...`) \n- Format \
        all responses clearly and professionally for a scientific audience. \
        \nAdditional Expectations: \n- Reason through ambiguous queries. \n- \
        Clarify assumptions explicitly in your replies. \n- Clearly state the \
        origin of any scientific data used. \n- Keep your answers as concise \
        as possible."

    update_history(history, "system", system_prompt)
    init_flag = False

# Call function from chat
def func_call(user_input, chat_message, history):
    global func_flag
    func_flag = True
    content = None

    func_name = chat_message.function_call.name
    print("Calling", func_name, "...")
    args = {"user_input":user_input}
    content = globals()[func_name](**args)
        
    func_flag = False
    return content

### Gene Expression Functions ###

# Extract cell types and regions
def extract_entities(user_input):

    cell_types = [
        "Arteriole", "Artery", "Astrocyte", "Capillary", "Endothelial", 
        "Epithelial", "Fenestrated Endothelial", "Fibroblast", "Large Artery", 
        "Microglia Macrophage or T Cell", "Neuron", "Oligodendrocyte", 
        "Oligodendrocyte Precursor", "Pericyte", "Smooth Muscle", "Vein", 
        "Venule"
    ]
    regions = [
        "Amygdala", "Anterior Cerebral Artery", 
        "Basilar Artery / Circle of Willis", "Cerebellum", "Choroid Plexus", 
        "Cingulum", "Corpus Callosum", "Cuneus", 
        "Dorsolateral Prefrontal Cortex", "Entorhinal Cortex", "Fornix", 
        "Fusiform Gyrus", "Hippocampus", "Inferior Frontal Gyrus",
        "Inferior Parietal Lobule", "Inferior Temporal Gyrus", "Insula", 
        "Lateral Occipital Cortex", "Lateral Temporal Gyrus", "Leptomeninges", 
        "Lingual Gyrus", "Midbrain", "Middle Cerebral Artery",
        "Middle Temporal Gyrus", "Midfrontal Anterior Watershed", 
        "Olfactory Bulb", "Orbitofrontal Cortex", "Parahippocampal Gyrus", 
        "Periventricular White Matter", "Pons", "Posterior Cingulate Cortex",
        "Posterior Watershed", "Precuneus", "Spinal Cord", 
        "Superior Frontal Gyrus and Rostromedial", "Superior Parietal Lobule", 
        "Superior Temporal Gyrus", "Supramarginal Gyrus", "Thalamus",
        "White Matter Anterior Watershed"
    ]

    def match_entities(user_input, entities):
        found = []
        words = re.findall(r"\w+", user_input.lower())

        for entity in entities:
            item = entity.lower()
            pattern = rf"\b{re.escape(item)}(es|s)?\b"
            if re.search(pattern, user_input.lower()):
                found.append(entity)
                continue
            for word in words:
                if difflib.SequenceMatcher(None, item, word).ratio() > 0.8:
                    found.append(entity)
                    break
        return found

    cell_matches = match_entities(user_input, cell_types)
    region_matches = match_entities(user_input, regions)
    return cell_matches, region_matches

# Extract genes
def extract_genes(user_input):
    system_prompt = "You are an expert molecular biologist. Extract *all* \
        human gene symbols or gene names mentioned in the most recent user \
        input. These may be short (e.g., APOE) or longer \
        transporter/receptor-style names like SLC16A1 or SLC2A1. Return only a \
        Python list (e.g. ['APOE', 'SLC16A1', 'INSR']). DO NOT return any \
        genes if the user doesn't specify any by name."

    response = openai.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ],
        temperature=0.2, top_p=0.4
    )

    raw_text = response.choices[0].message.content.strip()
    genes = eval(raw_text)
    if isinstance(genes, list):
        return genes
    else:
        return []

# Clarify regions
def all_regions(user_input):
    system_prompt = "You are a helpful assistant. Determine if the user is \
        asking about ALL brain regions, not just a subset. If the user \
        mentions comparisons like 'other brain regions', 'any other regions', \
        or 'higher/lower than elsewhere', assume they want to consider ALL \
        regions for comparison. Examples that should return True: 'across all \
        regions', 'in the whole brain', 'higher than other regions'. Examples \
        that should return False: 'in the hippocampus and amygdala only'. \
        Return ONLY the word True or False (as a Python boolean)."

    response = openai.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ],
        temperature=0, top_p=0.4
    )

    raw_text = response.choices[0].message.content.strip()
    normalized = raw_text.lower()
    if "true" in normalized:
        return True
    elif "false" in normalized:
        return False
    else:
        return False

# Format data extraction properties
def extract_format(cell_types=None, regions=None, entities=None, column=None):
    if entities and column:
        subset = lambda df: df[df[column].isin(entities)]
        form = lambda row: f"{row[column]}, {row.gene}, rank {row.rank}"
    else:
        subset = (
            lambda df: df[
                 df["cell_type"].isin(cell_types) & df["tissue"].isin(regions)
            ]
        )
        form = (
            lambda row: f"{row.cell_type}, {row.tissue}, "
            f"{row.gene}, rank {row.rank}"
        )
    return subset, form

# Get gene expression data
def gene_expression(user_input):

    # Extract entities
    all_regions_flag = all_regions(user_input)
    cell_types, regions = extract_entities(user_input)
    gene_names = extract_genes(user_input)

    # Choose dataset to load
    if cell_types and (regions or all_regions_flag):
        path = "data/c2s_ct.csv"
        subset, form = extract_format(
            cell_types=cell_types, 
            regions=([] if all_regions_flag else regions)
        )
    elif cell_types:
        path = "data/c2s_c.csv"
        subset, form = extract_format(
            entities=cell_types, 
            column="cell_type"
        )
    elif regions or all_regions_flag:
        path = "data/c2s_t.csv"
        subset, form = extract_format(
            entities=([] if all_regions_flag else regions), 
            column="tissue"
        )
    else:
        return "No matching gene data for cell type and/or region"

    # Load and filter dataset
    df = pd.read_csv(path)
    if not all_regions_flag:
        df = subset(df)
    if gene_names:
        df = df[df["gene"].str.upper().isin([g.upper() for g in gene_names])]
    if df.empty:
        return "No matching gene data found for the specified query."

    # Group data
    group_keys = [col for col in ("cell_type", "tissue") if col in df.columns]
    # grouped = df.groupby(group_keys)
    grouped = df.groupby(
        group_keys[0]) if len(group_keys) == 1 else df.groupby(group_keys
    )

    # Build headers
    formatted_sections = []
    for group_vals, group_df in grouped:
        if not isinstance(group_vals, tuple):
            group_vals = (group_vals,)
        group_dict = dict(zip(group_keys, group_vals))
        if "cell_type" in group_dict and "tissue" in group_dict:
            header = f"Gene data for {group_dict['cell_type']} "
            f"in {group_dict['tissue']}"
        elif "cell_type" in group_dict:
            header = f"Gene data for {group_dict['cell_type']}"
        else:
            header = f"Gene data for {group_dict['tissue']}"
        formatted_sections.append(header)

        # Add gene data
        for _, row in group_df.iterrows():
            formatted_sections.append(f"{row['gene']} {row['rank']}")
        formatted_sections.append("")

    return "\n".join(formatted_sections).strip()

### KG-RAG Functions ###

# Invoke KG_RAG
def query_kg_rag(user_input):
    response = requests.post(
        "http://host.docker.internal:5005/query",
        json={"query": user_input}
    )
    return response.json().get("result", "").strip()

### Search Functions ###

# Search Google
def search_google(query):

    # Define credentials and parameters
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    SE_ID = os.getenv("SEARCH_ENGINE_ID")
    url = "https://www.googleapis.com/customsearch/v1"
    params = {"key": GOOGLE_API_KEY, "cx": SE_ID, "q": query, "num": 5}

    # Generate response
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    # Format output
    formatted_results = ""
    for idx, item in enumerate(data.get("items", []), start=1):
        title = item.get("title", "No Title")
        link = item.get("link", "No Link")
        snippet = item.get("snippet", "")
        formatted_results += f"{idx}. {title}\n{link}\n{snippet}\n\n"
    return formatted_results

### Function Descriptions ###

functions = [
    {
        "name": "gene_expression",
        "description": "Collects information on gene expression rankings by \
        cell type and region in brain vasculature.",
        "parameters": {
            "type": "object",
            "properties": 
                {"user_input":{
                    "type":"string","description":"Full text of user input."}
                },
            "required": ["user_input"],
        }
    },
    {
        "name": "query_kg_rag",
        "description": "Collects biomedical information related to diseases \
        mentioned in user queries.",
        "parameters": {
            "type": "object",
            "properties": 
                {"user_input":{
                    "type":"string","description":"user input"}
                },
            "required": ["user_input"],
        }
    }
]

### Main Chat Function ###

# Chat between user and chatbot
def chat(user_input, history):
    global func_flag, init_flag

    # Initialize chat
    if init_flag:
        history.clear()
        initialize(history)

    # Update chat with user input
    update_history(history, "user", user_input)

    # Select and access augmentation tools
    retrieved_info = None
    chat_message = call_api(history, functions)
    if chat_message.function_call:
        retrieved_info = func_call(user_input, chat_message, history)
    if retrieved_info == None:
        print ("Calling Google Search API...")
        retrieved_info = search_google(user_input)

    # Update session history and generate response
    update_history(history, "system", retrieved_info)
    final_message = call_api(history).content
    update_history(history, "assistant", final_message)
    return final_message, history