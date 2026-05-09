#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Router-Summary QA Pipeline Package
"""

from .router import QuestionRouter, create_router
from .summary_generator import SummaryGenerator, create_summary_generator
from .summary_indexer import SummaryIndexer, create_summary_indexer
from .multi_doc_retrieval import MultiDocRetriever, MultiDocPipeline, create_multi_doc_retriever
from .answer_generator import AnswerGenerator, create_answer_generator
from .pipeline import RouterSummaryQAPipeline, create_qa_pipeline

__version__ = "1.0.0"
__all__ = [
    "QuestionRouter",
    "SummaryGenerator",
    "SummaryIndexer",
    "MultiDocRetriever",
    "MultiDocPipeline",
    "AnswerGenerator",
    "RouterSummaryQAPipeline",
    "create_router",
    "create_summary_generator",
    "create_summary_indexer",
    "create_multi_doc_retriever",
    "create_answer_generator",
    "create_qa_pipeline"
]
