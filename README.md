
# 🎙️ AI Communication Coach

A streamlined AI tool designed to evaluate student self-introduction transcripts. It combines rule-based logic, statistical analysis, and NLP (Semantic Similarity) to generate a score (0-100) based on a structured rubric.

---

**Live Demo:** https://nirmaan-coach.streamlit.app


##  Screenshot



 ![Main Page](https://github.com/user-attachments/assets/de114cd1-2751-45b0-879e-273f0caf8aca) 


---

##  Features

### **Content Analysis**
- **Keyword Matching:** Checks for mandatory terms (name, age, school, family, hobbies).
- **Semantic Similarity:** Uses Sentence-Transformers (NLP) to compare the student's speech against "ideal" introduction phrases (e.g., "My goals are...", "I study at...").

### **Speech Rate**
- Calculates WPM (Words Per Minute) from the transcript and audio duration.
- Provides feedback on pacing (Ideal: 111-140 WPM).

### **Grammar & Vocabulary**
- **Grammar:** Uses LanguageTool to detect errors.
- **Vocabulary:** Calculates TTR (Type-Token Ratio) to measure lexical richness.

### **Clarity**
- Detects and counts filler words (e.g., "um", "uh", "like") to measure speech fluency.

---

## 🛠️ Installation & Local Setup

Follow these steps to run the application on your local machine.

### **1. Clone the Repository**

```bash
git clone https://github.com/prathamesonar/nirmaan-coach.git
cd nirmaan-coach
````

### **2. Set Up Virtual Environment (Recommended)**

It is best practice to use a virtual environment to manage dependencies.

**Windows:**

```bash
python -m venv venv
.\venv\Scripts\activate
```

**Mac/Linux:**

```bash
python -m venv venv
source venv/bin/activate
```

### **3. Install Dependencies**

Install the required Python libraries listed in requirements.txt:

```bash
pip install -r requirements.txt
```

### **4. Run the Application**

Launch the Streamlit interface:

```bash
streamlit run app.py
```

The app will open automatically in your browser at:

```
http://localhost:8501
```

---

## 📊 Scoring Logic (Rubric)

The Overall Score (0-100) is calculated using a weighted sum of four key criteria, derived from the case study rubric.

| Criterion               | Weight | Logic / Formula                                                                                                                              |
| ----------------------- | ------ | -------------------------------------------------------------------------------------------------------------------------------------------- |
| **Content & Structure** | 40%    | Keywords (10pts) + Semantic Similarity (10pts) + Flow (10pts). Note: In “Lite Mode”, Semantic Similarity mirrors Keyword coverage.           |
| **Speech Rate**         | 10%    | WPM = (Word Count / Duration) * 60. <br> • Ideal (111-140): 10 pts <br> • Fast (>140) / Slow (81-110): 6 pts <br> • Too Slow (<80): 2 pts    |
| **Language & Grammar**  | 20%    | Grammar Score: `1 - min(errors_per_100 / 10, 1)` <br> Vocabulary: Based on TTR (Unique words / Total words).                                 |
| **Clarity**             | 30%    | Filler Word Rate: Percentage of fillers (“um”, “uh”, etc.) vs total words. <br> • <2%: 10 pts (Excellent) <br> • >8%: 2 pts (Needs Practice) |

---

## ⚙️ Architecture & Product Decisions

### **Tech Stack:**

Python, Streamlit, Pandas, NLTK, Sentence-Transformers.

### **Lite Mode vs. Full Mode**

The application includes a `FORCE_LITE_MODE` configuration.

* **Lite Mode (Default for Demo):**
  Bypasses heavy model downloads (2GB+) to ensure instant UI loading and responsiveness on the cloud. Uses robust rule-based approximation for scoring.

* **Full Mode:**
  Can be enabled by setting `FORCE_LITE_MODE = False` in `app.py`. This loads the full all-MiniLM-L6-v2 transformer model for deep semantic analysis.

### **Error Handling**

The app features graceful degradation.
If Java (required for Grammar check) is missing, it skips that specific check **without crashing** the entire application.

---

## 📂 Project Structure

```
nirmaan-coach/
│
├── app.py                # Main application file (Frontend + Logic)
├── requirements.txt      # Python dependencies
├── README.md             # Project documentation
└── venv/                 # Virtual environment (not included in repo)
```



