# langchain-imap

This package contains the LangChain integration with Imap

## Installation

```bash
pip install -U langchain-imap
```

And you should configure credentials by setting the following environment variables:

* TODO: fill this out

## Chat Models

`ChatImap` class exposes chat models from Imap.

```python
from langchain_imap import ChatImap

llm = ChatImap()
llm.invoke("Sing a ballad of LangChain.")
```

## Embeddings

`ImapEmbeddings` class exposes embeddings from Imap.

```python
from langchain_imap import ImapEmbeddings

embeddings = ImapEmbeddings()
embeddings.embed_query("What is the meaning of life?")
```

## LLMs

`ImapLLM` class exposes LLMs from Imap.

```python
from langchain_imap import ImapLLM

llm = ImapLLM()
llm.invoke("The meaning of life is")
```
