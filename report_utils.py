"""
Utility functions shared across report generators.
"""
import re
import os
import numpy as np
import pandas as pd


def clean_name(name):
    """Strip trailing digits from Synthea-generated names (e.g., 'Beatrice15' -> 'Beatrice')."""
    return re.sub(r'\d+$', '', str(name))


def patient_folder_name(info):
    """Return a clean folder name for a patient."""
    first = clean_name(info['FIRST'])
    last = clean_name(info['LAST'])
    return f"{first}_{last}"


def sanitize_text(text):
    """Sanitize text for fpdf core fonts (ASCII-safe)."""
    return (str(text)
        .replace('\u2014', '--')
        .replace('\u2013', '-')
        .replace('\u2018', "'")
        .replace('\u2019', "'")
        .replace('\u201c', '"')
        .replace('\u201d', '"')
        .replace('\u2026', '...')
        .replace('\u2192', '->')
        .replace('\u00b0', ' ')
        .replace('\u00b3', '3')
    )
