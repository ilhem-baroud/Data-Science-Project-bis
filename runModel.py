#spacy 3.5.0

#spacy-transformers 1.2.5
import os
import fitz
import spacy
import re
import streamlit as st

#Initialisations 
files = os.listdir('ResumePDF')
text_list=list()
languages=list()
technologies=list()
degrees = list()

#Patterns
pattern_lang = r'(?:Languages|Programming languages|Programs)[:,\s]*(.*?)\s*(?:[.-]|Others|AWARDS|Technology)'
pattern_tech = r'(?:Technology|Others)[:,\s]*(.*?)\s*(?:[.-]|AWARDS)'

# Load and test the model
nlp_resume = spacy.load("resume_parser_model")


def find_profile(skills):
    target_labels=["NAME", "EMAIL ADDRESS", "SKILLS"]
    response=list()
    
    for file in files:
        list_of_skills=[]
        score=0
        file_path = os.path.join('ResumePDF', file)
        if os.path.isfile(file_path):
            doc=fitz.open(file_path)
            text=""
            for page in doc:
                text=text+str(page.get_text())
                text=text.strip()
                text=' '.join(text.split())
                doc=nlp_resume(text)
                target_entity=[]
                for ent in doc.ents:
                    if any(word in ent.text.upper() for word in skills):
                        target_entity=ent
                        pattern=r'\b(' + '|'.join(re.escape(skill) for skill in skills) + r')\b'
                        matches = re.findall(pattern, ent.text, re.IGNORECASE)
                        for match in matches:
                            skill = re.split("[,\u2022]", match)
                            skill = [item.strip() for item in skill if item.strip()]
                            list_of_skills.extend(skill)
                            score=len(set(list_of_skills))/len(skills)
                        break
                if target_entity:
                    related_entities = [ent for ent in doc.ents if ent != target_entity]
                    for ent in related_entities:
                        st.write(f'{ent.label_} : {ent.text}')
                    st.markdown(f"""
                        <p style="color: red; font-size: 16px; font-weight:bold;">Score : {score}</p>
                        """, unsafe_allow_html=True) 
                    st.write(f"Skills : {set(list_of_skills)}")
                    
                    st.markdown(f"""
                        <hr />
                        """, unsafe_allow_html=True) 
    


selected_option = st.selectbox("Choose a label:", nlp_resume.get_pipe("ner").labels)

if(selected_option):
    st.markdown(f"""
    <p style="color: red; font-size: 16px; font-weight:bold;">{selected_option}</p>
    <hr />
    """, unsafe_allow_html=True)  



for file in files:

    file_path = os.path.join('ResumePDF', file)

    if os.path.isfile(file_path):
        doc=fitz.open(file_path)
        text=""
        for page in doc:
            text=text+str(page.get_text())
            text=text.strip()
            text=' '.join(text.split())
            doc=nlp_resume(text)

            for ent in doc.ents:
                if ent.label_==selected_option and selected_option:    
    
                    if ent.label_ == 'Skills': # Skills   
                        
                        matches = re.findall(pattern_lang, ent.text, re.IGNORECASE)
                        for match in matches:
                            lang = re.split("[,\u2022]", match)
                            lang = [item.strip() for item in lang if item.strip()]
                            languages.extend(lang)

                        matches = re.findall(pattern_tech, ent.text, re.IGNORECASE)
                        for match in matches:
                            tech = re.split("[,\u2022.]", match)
                            tech = [item.strip() for item in tech if item.strip()]
                            technologies.extend(tech)
                    elif ent.label_ == 'Degree': #Degrees
                        ent.text
                        result = re.sub(pattern_tech, "", ent.text)
                        result = re.sub(pattern_lang, "", result)
                        pattern = r"(\(.*?\))|(\bskills\b)|(\d{4}[-/]\d{2}[-/]\d{2}|\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2})"
                        result = re.sub(pattern,"", result)
                        pattern_degrees = r"[,;.\u2022]"

                        # Split the text using the pattern
                        words = re.split(pattern_degrees, result)

                        # Remove extra whitespace around each word
                        words = [word.strip() for word in words if word.strip()]
                        words
                    else:   
                        text_list.append(ent.text) 
if len(text_list):
    text_set=set(text_list)
    for elt in text_set:
        st.write(f' - {elt}')

if len(degrees):
    degrees_set=set(degrees)
    for elt in degrees_set:
        st.write(f' - {elt}')

if len(languages):
    st.markdown(f"""
    <div style="background-color: purple; padding: 10px 10px 5px 10px; border-radius: 10px; height: fit-content; 
        width: fit-content">
        <p style="color: white; font-size: 16px;">Programming languages</p>
    </div>
    <div style="height:5px;">
    </div>
    """, unsafe_allow_html=True)
    languages_set = set([lang.upper() for lang in languages])

    selection = st.pills("", languages_set, selection_mode="multi")
    st.write(selection)

    if st.button("Extract profiles"):
        find_profile(selection)



if len(technologies):
    st.markdown(f"""
    <div style="background-color: green; padding: 10px 10px 5px 10px; border-radius: 10px; height: fit-content; 
        width: fit-content">
        <p style="color: white; font-size: 16px;">Technologies</p>
    </div>
    <div style="height:5px;">
    </div>
    """, unsafe_allow_html=True)
    technologies_set = set([tech.upper() for tech in technologies])
    selection = st.pills("", technologies_set, selection_mode="multi")
    st.markdown(f"Your selected options: {selection}.")
    

