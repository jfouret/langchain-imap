"""Unit tests for ImapRetriever with GreenMail."""

import pytest

from langchain_imap import ImapConfig, ImapRetriever


class TestImapRetriever:
    """Test ImapRetriever functionality."""

    def test_basic_retrieval(self, greenmail_imaps_config: ImapConfig) -> None:
        """Test basic email retrieval."""
        retriever = ImapRetriever(config=greenmail_imaps_config, k=50)

        # Retrieve all messages
        docs = retriever.invoke("ALL")
        assert len(docs) == 5  # We have 5 test emails

        # Check that all documents have expected structure
        for doc in docs:
            assert "To:" in doc.page_content
            assert "From:" in doc.page_content
            assert "Subject:" in doc.page_content
            assert "Date:" in doc.page_content
            assert "Body:" in doc.page_content

            # Check metadata
            assert "message_id" in doc.metadata
            assert "date" in doc.metadata
            assert "from" in doc.metadata
            assert "subject" in doc.metadata

    def test_urgent_subject_search(self, greenmail_imaps_config: ImapConfig) -> None:
        """Test searching for emails with URGENT in subject."""
        retriever = ImapRetriever(config=greenmail_imaps_config, k=50)

        # Search for URGENT subjects (should match 3 emails: two plain text + one HTML)
        docs = retriever.invoke('SUBJECT "URGENT"')
        assert len(docs) == 3

        # Check that all returned emails have URGENT in subject
        urgent_subjects = [doc.metadata["subject"].upper() for doc in docs]
        assert all("URGENT" in subject for subject in urgent_subjects)

    def test_html_to_markdown_conversion(
        self, greenmail_imaps_config: ImapConfig
    ) -> None:
        """Test HTML email conversion to markdown."""
        retriever = ImapRetriever(config=greenmail_imaps_config)

        # Get the HTML urgent email
        docs = retriever.invoke('SUBJECT "Project Deadline"')
        assert len(docs) == 1

        content = docs[0].page_content
        # Should contain markdown from HTML conversion
        assert "# URGENT:" in content  # H1 header converted to markdown
        assert "**approaching**" in content  # Strong tag to bold
        assert "*immediately*" in content  # Em tag to italic
        assert "- Task 1:" in content or "* Task 1:" in content

    def test_limit_parameter(self, greenmail_imaps_config: ImapConfig) -> None:
        """Test limiting number of results with k parameter."""
        retriever = ImapRetriever(config=greenmail_imaps_config)

        # Test with k=2
        docs = retriever.invoke("ALL", k=2)
        assert len(docs) == 2

        # Test with k=1
        docs = retriever.invoke("ALL", k=1)
        assert len(docs) == 1

    def test_sender_search(self, greenmail_imaps_config: ImapConfig) -> None:
        """Test searching by sender."""
        retriever = ImapRetriever(config=greenmail_imaps_config)

        # Search for emails from alice@example.com
        docs = retriever.invoke('FROM "alice@example.com"')
        assert len(docs) == 1
        assert docs[0].metadata["subject"] == "Team Meeting Notes"
        assert docs[0].metadata["from"] == "alice@example.com"

    def test_date_search(self, greenmail_imaps_config: ImapConfig) -> None:
        """Test date-based search."""
        # Note: IMAP date search uses format like SINCE "2-Oct-2023"
        retriever = ImapRetriever(config=greenmail_imaps_config)

        # Search for emails since a specific date
        docs = retriever.invoke('SENTSINCE "1-Oct-2023"')
        # Should include emails from Oct 1-3 (urgent-2, urgent-1, urgent-html)
        assert len(docs) == 3

        # All returned dates should be Oct 1st or later
        import datetime

        cutoff_date = datetime.date(2023, 10, 1)
        for doc in docs:
            doc_date = datetime.date.fromisoformat(doc.metadata["date"].split("T")[0])
            assert doc_date >= cutoff_date

    def test_attachment_mode_names_only(
        self, greenmail_imaps_config: ImapConfig
    ) -> None:
        """Test attachment mode 'names_only'."""
        retriever = ImapRetriever(
            config=greenmail_imaps_config, attachment_mode="names_only"
        )

        docs = retriever.invoke("ALL")
        # All our test emails have no attachments, so no attachment field should appear
        for doc in docs:
            assert "Attachments:" not in doc.page_content

    def test_error_handling_invalid_config(
        self, greenmail_imaps_config: ImapConfig
    ) -> None:
        """Test error handling with invalid configuration."""
        # Create config with invalid host
        invalid_config = greenmail_imaps_config.model_copy()
        invalid_config.host = "invalid.host"

        retriever = ImapRetriever(config=invalid_config)

        with pytest.raises(RuntimeError, match="Failed to retrieve emails"):
            retriever.invoke("ALL")

    def test_auth_failure(self, greenmail_imaps_config: ImapConfig) -> None:
        """Test that authentication fails with an incorrect password."""
        invalid_config = greenmail_imaps_config.model_copy(
            update={"password": "wrongpassword"}
        )
        retriever = ImapRetriever(config=invalid_config)

        with pytest.raises(RuntimeError, match="Failed to retrieve emails"):
            retriever.invoke("ALL")

    def test_complex_query(self, greenmail_imaps_config: ImapConfig) -> None:
        """Test complex IMAP query combining conditions."""
        retriever = ImapRetriever(config=greenmail_imaps_config)

        # Find urgent emails not from security
        # This tests combining SUBJECT and negated FROM
        docs = retriever.invoke('SUBJECT "URGENT" NOT FROM "security@example.com"')

        # Should get 2 results: urgent-1 (sender) and urgent-html (boss),
        # but not urgent-2 (security)
        assert len(docs) == 2

        senders = {doc.metadata["from"] for doc in docs}
        assert "security@example.com" not in senders
        assert "sender@example.com" in senders
        assert "boss@example.com" in senders
