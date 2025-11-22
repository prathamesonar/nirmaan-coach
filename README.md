
````markdown
# AI Communication Evaluator - Intern Case Study

This application is a streamlined tool designed to evaluate student self-introduction transcripts. It combines rule-based logic, statistical analysis, and NLP (Semantic Similarity) to generate a score based on the provided rubric.

---

## Features

### **Content Analysis**
Uses Sentence Transformers (NLP) to compare the student's speech against semantic targets (e.g., "My name is...", "My goals are...") and checks for mandatory keywords.

### **Speech Rate**
Calculates WPM (Words Per Minute) and provides feedback based on optimal speaking ranges.

### **Grammar & Vocabulary**
Uses LanguageTool for grammar checking and Type-Token Ratio (TTR) for vocabulary richness.

### **Clarity**
Detects and counts filler words (um, uh, like, etc.).

---

## Setup Instructions

### **Prerequisites**
- Python 3.8 or higher  
- (Optional) Java 8+ (Required for the advanced language-tool-python library. If not present, the app falls back to basic mode).

### **1. Clone & Install**

Create a virtual environment and install the dependencies:

```bash
# Create virtual env
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install libraries
pip install -r requirements.txt
````

---

### **2. Run the Application**

```bash
streamlit run app.py
```

The app will open automatically in your browser at:

```
http://localhost:8501
```

---

## Scoring Logic (Rubric Implementation)

The **Overall Score (0-100)** is a weighted sum of four categories:

### **Content & Structure (40%)**

* **Keyword Matching:** Checks for specific terms (name, age, school, etc.).
* **Semantic Similarity:** Uses all-MiniLM-L6-v2 to vector-encode the transcript and compare it against ideal introduction phrases.
* **Flow:** Checks for closing statements.

### **Speech Rate (10%)**

Calculated as:

```
(Word Count / Duration) * 60
```

Ideal Range: **111 - 140 WPM**

### **Language & Grammar (20%)**

* **Grammar:**
  `1 - min(errors_per_100_words / 10, 1)`
* **Vocabulary:** Based on TTR (Unique Words / Total Words).

### **Clarity (30%)**

Based on **Filler Word Rate**:

Percentage of “um”, “uh”, “like”, etc. vs total words.

---

```

