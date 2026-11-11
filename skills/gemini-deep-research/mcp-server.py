#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "mcp[cli]>=1.2.0",
#   "httpx>=0.27.0",
# ]
# ///

from __future__ import annotations

import json
import os
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

DEFAULT_API_BASE_URL = "https://generativelanguage.googleapis.com/v1alpha"
DEFAULT_REGULAR_AGENT_ID = "deep-research-preview-04-2026"
DEFAULT_MAX_AGENT_ID = "deep-research-max-preview-04-2026"

mcp = FastMCP(
    "gemini-deep-research",
    instructions=(
        "Start and poll Google Gemini Deep Research interactions. "
        "Use deep_research_start_regular for standard deep research, "
        "deep_research_start_max for deeper and slower runs, and "
        "deep_research_start_regular_with_files or deep_research_start_max_with_files "
        "when file context is required. "
        "Use deep_research_poll with the interaction ID returned by a start tool."
    ),
)


# -- Validation ---------------------------------------------------------------

def _require_api_key() -> str:
    api_key = os.getenv("GOOGLE_API_KEY", "").strip()
    if not api_key:
        raise ValueError("Missing GOOGLE_API_KEY environment variable")
    return api_key


def _validate_prompt(prompt: str) -> str:
    clean = (prompt or "").strip()
    if not clean:
        raise ValueError("prompt must be a non-empty string")
    return clean


def _validate_optional_list(values: list[str] | None, name: str) -> list[str]:
    if values is None:
        return []

    if not isinstance(values, list):
        raise ValueError(f"{name} must be a list of strings")

    clean_values: list[str] = []
    for value in values:
        if not isinstance(value, str):
            raise ValueError(f"{name} must contain only strings")
        text = value.strip()
        if text:
            clean_values.append(text)

    return clean_values


def _validate_file_uris(file_uris: list[str] | None) -> list[str]:
    uris = _validate_optional_list(file_uris, "file_uris")
    if not uris:
        raise ValueError("file_uris must include at least one URI for file-aware research")

    invalid = [uri for uri in uris if ":" not in uri]
    if invalid:
        raise ValueError(
            "file_uris must contain valid URI-like values (e.g. file:///tmp/report.pdf)"
        )

    return uris


# -- Gemini Interactions API --------------------------------------------------

def _api_base_url() -> str:
    return os.getenv("GEMINI_API_BASE_URL", DEFAULT_API_BASE_URL).rstrip("/")


def _request(method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    api_key = _require_api_key()
    url = f"{_api_base_url()}{path}"
    headers = {
        "x-goog-api-key": api_key,
        "content-type": "application/json",
    }

    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.request(method=method, url=url, headers=headers, json=payload)
    except httpx.HTTPError as exc:
        raise RuntimeError(f"HTTP request failed: {exc}") from exc

    if response.status_code >= 400:
        body = response.text.strip() or "(empty response body)"
        raise RuntimeError(
            f"Gemini API error {response.status_code} on {path}: {body}"
        )

    try:
        return response.json()
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Gemini API returned invalid JSON: {exc}") from exc


def _extract_interaction_id(response: dict[str, Any]) -> str:
    for key in ("name", "id", "interactionId", "interaction_id"):
        value = response.get(key)
        if isinstance(value, str) and value.strip():
            return value

    interaction = response.get("interaction")
    if isinstance(interaction, dict):
        for key in ("name", "id"):
            value = interaction.get(key)
            if isinstance(value, str) and value.strip():
                return value

    raise RuntimeError("Could not find interaction ID in Gemini API response")


def _build_interaction_payload(
    *,
    prompt: str,
    agent: str,
    additional_instructions: str | None,
    file_uris: list[str] | None,
    file_search_stores: list[str] | None,
) -> dict[str, Any]:
    tools: list[dict[str, Any]] = [{"type": "google_search"}]
    if file_search_stores:
        tools.append({"type": "file_search", "file_search_store_names": file_search_stores})

    merged_prompt = prompt
    if additional_instructions:
        instructions = additional_instructions.strip()
        merged_prompt = f"{instructions}\n\n{prompt}"

    input_parts: list[dict[str, Any]] = [
        {
            "type": "text",
            "text": merged_prompt,
        }
    ]
    if file_uris:
        for uri in file_uris:
            input_parts.append({"type": "document", "uri": uri})

    payload: dict[str, Any] = {
        "agent": agent,
        "background": True,
        "input": input_parts,
        "tools": tools,
        "agent_config": {"type": "deep-research"},
    }

    return payload


def _start_interaction(
    *,
    prompt: str,
    agent_id: str,
    additional_instructions: str | None,
    file_uris: list[str] | None,
    file_search_stores: list[str] | None,
) -> str:
    clean_prompt = _validate_prompt(prompt)
    clean_file_uris = _validate_optional_list(file_uris, "file_uris")
    clean_file_search_stores = _validate_optional_list(file_search_stores, "file_search_stores")

    payload = _build_interaction_payload(
        prompt=clean_prompt,
        agent=agent_id,
        additional_instructions=additional_instructions,
        file_uris=clean_file_uris,
        file_search_stores=clean_file_search_stores,
    )
    response = _request("POST", "/interactions", payload)
    interaction_id = _extract_interaction_id(response)

    result = {
        "interaction_id": interaction_id,
        "status": response.get("status") or response.get("state") or "unknown",
        "agent_id": agent_id,
        "raw": response,
    }
    return json.dumps(result, indent=2)


def _normalize_interaction_path(interaction_id: str) -> str:
    clean_id = (interaction_id or "").strip()
    if not clean_id:
        raise ValueError("interaction_id must be a non-empty string")

    if clean_id.startswith("interactions/"):
        return f"/{clean_id}"

    return f"/interactions/{clean_id}"


# -- MCP Tools ----------------------------------------------------------------

@mcp.tool()
def deep_research_start_regular(
    prompt: str,
    additional_instructions: str | None = None,
    file_search_stores: list[str] | None = None,
) -> str:
    """Start a regular deep research interaction and return interaction_id.

    Args:
        prompt: Main research request.
        additional_instructions: Optional extra constraints for the researcher.
        file_search_stores: Optional file-search store names for retrieval context.
    """
    try:
        return _start_interaction(
            prompt=prompt,
            agent_id=DEFAULT_REGULAR_AGENT_ID,
            additional_instructions=additional_instructions,
            file_uris=None,
            file_search_stores=file_search_stores,
        )
    except (ValueError, RuntimeError) as exc:
        return f"Error: {exc}"


@mcp.tool()
def deep_research_start_max(
    prompt: str,
    additional_instructions: str | None = None,
    file_search_stores: list[str] | None = None,
) -> str:
    """Start a max deep research interaction and return interaction_id.

    Args:
        prompt: Main research request.
        additional_instructions: Optional extra constraints for the researcher.
        file_search_stores: Optional file-search store names for retrieval context.
    """
    try:
        return _start_interaction(
            prompt=prompt,
            agent_id=DEFAULT_MAX_AGENT_ID,
            additional_instructions=additional_instructions,
            file_uris=None,
            file_search_stores=file_search_stores,
        )
    except (ValueError, RuntimeError) as exc:
        return f"Error: {exc}"


@mcp.tool()
def deep_research_start_regular_with_files(
    prompt: str,
    file_uris: list[str],
    additional_instructions: str | None = None,
    file_search_stores: list[str] | None = None,
) -> str:
    """Start regular deep research with attached files and return interaction_id.

    Args:
        prompt: Main research request.
        file_uris: URI list for files to include (example: file:///tmp/brief.pdf).
        additional_instructions: Optional extra constraints for the researcher.
        file_search_stores: Optional file-search store names for retrieval context.
    """
    try:
        validated_file_uris = _validate_file_uris(file_uris)

        return _start_interaction(
            prompt=prompt,
            agent_id=DEFAULT_REGULAR_AGENT_ID,
            additional_instructions=additional_instructions,
            file_uris=validated_file_uris,
            file_search_stores=file_search_stores,
        )
    except (ValueError, RuntimeError) as exc:
        return f"Error: {exc}"


@mcp.tool()
def deep_research_start_max_with_files(
    prompt: str,
    file_uris: list[str],
    additional_instructions: str | None = None,
    file_search_stores: list[str] | None = None,
) -> str:
    """Start max deep research with attached files and return interaction_id.

    Args:
        prompt: Main research request.
        file_uris: URI list for files to include (example: file:///tmp/brief.pdf).
        additional_instructions: Optional extra constraints for the researcher.
        file_search_stores: Optional file-search store names for retrieval context.
    """
    try:
        validated_file_uris = _validate_file_uris(file_uris)

        return _start_interaction(
            prompt=prompt,
            agent_id=DEFAULT_MAX_AGENT_ID,
            additional_instructions=additional_instructions,
            file_uris=validated_file_uris,
            file_search_stores=file_search_stores,
        )
    except (ValueError, RuntimeError) as exc:
        return f"Error: {exc}"


@mcp.tool()
def deep_research_start_file_aware(
    prompt: str,
    file_uris: list[str],
    mode: str = "regular",
    additional_instructions: str | None = None,
    file_search_stores: list[str] | None = None,
) -> str:
    """Backward-compatible wrapper for file-aware deep research.

    Args:
        prompt: Main research request.
        file_uris: URI list for files to include (example: file:///tmp/brief.pdf).
        mode: "regular" or "max" depth mode.
        additional_instructions: Optional extra constraints for the researcher.
        file_search_stores: Optional file-search store names for retrieval context.
    """
    clean_mode = (mode or "").strip().lower()
    if clean_mode == "max":
        return deep_research_start_max_with_files(
            prompt=prompt,
            file_uris=file_uris,
            additional_instructions=additional_instructions,
            file_search_stores=file_search_stores,
        )
    if clean_mode == "regular":
        return deep_research_start_regular_with_files(
            prompt=prompt,
            file_uris=file_uris,
            additional_instructions=additional_instructions,
            file_search_stores=file_search_stores,
        )
    return "Error: mode must be either 'regular' or 'max'"


@mcp.tool()
def deep_research_poll(interaction_id: str) -> str:
    """Poll an interaction status and return current state plus any result data.

    Args:
        interaction_id: ID returned by a deep_research_start_* tool.
    """
    try:
        path = _normalize_interaction_path(interaction_id)
        response = _request("GET", path)

        status = (
            response.get("status")
            or response.get("state")
            or response.get("interaction", {}).get("status")
            or "unknown"
        )
        done = str(status).lower() in {
            "done",
            "completed",
            "succeeded",
            "failed",
            "cancelled",
            "canceled",
        }

        result = {
            "interaction_id": interaction_id,
            "status": status,
            "done": done,
            "raw": response,
        }
        return json.dumps(result, indent=2)
    except (ValueError, RuntimeError) as exc:
        return f"Error: {exc}"


if __name__ == "__main__":
    mcp.run()
