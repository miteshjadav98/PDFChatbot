from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from backend.rag.llm import get_llm
from backend.rag.vectorstore import VectorStoreManager

# Strict grounding prompt: forces the LLM to answer ONLY from the provided
# PDF context and produce grammatically correct, well-structured responses.
_SYSTEM_TEMPLATE = """\
You are a helpful document assistant. You MUST follow these rules strictly:

1. Answer the question ONLY using the provided context below. The context comes \
from uploaded PDF documents.
2. Do NOT use any prior knowledge, training data, or information outside the \
provided context. Every fact in your answer must be directly supported by the context.
3. If the context does not contain enough information to answer the question, \
respond ONLY with: "I'm sorry, the uploaded documents do not contain information \
related to your question."
4. Present your answer in a clear, grammatically correct, and well-structured \
manner. Use proper punctuation, complete sentences, and organized paragraphs.
5. Do NOT fabricate, speculate, or infer information that is not explicitly \
stated in the context.

Context from uploaded PDF documents:
{context}

Question: {question}

Answer:"""

_NO_CONTEXT_REPLY = (
    "I'm sorry, the uploaded documents do not contain information "
    "related to your question. Please upload a relevant PDF first."
)


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
        if not docs:
            return {"answer": _NO_CONTEXT_REPLY, "sources": []}

        # Build a single context string from retrieved PDF chunks
        context = "\n\n---\n\n".join(doc.page_content for doc in docs)

        # Invoke the LLM with the grounded prompt
        answer = self.chain.invoke({"context": context, "question": question})

        return {"answer": answer, "sources": docs}