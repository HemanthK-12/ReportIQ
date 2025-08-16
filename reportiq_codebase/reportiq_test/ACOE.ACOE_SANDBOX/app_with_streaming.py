from abc import ABC,abstractmethod
import zipfile
import streamlit as st
import os
from dotenv import load_dotenv
import requests
from datetime import datetime
import time 
import json

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
                print(file_info.filename)
                if file_info.filename.endswith('report.json'):
                    with zip_ref.open(file_info) as report_file:
                        report=report_file.read().decode('utf-8')
                elif file_info.filename.endswith('.tmdl') and "/cultures/" not in file_info.filename:
                    with zip_ref.open(file_info) as semantic_model_file:
                        semantic_model+=semantic_model_file.read().decode('utf-8')
        #print("Report = \n ----------------- \n",report,"\n -------------------------- \n")
        #print("Semantic model = \n ----------------- \n",semantic_model,"\n -------------------------- \n")
        print(f"Report = {len(report)} and Sem_model = {len(semantic_model)}")
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
            Generate table dependencies by looking at the tables, their columns and their relationships.
            All of the corresponding files are in .tmdl format. Data attached : {self.semantic_model}
            Make everything comprehensive, clear, avoid redundancy and finish everything under 1000 tokens.
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
            "presence_penalty": 0.1,   # Encourage diverse language
            "stream" : True,
            "stream_options" : {
                "include_usage" : True
            }
        }

        response = requests.post(os.getenv('COMPLETION_MODEL_ENDPOINT'), headers=headers, json=data, stream=True)
        response.raise_for_status()
        for chunk in response.iter_content(chunk_size=None): # read from here(https://requests.readthedocs.io/en/latest/_modules/requests/models/#Response.iter_content) that iter_content iterates over the response received till now in the chunk size given in the parameter. since moel is set in stream mode,we set chunk size to none (https://requests.readthedocs.io/en/latest/api/#requests.Response:~:text=When%20stream%3DTrue%20is%20set%20on%20the%20request%2C%20this%20avoids%20reading%20the%20content%20at%20once%20into%20memory%20for%20large%20responses.%20The%20chunk%20size%20is%20the%20number%20of%20bytes%20it%20should%20read%20into%20memory.%20This%20is%20not%20necessarily%20the%20length%20of%20each%20item%20returned%20as%20decoding%20can%20take%20place.) 
            if chunk:
                try:
                    chunk_str = chunk.decode('utf-8') 
                    print("Chunk string = \n---------------------------------\n",chunk_str,"\n--------------------------\n")
                    # this is example of a chunk string:
                    # {
                    #     "data": {
                    #         "choices": [
                    #         {
                    #             "content_filter_results": {
                    #             "hate": {
                    #                 "filtered": false,
                    #                 "severity": "safe"
                    #             },
                    #             "self_harm": {
                    #                 "filtered": false,
                    #                 "severity": "safe"
                    #             },
                    #             "sexual": {
                    #                 "filtered": false,
                    #                 "severity": "safe"
                    #             },
                    #             "violence": {
                    #                 "filtered": false,
                    #                 "severity": "safe"
                    #             }
                    #             },
                    #             "delta": {
                    #             "content": " membership" # <----- THHHHHHHHHIIIIIIIIIIIISSSSSSSSSSSSSSSS IS THE CONTENT, WE NEED TO EXTRACT THIS, SO DID THAT BELOW
                    #             },
                    #             "finish_reason": null,
                    #             "index": 0,
                    #             "logprobs": null
                    #         }
                    #         ],
                    #         "created": 1752057079,
                    #         "id": "chatcmpl-BrMN52V9JdezaUMW8RpIHsy6fPQj9",
                    #         "model": "gpt-4o-2024-11-20",
                    #         "object": "chat.completion.chunk",
                    #         "system_fingerprint": "fp_ab9114d383",
                    #         "usage": null
                    #     }
                    #     }
                    for line in chunk_str.split('\n'):
                            if line.startswith('data: '):
                                json_data = line[len('data: '):]
                                if json_data.strip() == '[DONE]': # tHIS IS LIKE EOF FOR STREAM
                                    break
                                parsed_data = json.loads(json_data) 
                                if 'choices' in parsed_data and len(parsed_data['choices']) > 0:
                                    delta = parsed_data['choices'][0].get('delta', {}) 
                                    if 'content' in delta:
                                        yield delta['content'] # Yield the streamed content
                                        time.sleep(0.02)
                except json.JSONDecodeError:
                    print(f"Error decoding JSON from chunk: {chunk_str}") 
                except Exception as e:
                    print(f"An unexpected error occurred: {e}") 
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
    st.title("ReportIQ - Documentation Generator")
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
        documentation=""
        if st.toggle("Would you like to provide any additional context about your file?\n(Optional — e.g., purpose, data source, or anything we should know)"):
            user_context=st.text_input("Enter any context related to the file and any info")
        prompt=SetContextFactory.get_context(option,file_contents,user_context).set_context()
        if st.button("Generate Documentation"):
            model=CompletionModel(prompt)
            documentation+=st.write_stream(model.generate_documentation)
            timestamp=datetime.now().strftime("%Y%m%d_%H%M%S")
            st.success("Documentation generated successfully!!")
            st.download_button(
                label=f"Download as Markdown",
                data=documentation,
                file_name=f"Documentation_{timestamp}.md",
                on_click="ignore"
            ) 

if __name__=="__main__":
    main()