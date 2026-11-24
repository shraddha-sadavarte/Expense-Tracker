"""Aggregates every module router under /api/v1. Modules are added as they are built."""

from fastapi import APIRouter

api_router = APIRouter(prefix="/api/v1")
