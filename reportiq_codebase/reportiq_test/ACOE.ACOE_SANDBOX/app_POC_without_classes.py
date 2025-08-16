from abc import ABC, abstractmethod
import streamlit as st
#the ones below are solely to enable streamlit to take a FOLDER as input instead of a file
#from mttkinter import mtTkinter as tk
#from tkinter import filedialog

from datetime import datetime
import os
#import shutil
import zipfile
import requests
from dotenv import load_dotenv
load_dotenv()

# used https://refactoring.guru/design-patterns/factory-method/python/example#example-0 for reference on factory design pattern
#class FileProcessor(ABC):
#    @abstractmethod
#    def process(self): #this will further be defined differently for every different file type, written in it's own subclass 
#        pass




class CompletionModel:
    def __init__(self, report, sem_model, context, file_type):
        self.report=report
        self.sem_model=sem_model
        self.context = context
        self.file_type = file_type
        #st.write("Sem_model = \n",self.sem_model)
        if file_type=="powerbi":
            self.system_prompt="You are a PowerBI report specialist working on converting a report to documentation. Attached is the data from which you have to extract and make documentation for : "+self.report+". Also generate table dependencies by looking at the tables, their columns and their relationships. All of the corresponding files are in .tmdl format by microsoft. Data attached :"#+self.sem_model
            if context !=  "":
                self.system_prompt=self.system_prompt + "And this is the context : "+self.context
        self.user_prompt="Generate documentation based on this power bi report.json file. it should have overview, key contacts, data flow, data explorer, dependencies(table dependencies as would be given in an er diagram) and data dictionary. Make it comprehensive but finish it off and conclude it by 1000 tokens. "
    def generate_documentation(self):
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": self.user_prompt}
        ]
        headers = {
            "Content-Type": "application/json",
            "api-key": os.getenv('COMPLETION'),
            "User-agent": "your bot 0.2"
        }
        data = {
            "messages": messages,
            "max_tokens": 1000,# Increased for more detailed answers
            "temperature": 0.2,  # Lower for more focused answers
            "top_p": 0.9,
            "frequency_penalty": 0.1,  # Reduce repetition
            "presence_penalty": 0.1   # Encourage diverse language
        }

        response = requests.post(os.getenv('ENDPOINT'), headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content'].strip()

if __name__ == "__main__":
    st.title("Scriptex - Documentation Generator")
    st.info("This tool can be used to generate documentation for any kind of document/report/pdf,etc. Just select the input file type, upload the files in the specified way and have documentation in different file formats like Markdown, pdf, docx, etc.")
    option = st.selectbox(
    "Select the file type below",
    ("Power BI (.pbip)"),
)
    if option == "Power BI (.pbip)":
        report=""
        sem_model=""
        st.info("""Please follow these steps to upload your .pbip project correctly:\n

- Open your Power BI project in Power BI Desktop.\n
- Go to File → Save As → Choose .pbip format.
- Power BI will create two folders:
    - .Report
    - .SemanticModel
- Select both folders, right-click, and choose "Send to > Compressed (zipped) folder" to create a .zip file.
- Upload the .zip file using the form below.""")
        zipped_files=st.file_uploader("Upload the aforementioned zip file")
        name_part=""
        if zipped_files is not None:  # Check if a file has been uploaded
            with zipfile.ZipFile(zipped_files, 'r') as zip_ref:
                for file_info in zip_ref.infolist():  # Use infolist() to get ZipInfo objects
                    filename = file_info.filename

            # Check if the filename is within a folder ending in ".Report"
            # Split the path into parts
                    path_parts = filename.split(os.sep)
            # Check if there's a folder part and if it ends with ".Report"
                    if len(path_parts) > 1 and path_parts[-2].endswith('.Report'):
                # Extract the folder name
                        folder_name = path_parts[-2]
                # Extract the [name] part by removing ".Report"
                        name_part = folder_name.rsplit('.Report', 1)[0]
                        st.write(f"Extracted name: {name_part}")  # Example: display the extracted name
                    if file_info.filename.endswith('report.json'):
                        with zip_ref.open(file_info) as report_file: # Open the file within the zip
                            # Read the content as bytes
                            report_bytes = report_file.read() 
                        # Decode the bytes to a string (assuming UTF-8 encoding)
                            report = report_bytes.decode('utf-8') 
                    elif file_info.filename.endswith('.tmdl') and not file_info.filename.endswith('en-US.tmdl'):
                        with zip_ref.open(file_info) as report_file: # Open the file within the zip
                            # Read the content as bytes
                            report_bytes = report_file.read() 
                        # Decode the bytes to a string (assuming UTF-8 encoding)
                            sem_model+=report_bytes.decode('utf-8') 
#Now file_contents is a list where each item is the content of a file in the zip
        file_type='powerbi' # we can then change this based on the input file format if it is pdf or not
        context=""
        on=st.toggle("Would you like to provide any additional context about your file?\n(Optional — e.g., purpose, data source, or anything we should know)")
        if on:
            context=st.text_input("Enter any metadata related to the file and any info") 
        if st.button("Generate Documentation"):
            with st.spinner("Generating documentation..."):
            # Simulate a call to a completion model or backend process
            # Replace this with your actual model call
                
                documentation=CompletionModel(report,sem_model,context,file_type).generate_documentation()
                timestamp=datetime.now().strftime("%Y%m%d_%H%M%S")
                st.success("Documentation generated successfully!!")
                st.write(documentation)
                st.download_button(
                    label=f"Download as Markdown",
                    data=documentation,
                    file_name=f"Documentation_{timestamp}.md"
                )


