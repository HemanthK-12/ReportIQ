
# ReportIQ - Documentation Generator

## Overview

ReportIQ is a Streamlit app to automate the generation of documentation/wiki from various file types. Its focus for now is on Power BI reports, but it is architected to support additional file formats in the future. The application utilizes a factory design pattern for file processing and context setting, promoting extensibility and scalability. It also uses a completion model API to generate structured documentation based on the contents and context provided.

## Features

- **File Type Selection:** Users can select the file type they want to process and generate documentation on.
- **File Upload:** Supports uploading of zip files for Power BI reports (.pbip format).
- **Context Input:** Allows users to add additional context to help tailor the generated documentation.
- **Documentation Generation:** Produces detailed documentation, extracting necessary information from files.
- **Download Option:** Provides the ability to download the generated documentation in Markdown format.

## How It Works

### Architecture
#### Process Flow Diagram
![](./Process%20Flow%20Diagram.png)
#### Low Level Diagram
![](./Low%20Level%20Diagram.png)
1. **FileProcessor Abstract Class:** This serves as a blueprint for file processors. Each specific file type processor must implement the `process()` method.
2. **FileProcessorFactory:** Provides a mechanism to retrieve the appropriate file processor based on the selected file type. This abstracts the file processing logic, allowing easy addition of support for new file types.
3. **SetContext Abstract Class:** Defines the `set_context()` method for setting system and user prompts specific to the file type being processed.
4. **SetContextFactory:** Similar to the `FileProcessorFactory`, this factory class provides the appropriate context setter.
5. **CompletionModel Class:** Sends API requests to a completion model using prompts generated from the context. Processes streamed responses to assemble the final documentation.

### Supported File Types

- **Power BI (.pbip):** Requires users to compress the .Report and .SemanticModel folders into a zip file.

### How to Add Support for Another File Type

1. **Add the File Type in the Option SelectBox:** Modify the `main()` function to include the new file type in the select box.
2. **Create a New FileProcessor Class:** Extend `FileProcessor` to handle the specific file type and implement the `process()` method.
3. **Update FileProcessorFactory:** Reference the new processor class in `get_file_processor()` based on the file type.
4. **Create a New SetContext Class:** Implement the `set_context()` method to define prompts specific to the new file type.
5. **Update SetContextFactory:** Reference the new context class in `get_context()` based on the file type.

### Running the App

1. **Environment Setup:**
   - Ensure Streamlit is installed: `pip install -r requirements.txt`
   - Set up your environment variables in a `.env` file for `COMPLETION_MODEL_API_KEY` and `COMPLETION_MODEL_ENDPOINT`.
2. **Run the App:**
   - Execute the script using Streamlit: `streamlit run app.py`

### Example Usage

1. Select "Power BI" as the file type.
2. Upload a zip file containing the .Report and .SemanticModel folders.
3. Optionally add context for better-tailored documentation.
4. Click "Generate Documentation" to start the process.
5. View the documentation and download it in Markdown format.

## Future Enhancements

- **Support for Additional File Types:** Expand capabilities to include PDFs, CSVs, and other common formats.
- **Enhanced User Interface:** Improve the UX design for easier navigation and better feedback during processing.
- **Error Handling:** Implement more robust error messages and validation checks for file uploads.
- **Building as a Framework:** Provide an API to the users such that it is made as a framework which can be integrated into any application.
