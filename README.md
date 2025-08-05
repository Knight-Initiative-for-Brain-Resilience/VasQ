# 🧠 VasQ Setup Guide

Welcome! Follow the steps below to get your VasQ environment up and running. This project uses Docker and Django, and requires some basic API key setup.

---

## 🚀 Requirements

1. **Install Docker Desktop**  
   [Download for your OS →](https://docs.docker.com/desktop/)

2. **Clone this repository**

   ```bash
   git clone https://github.com/Knight-Initiative-for-Brain-Resilience/VasQ.git
   cd VasQ
   ```

3. **Open the shared environment file**

   ```bash
   nano .env-shared
   ```

   This file contains placeholder API keys and secrets you’ll need to replace with your own.

---

## 🔑 Add Your Keys

Depending on your account type or system setup, these steps may vary slightly. Choose the method that best fits your context.

<details>
<summary>🧠 <strong>OpenAI API Key</strong></summary>

#### Individual Users

1. Create or sign in: [OpenAI Account](https://auth.openai.com/create-account)  
2. Go to [API Keys](https://platform.openai.com/api-keys)  
3. Click `+ Create new secret key`  
4. Name it, keep **Default project** and **All permissions**  
5. Copy the key into your `.env-shared` file

#### Organization Accounts

1. Log in to your org account  
2. Visit [Organization API Keys](https://platform.openai.com/settings/organization/api-keys)  
3. Click `+ Create new secret key`  
4. Name it, choose the appropriate project, keep **All permissions**  
5. Copy the key into your `.env-shared` file

</details>

---

<details>
<summary>🔍 <strong>Google Custom Search API Key</strong></summary>

> ⚠️ Google offers a generous free trial for this API.

1. Log in to your [Google Account](https://accounts.google.com)  
2. Go to [Google Custom Search API](https://console.cloud.google.com/marketplace/product/google/customsearch.googleapis.com)  
3. Create or select a project  
4. Click **Enable** 
5. In the sidebar, go to **Credentials**  
6. Click `+ Create credentials` → **API key**  
7. Click **Edit API key**  
8. Under **Application restrictions**, choose **None**  
9. Under **API restrictions**, select **Restrict key**  
10. From the dropdown, choose **Custom Search API** → Click **OK**  
11. Click **Save**, **Show key**, then copy the API key into `.env-shared`

</details>

---

<details>
<summary>🌐 <strong>Programmable Search Engine ID</strong></summary>

1. Go to the [Programmable Search Control Panel](https://programmablesearchengine.google.com/controlpanel/all)  
2. Click **Add**  
3. Name your engine  
4. For "What to search?", select **Search the entire web**  
5. Leave “Search settings” unchecked  
6. Fill out the CAPTCHA and click **Create**  
7. On the next page, go to **Back to all engines**  
8. Click on the engine you just created  
9. In the **Overview** section under **Basic**, copy your **Search engine ID** and paste it into `.env-shared`

</details>

---

<details>
<summary>🔒 <strong>Django Secret Key</strong></summary>

Open a new terminal window and navigate to your project folder. Enter the following:

```bash
python3 -m venv venv
source venv/bin/activate
pip install django
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
deactivate
```

Copy the generated key and add it to your `.env-shared` file. Close this window.

</details>

---

## 💾 Save Your `.env-shared` File

If you're using `nano`, press:  
`Ctrl + X`, then `Y`, then `Enter`

---

## 🛠️ Launch the Application

1. Build and run the application:

   ```bash
   cd vasq
   docker-compose build --no-cache
   docker-compose up
   ```

2. Open your browser and visit:  
   [http://127.0.0.1:8000/vasq/](http://127.0.0.1:8000/vasq/)

---

## ✅ You're Ready!

VasQ should now be live on your local machine. Happy exploring!
