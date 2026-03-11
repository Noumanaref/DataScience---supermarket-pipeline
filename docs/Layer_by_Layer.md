# Supermarket Data Pipeline: Layer-by-Layer Implementation Plan

This document outlines the systematic 10-layer approach used to build a robust price index pipeline.

## Milestone 1: Data Collection (Layers 1 & 1.5)
- **Layer 1**: Implement `BaseScraper` and store-specific classes.
- **Layer 1.5**: Consolidate city-level raw files into a single master CSV per store.

## Milestone 2: Cleaning & Validation (Layer 2)
- **Layer 2**: Outlier detection, null handling, and regex-based extraction of name/price tokens.

## Milestone 3: Data Normalization (Layer 3)
- **Layer 3**: Unit standardization (kg/g/ml) and brand extraction.

## Milestone 4: Entity Resolution (Layer 4)
- **Layer 4**: High-performance fuzzy matching with `rapidfuzz` to align product identities.

## Milestone 5-9: Analytics & Visualization
- Implementation of LDI, CV, and synchronisation metrics.
- Generation of high-resolution Ridge plots, Heatmaps, and Clustermaps.

## Milestone 10: Quality Assurance (Current)
- Verification of 500k row constraint.
- Professional restructuring and directory optimization.
