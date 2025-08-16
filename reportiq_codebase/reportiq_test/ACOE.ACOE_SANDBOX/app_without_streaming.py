from abc import ABC,abstractmethod
import zipfile
import streamlit as st
import os
from dotenv import load_dotenv
import requests
from datetime import datetime

class FileProcessor(ABC):
    @abstractmethod
    def process(self):
        pass
class PowerBIProcessor(FileProcessor):
    def __init__(self,zip_file):
        self.zip_file=zip_file
    def process(self):
        report=""
        semantic_model=""
        with zipfile.ZipFile(self.zip_file,'r') as zip_ref:
            for file_info in zip_ref.infolist():
                if file_info.filename.endswith('report.json'):
                    with zip_ref.open(file_info) as report_file:
                        report=report_file.read().decode('utf-8')
                elif file_info.filename.endswith('.tmdl') and not file_info.filename.endswith('en-US.tmdl'):
                    with zip_ref.open(file_info) as semantic_model_file:
                        semantic_model+=semantic_model_file.read().decode('utf-8')
        return [report,semantic_model]
class FileProcessorFactory(ABC):
    @staticmethod
    def get_file_processor(file_type,*args)->FileProcessor:
        if file_type == "Power BI":
            return PowerBIProcessor(*args)
        #elif file_type == "pdf":
        #    return PDFProcessor(*args)
        #elif file_type == "csv":
        #    return CSVProcessor(*args)
        #else:
        #    raise ValueError("We don't support this file format yet")


class SetContext(ABC):
    @abstractmethod
    def set_context(self):
        pass
class PowerBIContext(SetContext):
    def __init__(self,file_contents,user_context):
        self.report=file_contents[0]
        self.semantic_model=file_contents[1]
        self.user_context=user_context
    def set_context(self):
        system_prompt=f"""
            You are a PowerBI report specialist working on converting a report to documentation.
            Attached is the data from which you have to extract and make documentation for : {self.report}
            Also generate table dependencies by looking at the tables, their columns and their relationships.
            All of the corresponding files are in .tmdl format by microsoft. Data attached : {self.semantic_model}
            Make everything comprehensive and finish everything under 1000 tokens
            """
        if self.user_context != "":
            system_prompt+=f"""
                    Also make sure you take into account the attached information which the user has given as context : {self.user_context}"""
        user_prompt="""
            Generate documentation based on this power bi report.json file.
            It should have overview, key contacts, data flow, data explorer, dependencies(table dependencies as would be given in an er diagram) and data dictionary.
            Make it comprehensive but finish it off and conclude it by 1000 tokens. 
        """
        return [system_prompt,user_prompt]
class SetContextFactory(ABC):
    @staticmethod
    def get_context(file_type,*args)->SetContext:
        if file_type == "Power BI":
            return PowerBIContext(*args)
        #elif file_type == "pdf":
        #    return PDFContext(*args)
        #elif file_type == "csv" : 
        #    return CSVContext(*args)
        else:
            raise ValueError("We don't support this file type yet.")


class CompletionModel:
    def __init__(self,prompt):
        self.system_prompt=prompt[0]
        self.user_prompt=prompt[1]
    def generate_documentation(self):
        messages =[
            {
                "role": "system",
                "content": self.system_prompt
            },
            {
                "role": "user",
                "content": self.user_prompt
            }
        ]
        headers = {
            "Content-Type": "application/json",
            "api-key": os.getenv('COMPLETION_MODEL_API_KEY'),
            "User-agent":"Your agent v2.0"
        }
        data = {
            "messages": messages,
            "max_tokens": 1500,# Increased for more detailed answers
            "temperature": 0.2,  # Lower for more focused answers
            "top_p": 0.9,
            "frequency_penalty": 0.1,  # Reduce repetition
            "presence_penalty": 0.1   # Encourage diverse language
        }

        response = requests.post(os.getenv('COMPLETION_MODEL_ENDPOINT'), headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content'].strip() 

def info_and_uploader(option):
    #info=""
    #uploader_text=""
    if option == "Power BI":
        info="""
                Please follow these steps to upload your .pbip project correctly:\n
                - Open your Power BI project in Power BI Desktop.\n
                - Go to File → Save As → Choose .pbip format.
                - Power BI will create two folders:
                    - .Report
                    - .SemanticModel
                - Select both folders, right-click, and choose "Send to > Compressed (zipped) folder" to create a .zip file.
                - Upload the .zip file using the form below.
        """
        uploader_text="""Upload the aforementioned zip file"""
    else:
        info="""Please select the desired file type"""
        uploader_text="""Upload the selected file"""
    return [info,uploader_text]

def main():
    load_dotenv()
    st.title("Scriptex - Documentation Generator")
    st.info("""This tool can be used to generate documentation for any kind of document/report/pdf,etc.
            Just select the input file type, upload the files in the specified way, and 
            have documentation in different file formats like Markdown, pdf, docx, etc.""")
    option = st.selectbox(
        "Select the file type below",
        ("--Select file type--","Power BI"))
    instr=info_and_uploader(option)
    st.info(instr[0])
    zip_file=st.file_uploader(instr[1])
    if zip_file is not None:
        file_contents=FileProcessorFactory.get_file_processor(option,zip_file).process()
        user_context=""
        if st.toggle("Would you like to provide any additional context about your file?\n(Optional — e.g., purpose, data source, or anything we should know)"):
            user_context=st.text_input("Enter any context related to the file and any info")
        prompt=SetContextFactory.get_context(option,file_contents,user_context).set_context()
        if st.button("Generate Documentation"):
            with st.spinner("Generating documentation..."):
                documentation=CompletionModel(prompt).generate_documentation()
                timestamp=datetime.now().strftime("%Y%m%d_%H%M%S")
                st.success("Documentation generated successfully!!")
                st.write(documentation)
                st.download_button(
                    label=f"Download as Markdown",
                    data=documentation,
                    file_name=f"Documentation_{timestamp}.md"
                ) 

if __name__=="__main__":
    main()