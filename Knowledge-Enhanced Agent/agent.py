import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
 
# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Load the PDF
file_path = "pdf/Chpt1_AlagaMind.pdf"
loader = PyPDFLoader(file_path)
docs = loader.load()

# Split the documents
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
docs = splitter.split_documents(docs)

# Create embeddings
embeddings = OpenAIEmbeddings(
    openai_api_key=api_key,
    model="text-embedding-3-large"
)

# Create vector store
vectorStore = FAISS.from_documents(docs, embeddings)

# Create retriever
retriever = vectorStore.as_retriever(search_kwargs={"k": 3})

# Create RAG chain
llm = ChatOpenAI(
    api_key=api_key,
      model="gpt-4o-mini"
)
chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    return_source_documents=True
)

 

# Query
query = "What is this all about?"
result = chain.invoke({"query": query})

print("Answer:", result["result"])
