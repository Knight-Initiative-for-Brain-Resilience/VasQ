# 🧬 About VasQ

**VasQ** is a custom AI-powered chat system designed to support complex biomedical reasoning, particularly around vascular biology and drug delivery in the human brain. It builds on the GPT-4 API and integrates three primary data sources:

- **Vascular snRNA-seq dataset**: Region- and cell type–specific gene expression data derived from a human vascular single-nucleus RNA-seq atlas, processed using *Cell2Sentence*.
- **SPOKE knowledge graph (KG-RAG)**: A biomedical knowledge graph of curated biological relationships (genes, proteins, drugs, diseases, etc.), used via a retrieval-augmented generation (RAG) system to inject structured context into GPT-4.
- **Google Custom Search**: Live web search to retrieve up-to-date biomedical information from the broader internet.

These components work together to support **multi-hop investigations** across gene expression, disease associations, and pharmacological mechanisms. For example, users can query transporters enriched in disease-relevant brain regions and trace their roles in blood-brain barrier (BBB) transport and drug uptake.

Key capabilities include:

- **Natural language querying** of transcriptomic data across 17 vascular cell types and 41 brain regions.
- **Dynamic knowledge graph retrieval** to surface disease and mechanism-related insights from SPOKE.
- **Web search integration** for real-time external references.
- **Zero training required** — fully operational out of the box via API keys and Docker.

VasQ is ideal for generating hypotheses around **BBB-targeted therapeutics**, understanding **region-specific vascular biology**, and identifying **molecular pathways** for rational drug design.

> ℹ️ A paper including descriptions VasQ’s design and capabilities is forthcoming.

# 🧠 VasQ Setup Guide

Follow the steps below to get your VasQ environment up and running. This project uses Docker and Django, and requires some basic API key setup.

---

## 🚀 Initial Setup

**Install Docker Desktop**  

1. [Download for your OS →](https://docs.docker.com/desktop/)
2. Open the Docker Desktop app

**Clone this repository**  

Open a terminal:

   ```bash
   git clone https://github.com/Knight-Initiative-for-Brain-Resilience/VasQ.git
   cd VasQ
   ```

**Download large data files**  

   ```bash
   brew install git-lfs
   git lfs install
   git lfs pull
   ```

---

## 🔑 Add Your Keys

Depending on your account type or system setup, these steps may vary slightly.

<details>
<summary>⚗️ <strong>OpenAI API Key (Flask) </strong></summary>  
  
1. Open the Flask environment file:

   ```bash
   cd kg_rag
   nano .gpt_config.env
   ```

2. Generate your OpenAI API key:

#### Individual Users

- Create or sign in: [OpenAI Account](https://auth.openai.com/create-account)  
- Go to [API Keys](https://platform.openai.com/api-keys)  
- Click `+ Create new secret key`  
- Name it, keep **Default project** and **All permissions**
- Click `Create secret key` and copy the key

#### Organization Accounts

- Log in to your org account  
- Visit [Organization API Keys](https://platform.openai.com/settings/organization/api-keys)  
- Click `+ Create new secret key`  
- Name it, choose the appropriate project, keep **All permissions**
- Click `Create secret key` and copy the key

3. Paste key into `.gpt_config.env` after `API_KEY=`
4. Copy key to clipboard for use in Django environment file
5. Save Flask environment file: `Ctrl + X`, `Y`, `Enter`

</details>

---

<details>
<summary>🧠 <strong>OpenAI API Key (Django)</strong></summary>

1. Open Django environment file:

   ```bash
   cd ..
   nano .env-shared
   ```
   
2. Paste the OpenAI API key into `.env-shared` after `OPENAI_API_KEY=`

</details>

---

<details>
<summary>🔍 <strong>Google Custom Search API Key</strong></summary>  
  
> ⚠️ Google offers a generous free trial for this API.

1. Generate Google Custom Search API Key:

- Log in to your [Google Account](https://accounts.google.com)  
- Go to [Google Custom Search API](https://console.cloud.google.com/marketplace/product/google/customsearch.googleapis.com)  
- Create or select a project  
- Click **Enable** 
- In the sidebar, go to **Credentials**  
- Click `+ Create credentials` → **API key**  
- Click **Edit API key**  
- Under **Application restrictions**, choose **None**  
- Under **API restrictions**, select **Restrict key**  
- From the dropdown, choose **Custom Search API** → Click **OK**  
- Click **Save**
- On the next page **Show key** and copy it

2. Paste the API key into `.env-shared` after `GOOGLE_API_KEY=`

</details>

---

<details>
<summary>🌐 <strong>Programmable Search Engine ID</strong></summary>  
  
1. Generate Programmable Search Engine ID:
   
- Go to the [Programmable Search Control Panel](https://programmablesearchengine.google.com/controlpanel/all)
- Click **Add**  
- Name your engine  
- For "What to search?", select **Search the entire web**  
- Leave “Search settings” unchecked  
- Fill out the CAPTCHA and click **Create**  
- On the next page, go to **Back to all engines**  
- Click on the engine you just created  
- Find your ID in the **Overview** section under **Basic**
- Copy your **Search engine ID**

2. Paste the ID into `.env-shared` after `SEARCH_ENGINE_ID=`
3. Save Django environment file: `Ctrl + X`, `Y`, `Enter`

</details>

---

## 🛠️ Launch the Application

1. Build and run the application:

   ```bash
   cd ../vasq
   docker-compose build --no-cache
   docker-compose up
   ```

   If a pop-up window appears, click `Allow`.

2. Open your browser and visit:  
   [http://127.0.0.1:8000/vasq/](http://127.0.0.1:8000/vasq/)

---

## ✅ You're Ready!

VasQ should now be live on your local machine. Happy exploring!

---

# 🙏 Acknowledgements

This project builds on the work of several open-source efforts. In particular, we adapted and extended components from the following repositories:

- [**scChat**](https://github.com/li-group/scChat): A chat-based system for querying single-cell RNA-seq datasets, which provided the foundational architecture for VasQ's interface and agent design.
- [**KG-RAG**](https://github.com/BaranziniLab/KG_RAG): A retrieval-augmented generation (RAG) system for biomedical knowledge graphs, which informed the implementation of VasQ's knowledge graph querying module using SPOKE.

We are grateful to the developers of these projects for their contributions to the open-source community.
