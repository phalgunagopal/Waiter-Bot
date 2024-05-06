from llama_index.core import Document, VectorStoreIndex
import os   
from llama_index.core.extractors import (
    SummaryExtractor,
    QuestionsAnsweredExtractor,
    TitleExtractor,
    KeywordExtractor,
    BaseExtractor,
)
from llama_index.llms.openai import OpenAI
import multiprocessing
# from llama_index.extractors.entity import EntityExtractor
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.core import SimpleDirectoryReader
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.question_gen import LLMQuestionGenerator
from llama_index.core.question_gen.prompts import (
    DEFAULT_SUB_QUESTION_PROMPT_TMPL,
)
from llama_index.core import VectorStoreIndex
from llama_index.core.query_engine import SubQuestionQueryEngine
from llama_index.core.tools import QueryEngineTool, ToolMetadata
import streamlit as st
import pandas as pd
from llama_index.core import VectorStoreIndex
import nest_asyncio

nest_asyncio.apply()
openai.api_key=st.secrets["OPENAI_KEY"]
llm = OpenAI(temperature=0.1, model="gpt-3.5-turbo", max_tokens=512)
def ParseandExtract(document):
    text_splitter = TokenTextSplitter(
    separator=" ", chunk_size=512, chunk_overlap=128
)
    extractors = [
    TitleExtractor(nodes=5, llm=llm),
    QuestionsAnsweredExtractor(questions=3, llm=llm),
    # EntityExtractor(prediction_threshold=0.5),
    # SummaryExtractor(summaries=["prev", "self"], llm=llm),
    KeywordExtractor(keywords=10, llm=llm),
    # CustomExtractor()
]

    transformations = [text_splitter] + extractors
    

    pipeline = IngestionPipeline(transformations=transformations)

    manual_nodes = pipeline.run(documents=document)
    return manual_nodes
def ask(manual_nodes, question):
    question_gen = LLMQuestionGenerator.from_defaults(
    llm=llm,
    prompt_template_str="""
        Follow the example, but instead of giving a question, always prefix the question
        with: 'By first identifying and quoting the most relevant sources, '.
        """
    + DEFAULT_SUB_QUESTION_PROMPT_TMPL,
)
    # for i in range(len(manual_nodes)-1):
    #     if len(manual_nodes[i].get_content())< 30:
    #         manual_nodes.pop(i)
    index = VectorStoreIndex(
    nodes=manual_nodes,
)
    engine = index.as_query_engine(similarity_top_k=3, llm=OpenAI(model="gpt-4"))
    retriever=index.as_retriever()
    nodes=retriever.retrieve(question)
    print(nodes[0])
    if nodes[0].score>0.65:
        
        final_engine = SubQuestionQueryEngine.from_defaults(
        query_engine_tools=[
            QueryEngineTool(
                query_engine=engine,
                metadata=ToolMetadata(
                    name="Manual_PDF",
                    description="Instructions on setting up various parts.",
                ),
            )
        ],
        question_gen=question_gen,
        use_async=True,
    )
        response = final_engine.query(question
    )
        return response.response

def main(question):
    col_names=[]
    df=pd.read_csv("dishes_rows.csv")
    for col in df.columns:
        col_names.append(col)
    col_names.pop(0)
    col_names.pop(0)
    text=""
    document=[]
    for i,j in df.iterrows():
        list=j.tolist()
        list.pop(0)
        list.pop(0)
        
        for k in range(len(list)):
            text=text+str(col_names[k])+" is "+str(list[k])+"\n"
        document.append(text)
    print(text)
    documents = [Document(text=t) for t in document]
    
    manual_nodes=ParseandExtract(documents)
    response=ask(manual_nodes,question)
    print(response)
    return manual_nodes,response
if __name__=='__main__':
    multiprocessing.freeze_support()
    response=main("how many calories in hot chocolate fudge")
    
