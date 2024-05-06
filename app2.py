import streamlit as st
import os
from pathlib import Path
import table_reader
# import fitz
import io
from PIL import Image
import pandas as pd
from llama_index.core import Document

st.set_page_config(page_title="Waiter-Bot", page_icon="📒")
st.title("Waiter Bot")



if 'files' not in st.session_state:    
    st.session_state.files=[]
if 'count' not in st.session_state:
    st.session_state.count=0
if 'help' not in st.session_state:
   st.session_state.help=""
if 'manual_nodes' not in st.session_state:
   st.session_state.manual_nodes=None
if 'df' not in st.session_state:
   st.session_state.df=None
if 'manual_nodes' not in st.session_state:
   st.session_state.manual_nodes=None
if 'documents' not in st.session_state:
   st.session_state.documents=None
if 'document' not in st.session_state:
   st.session_state.document=None

col_names=[]
with st.sidebar:
    
        Submit = st.button(label='Load')
        if Submit :
            st.session_state.df=pd.read_csv("dishes_rows.csv")
            for col in st.session_state.df.columns:
                 col_names.append(col)
            col_names.pop(0)
            col_names.pop(0)
            text=""
            st.session_state.document=[]
            for i,j in st.session_state.df.iterrows():
                list=j.tolist()
                list.pop(0)
                list.pop(0)
    
                for k in range(len(list)):
                    text=text+str(col_names[k])+" is "+str(list[k])+"\n"
                st.session_state.document.append(text)

            st.session_state.documents = [Document(text=t) for t in st.session_state.document]

    
            st.session_state.manual_nodes=table_reader.ParseandExtract(st.session_state.documents)        
st.subheader("Ask Question")
question=st.text_input("Enter...")
if st.button("Find Answer"):
    st.session_state.count+=1
 

    
    print(st.session_state.files)
    Answer=table_reader.ask(st.session_state.manual_nodes,question)
    
   
    st.write(Answer)
      
    
