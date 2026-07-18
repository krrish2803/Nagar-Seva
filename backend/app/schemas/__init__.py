"""Pydantic schemas for request/response validation.

Note: Currently using models from app.models for both MongoDB storage
and API request/response validation. In a larger project, you might
separate these:
- models/: MongoDB document structures
- schemas/: API request/response schemas

This can be refactored later if needed.
"""
