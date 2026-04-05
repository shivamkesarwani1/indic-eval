"""
setup.py for indic-eval
=======================
Install with:
    pip install -e .               # core only (API models)
    pip install -e ".[hf]"         # + HuggingFace support
    pip install -e ".[quantized]"  # + 8-bit quantization
    pip install -e ".[dev]"        # + development tools
    pip install -e ".[all]"        # everything
"""

from setuptools import setup, find_packages
from pathlib import Path
import sys

# ── Python version guard ───────────────────────────────────────────────────────
if sys.version_info < (3, 9):
    raise RuntimeError(
        "indic-eval requires Python 3.9 or higher. "
        f"You are running Python {sys.version_info.major}.{sys.version_info.minor}."
    )

# ── Read long description from README ─────────────────────────────────────────
HERE = Path(__file__).parent

try:
    long_description = (HERE / "README.md").read_text(encoding="utf-8")
except FileNotFoundError:
    long_description = (
        "indic-eval: An open evaluation harness for LLMs on Indic language tasks. "
        "Supports Hindi reading comprehension, English-Hindi translation, "
        "Hinglish sentiment, Indian cultural reasoning, and Hindi summarisation. "
        "Works with any OpenAI-compatible API or HuggingFace model."
    )

# ── Read version from package __init__.py ─────────────────────────────────────
def get_version():
    init_path = HERE / "indic_eval" / "__init__.py"
    try:
        for line in init_path.read_text(encoding="utf-8").splitlines():
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"').strip("'")
    except FileNotFoundError:
        pass
    return "0.1.0"

# ── Core dependencies (always installed) ──────────────────────────────────────
INSTALL_REQUIRES = [
    "openai>=1.0",           # OpenAI-compatible API client (Sarvam, GPT, Groq, etc.)
    "sacrebleu>=2.3",        # BLEU and chrF metrics
    "rouge-score>=0.1.2",    # ROUGE-L metric
    "streamlit>=1.32",       # Dashboard
    "datasets>=2.18",        # HuggingFace datasets (IndicQA, FLORES-200)
    "python-dotenv>=1.0",    # .env file support for API keys
    "requests>=2.28",        # HTTP utilities
]

# ── Optional extras ───────────────────────────────────────────────────────────
EXTRAS_REQUIRE = {

    # HuggingFace model inference
    "hf": [
        "transformers>=4.40",
        "torch>=2.0",
        "accelerate>=0.27",   # Multi-GPU and device management
        "sentencepiece>=0.1.99",  # Required by many Indic tokenizers
        "protobuf>=3.20",     # Required by sentencepiece
    ],

    # 8-bit quantization for large models (e.g. Sarvam 30B on limited VRAM)
    "quantized": [
        "transformers>=4.40",
        "torch>=2.0",
        "accelerate>=0.27",
        "bitsandbytes>=0.43",
        "sentencepiece>=0.1.99",
    ],

    # Development tools
    "dev": [
        "pytest>=7.0",
        "pytest-cov>=4.0",   # Test coverage
        "black>=24.0",       # Code formatting
        "ruff>=0.3",         # Fast linting
        "mypy>=1.8",         # Type checking
        "ipython>=8.0",      # Better REPL for development
    ],

    # Documentation generation
    "docs": [
        "mkdocs>=1.5",
        "mkdocs-material>=9.0",
        "mkdocstrings[python]>=0.24",
    ],
}

# Convenience: install everything at once
EXTRAS_REQUIRE["all"] = list({
    dep
    for group in ["hf", "quantized", "dev", "docs"]
    for dep in EXTRAS_REQUIRE[group]
})

# ── Setup ─────────────────────────────────────────────────────────────────────
setup(
    # ── Identity ──────────────────────────────────────────────────────────────
    name="indic-eval",
    version=get_version(),
    author="Shivam Kesarwani",
    author_email="shivamkesarwani@alumni.iitd.ac.in",
    maintainer="Shivam Kesarwani",
    maintainer_email="shivamkesarwani@alumni.iitd.ac.in",

    # ── Description ───────────────────────────────────────────────────────────
    description=(
        "Open evaluation harness for LLMs on Indic language tasks — "
        "Hindi, Hinglish, translation, cultural reasoning. "
        "Supports any OpenAI-compatible API + HuggingFace."
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",

    # ── URLs ──────────────────────────────────────────────────────────────────
    url="https://github.com/shivamkesarwani/indic-eval",
    project_urls={
        "Bug Tracker":  "https://github.com/shivamkesarwani/indic-eval/issues",
        "Source Code":  "https://github.com/shivamkesarwani/indic-eval",
        "Related Work": "https://www.sarvam.ai/blogs/evaluating-indian-language-asr",
    },

    # ── Packages ──────────────────────────────────────────────────────────────
    packages=find_packages(
        exclude=["tests*", "docs*", "examples*", "results*", "data*"]
    ),
    include_package_data=True,      # Include non-Python files listed in MANIFEST.in
    package_data={
        "indic_eval": [
            "data/samples/*.json",  # Bundled fallback sample data
            "py.typed",             # PEP 561: marks package as type-annotated
        ]
    },

    # ── Requirements ──────────────────────────────────────────────────────────
    python_requires=">=3.9",
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,

    # ── CLI entry points ──────────────────────────────────────────────────────
    # This is what makes `indic-eval` work as a terminal command
    entry_points={
        "console_scripts": [
            "indic-eval=indic_eval.cli:main",
        ]
    },

    # ── PyPI classifiers ──────────────────────────────────────────────────────
    # These appear on the PyPI page and help people find the package
    classifiers=[
        # Development status
        "Development Status :: 3 - Alpha",

        # Intended audience
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",

        # Topic
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Linguistic",

        # License
        "License :: OSI Approved :: MIT License",

        # Python versions
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",

        # Operating system
        "Operating System :: OS Independent",

        # Natural language
        "Natural Language :: Hindi",
        "Natural Language :: English",
    ],

    # ── Keywords (helps with PyPI search) ────────────────────────────────────
    keywords=[
        "nlp", "indic", "hindi", "hinglish", "evaluation", "llm",
        "benchmark", "sarvam", "machine-learning", "natural-language-processing",
        "indian-languages", "multilingual", "flores", "indicqa",
    ],

    # ── Zip safety ────────────────────────────────────────────────────────────
    zip_safe=False,  # Required when package_data is used
)
