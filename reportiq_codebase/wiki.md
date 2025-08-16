# 📘 Scriptex: Modular Documentation Generator

## 🧩 Overview

**Scriptex** is a modular Streamlit application designed to generate comprehensive documentation from various file types, starting with Power BI `.pbip` projects. It supports Markdown and DOCX outputs and visualizes ER diagrams from semantic models.

---

## 🏗️ Architecture

### Modular Components

- **FileProcessor**: Abstract base class for file-specific processors.
- **SetContext**: Abstract base class for setting prompts based on file type and user context.
- **CompletionModel**: Handles API interaction with the language model to generate documentation.
- **markdown_to_docx.py**: Converts Markdown documentation to DOCX format.
- **tmdl_to_er.py**: Parses `.tmdl` files and generates ER diagrams using Graphviz.

---

## 📂 Supported File Types

Currently supports:
- **Power BI (.pbip)**: Upload as a zipped folder containing `.Report` and `.SemanticModel`.

Planned support:
- PDF
- CSV

---

## 🧠 Key Features

### 🔍 Context-Aware Documentation
Users can optionally provide **custom context** (e.g., purpose, data source) to tailor the documentation output.

### 📄 Multi-Format Output
- Markdown
- DOCX (via `markdown_to_docx.py`)
- ER Diagram (PNG via `tmdl_to_er.py`)

### 🧪 Semantic Parsing
- Extracts `report.json` and `.tmdl` files.
- Parses relationships and tables to build ER diagrams.

### 🧱 Extensible Design
To add support for a new file type:
1. Extend `FileProcessor` and `SetContext`.
2. Register in `FileProcessorFactory` and `SetContextFactory`.
3. Define processing and prompt logic.

---

## 🖼️ ER Diagram Generation

Implemented in `tmdl_to_er.py`:
- Parses `.tmdl` files for tables and relationships.
- Uses Graphviz to render ER diagrams.
- Skips irrelevant columns like `LocalDate`.

---

## 📄 Markdown to DOCX Conversion

Implemented in `markdown_to_docx.py`:
- Converts Markdown to HTML using `markdown2`.
- Parses HTML with BeautifulSoup.
- Formats headings, lists, tables, and paragraphs into DOCX using `python-docx`.

---

## 🧪 How It Works

### 1. File Upload
User selects file type and uploads the corresponding zip file.

### 2. File Processing
`FileProcessorFactory` returns the appropriate processor (e.g., `PowerBIProcessor`) to extract contents.

### 3. Context Setting
`SetContextFactory` returns a context setter (e.g., `PowerBIContext`) which builds system and user prompts.

### 4. Documentation Generation
`CompletionModel` sends prompts to the language model and streams the response.

### 5. Output Downloads
User can download:
- Markdown file
- DOCX file
- ER Diagram image

---

## 🛠️ Dependencies

Add to `requirements.txt`:

```txt
streamlit
python-docx
markdown2
beautifulsoup4
graphviz
requests
python-dotenv
