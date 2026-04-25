from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from backend.rag.llm import get_llm
from backend.rag.vectorstore import VectorStoreManager

import json
import os

# Load prompts from prompt.json
PROMPT_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompt.json")

try:
    with open(PROMPT_FILE, "r") as f:
        _prompts = json.load(f)
        _SYSTEM_TEMPLATE = _prompts.get("system_prompt", "")
        _NO_CONTEXT_REPLY = _prompts.get("no_context_reply", "")
except Exception as e:
    # Fallback or error handling if needed
    _SYSTEM_TEMPLATE = "{context}\n{question}"
    _NO_CONTEXT_REPLY = "No context reply found."



class RAGPipeline:
    def __init__(self, vectorstore_manager: VectorStoreManager):
        self.vectorstore_manager = vectorstore_manager
        self.llm = get_llm()
        self.prompt = ChatPromptTemplate.from_template(_SYSTEM_TEMPLATE)
        self.chain = self.prompt | self.llm | StrOutputParser()

    def ask(self, question: str) -> dict:
        """
        Retrieve relevant PDF chunks from the vector store and generate an
        answer that is strictly grounded in those chunks.

        Returns a dict with 'answer' (str) and 'sources' (list of Document).
        """
        # Retrieve relevant chunks from the FAISS vector store (PDF content)
        docs = self.vectorstore_manager.search(question, k=3)

        # Guard: if no documents were retrieved, refuse to answer
        # Bypass this guard if the user is just greeting the bot
        is_greeting = question.lower().strip() in {"hi", "hello", "hey", "greetings", "good morning", "good afternoon", "good evening"}
        if not docs and not is_greeting:
            return {"answer": _NO_CONTEXT_REPLY, "sources": []}

        # Build a single context string from retrieved PDF chunks
        context = "\n\n---\n\n".join(doc.page_content for doc in docs)

        # Invoke the LLM with the grounded prompt
        answer = self.chain.invoke({"context": context, "question": question})

        return {"answer": answer, "sources": docs}