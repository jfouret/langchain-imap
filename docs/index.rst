langchain-imap Documentation
============================

LangChain integration for retrieving emails from IMAP servers.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   api

Installation
------------

Install the package using pip:

.. code-block:: bash

   pip install langchain-imap

For additional features:

.. code-block:: bash

   # For basic text extraction from attachments
   pip install langchain-imap[text_extract]
   
   # For full document processing (PDF, DOCX, etc)
   pip install langchain-imap[docling]

Quick Start
-----------

.. code-block:: python

   from langchain_imap import ImapRetriever, ImapConfig

   config = ImapConfig(
       host="imap.gmail.com",
       port=993,
       user="your-email@gmail.com",
       password="your-app-password"
   )
   
   retriever = ImapRetriever(
       config=config,
       k=10,
       attachment_mode="text_extract"
   )
   
   # Search for emails
   query = 'FROM john@example.com SUBJECT "project update"'
   results = retriever.invoke(query)

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
