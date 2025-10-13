"""Pytest fixtures for unit tests."""

import os
import subprocess
import tempfile
import time
from pathlib import Path

import pytest
import requests

from langchain_imap import ImapConfig


@pytest.fixture(scope="session")
def greenmail_data_dir():
    """Create a temporary directory for GreenMail data."""
    tmp_dir = tempfile.mkdtemp(prefix="greenmail_")
    yield Path(tmp_dir)


@pytest.fixture(scope="session")
def greenmail_container(greenmail_data_dir):
    """Start GreenMail container using Podman."""
    # Path to preload directory (relative to project root)
    preload_dir = Path(__file__).parent.parent / "fixtures" / "preload"
    log_path = Path(__file__).parent.parent / "container.log"

    # GreenMail configuration
    env_vars = {
        "GREENMAIL_OPTS": " ".join([
            "-Dgreenmail.setup.test.all",
            "-Dgreenmail.users=test:test123@localhost",
            "-Dgreenmail.preload.dir=/preload",
            "-Dgreenmail.verbose",
            "-Dgreenmail.hostname=0.0.0.0"
        ])
    }

    # Prepare podman run command
    container_name = "langchain-imap-test"
    cmd = [
        "podman", "run", "--rm", "-d",
        "--name", container_name,
        "-e", f"GREENMAIL_OPTS={env_vars['GREENMAIL_OPTS']}",
        "-v", f"{preload_dir}:/preload:ro,Z",
        "-p", "3143:3143",
        "-p", "3993:3993",
        "-p", "8080:8080",
        "--log-driver", "k8s-file",
        "--log-opt", f"path={log_path.absolute()}",
        "docker.io/greenmail/standalone:2.1.5",
    ]

    try:
        # Start container
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        container_id = result.stdout.strip()

        # Wait for GreenMail API to be ready
        max_attempts = 30
        readiness_url = "http://localhost:8080/api/service/readiness"
        for _ in range(max_attempts):
            try:
                response = requests.get(readiness_url, timeout=5)
                if response.status_code == 200 and response.json() == {
                    "message": "Service running"
                }:
                    break
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                pass
            time.sleep(1)
        else:
            pytest.fail("GreenMail API not ready within 30 seconds")

        yield container_id

    finally:
        # Clean up container
        subprocess.run(["podman", "stop", container_name],
                      capture_output=True, check=False)


@pytest.fixture(scope="session")
def greenmail_imaps_config():
    """Configure IMAP settings for GreenMail."""
    config = ImapConfig(
        host="localhost",
        port=3993,
        user="test",
        password="test123",
        ssl_mode="ssl",
        auth_method="login",
        verify_cert=False,
    )
    return config

@pytest.fixture(scope="session")
def greenmail_imap_starttls_config():
    """Configure IMAP settings for GreenMail."""
    config = ImapConfig(
        host="localhost",
        port=3143,
        user="test",
        password="test123",
        ssl_mode="plain",
        auth_method="login",
        verify_cert=False,
    )
    return config
