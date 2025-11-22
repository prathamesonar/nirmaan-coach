import streamlit as st
import pandas as pd
import numpy as np
import re
from textblob import TextBlob
import plotly.graph_objects as go

# --- CONFIGURATION & SETUP ---
st.set_page_config(page_title="Nirmaan AI - Communication Evaluator", layout="wide")

FORCE_LITE_MODE = False

# --- ROBUST IMPORT ---
try:
    import language_tool_python
    HAS_GRAMMAR_TOOL = True
except ImportError:
    HAS_GRAMMAR_TOOL = False

try:
    from sentence_transformers import SentenceTransformer, util
    HAS_SEMANTIC_AI = True
except ImportError:
    HAS_SEMANTIC_AI = False

# --- CACHED RESOURCE LOADING ---
@st.cache_resource
def load_nlp_models():
    if FORCE_LITE_MODE:
        return None, None

    tool = None
    semantic_model = None
    
    if HAS_GRAMMAR_TOOL:
        try:
            tool = language_tool_python.LanguageTool('en-US')
        except Exception:
            pass 
    
    if HAS_SEMANTIC_AI:
        try:
            semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception:
            pass

    return tool, semantic_model

tool, semantic_model = load_nlp_models()

# --- RUBRIC LOGIC ---
RUBRIC = {
    "weights": {
        "Content & Structure": 0.40,
        "Speech Rate": 0.10,
        "Language & Grammar": 0.20,
        "Clarity": 0.30
    },
    "keywords": [
        "name", "age", "class", "school", "family", "hobby", "interest", "goal", "ambition", "unique"
    ],
    "filler_words": [
        "um", "uh", "like", "you know", "so", "actually", "basically", "right", "i mean", "well", "kinda", "sort of", "okay", "hmm", "ah"
    ],
    "semantic_targets": [
        "My name is", 
        "I am studying in", 
        "I live with my family", 
        "My hobbies are", 
        "My goal is to become", 
        "Thank you for listening"
    ]
}

# --- ANALYSIS FUNCTIONS ---

def analyze_speech_rate(word_count, duration_sec):
    if duration_sec <= 0: return 0, 0, "Invalid duration"
    
    wpm = (word_count / duration_sec) * 60
    
    # Determine Score based on Rubric
    if 111 <= wpm <= 140:
        score = 10
        feedback = "Ideal pacing."
    elif wpm > 140:
        score = 6
        feedback = "Too fast. Try to slow down."
    elif 81 <= wpm <= 110:
        score = 6
        feedback = "Slightly slow."
    else:
        score = 2
        feedback = "Too slow. Needs more energy."
        
    return wpm, score, feedback

def analyze_grammar(text):
    # 1. Grammar Check
    error_count = 0
    matches = []
    
    if tool:
        matches = tool.check(text)
        error_count = len(matches)
        
    words = text.split()
    word_count = len(words)
    if word_count == 0: return 0, 0, 0, 0
    
    errors_per_100 = (error_count / word_count) * 100
    grammar_score_raw = 1 - min(errors_per_100 / 10, 1)
    grammar_score_final = 0
    
    if grammar_score_raw > 0.9: grammar_score_final = 10
    elif grammar_score_raw >= 0.7: grammar_score_final = 8
    elif grammar_score_raw >= 0.5: grammar_score_final = 6
    elif grammar_score_raw >= 0.3: grammar_score_final = 4
    else: grammar_score_final = 2

    # 2. Vocabulary (TTR)
    unique_words = set([w.lower() for w in words])
    ttr = len(unique_words) / word_count
    
    vocab_score = 0
    if ttr >= 0.7: vocab_score = 10
    elif ttr >= 0.5: vocab_score = 8
    elif ttr >= 0.4: vocab_score = 6
    else: vocab_score = 4
    
    combined_score = (grammar_score_final + vocab_score) / 2
    return combined_score, error_count, ttr, matches

def analyze_clarity(text):
    words = text.lower().split()
    word_count = len(words)
    filler_count = 0
    found_fillers = []
    
    for word in words:
        clean_word = re.sub(r'[^\w\s]', '', word)
        if clean_word in RUBRIC['filler_words']:
            filler_count += 1
            found_fillers.append(clean_word)
            
    filler_rate = (filler_count / word_count) * 100
    
    if filler_rate < 2: score = 10
    elif filler_rate < 4: score = 8
    elif filler_rate < 6: score = 6
    elif filler_rate < 8: score = 4
    else: score = 2
    
    return score, filler_count, list(set(found_fillers))

def analyze_content_structure(text):
    text_lower = text.lower()
    
    # 1. Keyword Presence
    found_keywords = [kw for kw in RUBRIC['keywords'] if kw in text_lower]
    keyword_coverage = len(found_keywords) / len(RUBRIC['keywords'])
    keyword_score = keyword_coverage * 10
    
    # 2. Semantic Similarity
    semantic_score = 0
    sem_sim_val = 0.0
    
    if semantic_model:
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
        if not sentences: sentences = [text]
        
        embeddings_input = semantic_model.encode(sentences)
        embeddings_target = semantic_model.encode(RUBRIC['semantic_targets'])
        
        cosine_scores = util.cos_sim(embeddings_target, embeddings_input)
        max_scores_per_target, _ = cosine_scores.max(axis=1).sort(descending=True)
        sem_sim_val = max_scores_per_target.mean().item()
        semantic_score = sem_sim_val * 10
    else:
        sem_sim_val = keyword_coverage 
        semantic_score = keyword_score 

    # 3. Flow Check
    flow_score = 10 if "thank" in text_lower[-50:] else 5
    
    final_content_score = (keyword_score * 0.4) + (semantic_score * 0.4) + (flow_score * 0.2)
    
    return final_content_score, found_keywords, sem_sim_val

# --- UI LAYOUT ---

def main():
    st.title("🎙️ AI Communication Coach")
    
    if FORCE_LITE_MODE:
        st.warning(" **Super Lite Mode Active**: AI models are disabled for instant performance.")
    
    with st.sidebar:
        st.header("Input Configuration")
        duration_input = st.number_input("Audio Duration (seconds)", min_value=10, value=52)
        st.info("Paste the transcript generated from the audio file.")
        
    transcript = st.text_area("Student Transcript", height=200, 
                              value="Hello everyone, myself Muskan, studying in class 8th B section from Christ Public School. I am 13 years old. I live with my family. There are 3 people in my family, me, my mother and my father. One special thing about my family is that they are very kind hearted to everyone and soft spoken. One thing I really enjoy is play, playing cricket and taking wickets. A fun fact about me is that I see in mirror and talk by myself. One thing people don't know about me is that I once stole a toy from one of my cousin. My favorite subject is science because it is very interesting. Through science I can explore the whole world and make the discoveries and improve the lives of others. Thank you for listening.")

    if st.button("Analyze Transcript", type="primary"):
        if not transcript.strip():
            st.error("Please enter a transcript.")
            return
            
        with st.spinner("Analyzing..."):
            word_count = len(transcript.split())
            
            # --- FIX: Correct Variable Unpacking ---
            # analyze_speech_rate returns: wpm (raw), score (0-10), feedback
            raw_wpm, score_wpm, wpm_feedback = analyze_speech_rate(word_count, duration_input)
            
            s_grammar_total, err_count, ttr, matches = analyze_grammar(transcript)
            s_clarity, filler_count, fillers_found = analyze_clarity(transcript)
            s_content, keywords_found, sem_sim = analyze_content_structure(transcript)
            
            # --- FIX: Use Score (0-10), NOT Raw Values ---
            weights = RUBRIC['weights']
            overall_score = (
                (s_content * weights['Content & Structure']) +
                (score_wpm * weights['Speech Rate']) +  # Used score_wpm here
                (s_grammar_total * weights['Language & Grammar']) +
                (s_clarity * weights['Clarity'])
            ) * 10 
            
            # Cap score at 100 just in case
            overall_score = min(overall_score, 100)
            
            # --- RESULTS ---
            col1, col2 = st.columns([1, 3])
            with col1:
                st.metric(label="Overall Score", value=f"{overall_score:.1f}/100")
                if overall_score > 80: st.success("Excellent!")
                elif overall_score > 60: st.warning("Good effort")
                else: st.error("Needs Practice")
                    
            with col2:
                categories = ['Content', 'Speech Rate', 'Grammar/Vocab', 'Clarity']
                scores = [s_content*10, score_wpm*10, s_grammar_total*10, s_clarity*10]
                fig = go.Figure(data=[go.Bar(name='Score', x=categories, y=scores, marker_color=['#4F46E5', '#10B981', '#F59E0B', '#EF4444'])])
                fig.update_layout(yaxis_range=[0, 100], title="Criterion Breakdown", height=250, margin=dict(l=20, r=20, t=30, b=20))
                st.plotly_chart(fig, use_container_width=True)
            
            st.divider()
            
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("🗣️ Speech Rate")
                # --- FIX: Display Raw WPM here ---
                st.markdown(f"**{raw_wpm:.0f} WPM**") 
                st.info(wpm_feedback)
                
                st.subheader("📝 Content & Structure")
                st.progress(min(s_content/10, 1.0))
                st.write(f"**Keywords:** {', '.join(keywords_found) if keywords_found else 'None'}")
                if semantic_model:
                    st.caption(f"Semantic Match: {sem_sim*100:.1f}%")
                else:
                    st.caption("Semantic Analysis: N/A (Lite Mode)")

            with c2:
                st.subheader("📖 Grammar")
                st.markdown(f"**Errors:** {err_count} | **TTR:** {ttr:.2f}")
                if matches:
                    with st.expander("View Errors"):
                        for m in matches: st.write(f"- {m.message}")
                            
                st.subheader("💧 Clarity")
                st.markdown(f"**Fillers:** {filler_count}")
                if fillers_found: st.write(f"Found: {', '.join(fillers_found)}")

if __name__ == "__main__":
    main()
