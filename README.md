# langchain-imap

This package provides the `ImapRetriever` for LangChain, enabling search and retrieval of emails from IMAP servers as LangChain `Document` objects.

## Installation

```bash
pip install -U langchain-imap
```

For full document processing (DOCX, PPTX, etc.) with docling:

```bash
pip install "langchain-imap[docling]"
```

## Quickstart

```python
from langchain_imap import ImapConfig, ImapRetriever

config = ImapConfig(
    host="imap.gmail.com",
    port=993,
    user="your-email@gmail.com",
    password="your-app-password",  # Use app password for Gmail
    ssl_mode="ssl",
)

retriever = ImapRetriever(config=config, k=10)

# Search emails using IMAP syntax
docs = retriever.invoke('SUBJECT "urgent"')
for doc in docs:
    print(doc.page_content)  # Formatted email content
```

## Attachment Handling

Three modes:
- `"names_only"` (default): List attachment names
- `"text_extract"`: Extract text from PDFs and plain text attachments
- `"full_content"`: Full extraction using docling from office documents (requires [docling] extra)

## Use in Chains

Integrate with LLMs for QA over emails. See the [documentation notebook](docs/retrievers.ipynb) for examples.

## Configuration

- **auth_method**: "login" (default), supports others
- **ssl_mode**: "ssl" (default), "starttls", "plain"
- **verify_cert**: `False` for self-signed certs (not for production)

Supports Gmail, Outlook, Yahoo, custom IMAP servers.

## API Reference

[ImapRetriever](https://api.python.langchain.com/en/latest/retrievers/langchain_imap.retrievers.ImapRetriever.html)
