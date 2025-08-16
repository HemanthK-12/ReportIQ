from abc import ABC,abstractmethod
import zipfile
import streamlit as st
import os
from dotenv import load_dotenv
import requests
import time 
import json
import sys
from tmdl_to_er import ERDiagramFromTMDL
from markdown_to_docx import markdown_to_docx
import logging
logging.basicConfig(level=logging.DEBUG,stream=sys.stdout,format='%(asctime)s %(message)s',filemode='w')
logger=logging.getLogger(__name__)
# Refer to the Low-Level diagram in the README.md file for more clarity on this code.

#To add support for another file type : 
# - Add the file type in the option selectbox in main()
# - Write the info and files to upload in the info_and_uploader() function
# - Write a class called {file type}Processor which extends from FilePRocessor class, and fill up the process method on how to process this file type and get the text.
# - Reference this class in the FileProcessorFactory under the get_file_processor() function given this file type
# - Similarly, write a class named {file type}Context which writes the required system_prompt and user_prompt for this particular file type.
# - Reference this class in the SetContextFactory under the get_context() function given this file type.
class FileProcessor(ABC):
    @abstractmethod
    def process(self):
        pass
class PowerBIProcessor(FileProcessor):
    def __init__(self,zip_file):
        self.zip_file=zip_file
    def process(self):
        """For PowerBI, this processes info by takign in a zip file of the .Report and .SemanticModel folders and extracts report.json and all .tmdl files from them respectively."""
        logger.debug("Called process method in the processor")
        report=""
        semantic_model=[]
        try:
            with zipfile.ZipFile(self.zip_file,'r') as zip_ref:
                for file_info in zip_ref.infolist():
                    logger.debug(f"File name : {str(file_info.filename)}")
                    if file_info.filename.endswith('report.json'):
                        with zip_ref.open(file_info) as report_file:
                            report=report_file.read().decode('utf-8')
                            logger.debug("report.json extracted!")
                            logger.debug(f"Tokens of report.json = {len(report)}")
                    elif "/LocalDate" not in file_info.filename and "/DateTableTemplate" not in file_info.filename and (file_info.filename.endswith('relationships.tmdl') or "/tables/" in file_info.filename): # /cultures/ has a .tmdl file which is language specific and lists out all the nouns and verbs in the whole report, which is very long and not useful to the model. So excluding it to decrease token count.
                        with zip_ref.open(file_info) as semantic_model_file:
                            semantic_model.append(semantic_model_file.read().decode('utf-8'))
                            logger.debug(f"Tokens in semantic model after adding {file_info.filename} : {len(semantic_model)}")
            if(len(report)==0 or len(semantic_model)==0):
                st.warning("Please upload valid Power BI zip file.")
        except Exception as e:
            st.warning(f"Error in handling zip file : {e}")
        #logger.debug("Report = \n ----------------- \n",report,"\n -------------------------- \n")
        #logger.debug("Semantic model = \n ----------------- \n",semantic_model,"\n -------------------------- \n")
        #timestamp=datetime.now().strftime("%Y%m%d_%H%M%S")
        image_bytes=""
        try:
            image_bytes=ERDiagramFromTMDL(semantic_model).generate_er_diagram()
        except Exception as e:
            st.warning(f"ER diagram was not able to generate at the moment. Please try again after sometime. Error : {e}")
        logger.debug(f"Report = {len(report)} and Sem_model = {len(semantic_model)}")
        return [report,semantic_model,image_bytes]
class FileProcessorFactory(ABC):
    @staticmethod
    def get_file_processor(file_type,*args)->FileProcessor:
        """ Static method to return class based on file type, abstracting the process."""
        if file_type == "Power BI":
            logger.debug("Returned PowerBIProcessor from factory")
            return PowerBIProcessor(*args)
        #elif file_type == "pdf":
        #    return PDFProcessor(*args)
        #elif file_type == "csv":
        #    return CSVProcessor(*args)
        else:
            raise ValueError("We don't support this file format yet")
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
        """ File-type specific prompts are set here along with the file contents"""
        logger.debug("Set system prompt and user prompt")
        system_prompt=f"""
            You are a PowerBI report specialist working on converting a report to documentation.
            Attached is the data from which you have to extract and make documentation for : {self.report}
            Extract as much data as possible and ive comprehensive info and overview of the report. All of the corresponding files are in .tmdl format. Data attached : {self.semantic_model}
            Make everything comprehensive, clear, avoid redundancy and finish everything under 1000 tokens. Give data dictionary in the form of a formatted table in markdown
            """
        if self.user_context != "":
            system_prompt+=f"""
                    Also make sure you take into account the attached information which the user has given as context : {self.user_context}"""
        user_prompt="""
            Generate documentation based on this power bi report.json file. Always give data dictionary formatted as a table.
            It should have overview, key contacts, data flow, data explorer, and data dictionary.
            Make it comprehensive and give more information about the report. 
        """
        return [system_prompt,user_prompt]
class SetContextFactory(ABC):
    @staticmethod
    def get_context(file_type,*args)->SetContext:
        """ Static method to return class based on file type, abstracting the process."""
        if file_type == "Power BI":
            logger.debug("Sent PowerBIContext class from context factory")
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
        """ Responsible for sending request api with the given system prompt and receiving response in chunks and sending it as a stream"""
        logger.debug(f"System prompt length = {len(self.system_prompt)}")
        logger.debug(f"User prompt length = {len(self.user_prompt)}")
        logger.debug(f"Total length = {len(self.system_prompt)+len(self.user_prompt)}")
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
            "max_tokens": 2000,# Increased for more detailed answers
            "temperature": 0.2,  # Lower for more focused answers
            "top_p": 0.9,
            "frequency_penalty": 0.1,  # Reduce repetition
            "presence_penalty": 0.1,   # Encourage diverse language
            "stream" : True,
            "stream_options" : {
                "include_usage" : True
            }
        }
        try:
            response = requests.post(os.getenv('COMPLETION_MODEL_ENDPOINT'), headers=headers, json=data, stream=True)
            response.raise_for_status()
        except Exception as e:
            st.warning(f"Error in response from model : {e}")
            if(str(e)[0:3]=="400"):
                st.warning(f" {response.json()['error']['message']}") 
        for chunk in response.iter_content(chunk_size=None): # read from here(https://requests.readthedocs.io/en/latest/_modules/requests/models/#Response.iter_content) that iter_content iterates over the response received till now in the chunk size given in the parameter. since moel is set in stream mode,we set chunk size to none (https://requests.readthedocs.io/en/latest/api/#requests.Response:~:text=When%20stream%3DTrue%20is%20set%20on%20the%20request%2C%20this%20avoids%20reading%20the%20content%20at%20once%20into%20memory%20for%20large%20responses.%20The%20chunk%20size%20is%20the%20number%20of%20bytes%20it%20should%20read%20into%20memory.%20This%20is%20not%20necessarily%20the%20length%20of%20each%20item%20returned%20as%20decoding%20can%20take%20place.) 
            if chunk:
                try:
                    chunk_str = chunk.decode('utf-8') 
                    #logger.debug("Chunk string = \n---------------------------------\n",chunk_str,"\n--------------------------\n")
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
                    #             "content": " membership" # <----- THIS IS THE CONTENT, WE NEED TO EXTRACT THIS, SO DID THAT BELOW
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
                    #         "system_fingerlogger.debug": "fp_ab9114d383",
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
                    st.warning(f"Error decoding JSON from chunk: {chunk_str}") 
                except Exception as e:
                    st.warning(f"Error occure while streaming response from model : {e}") 
def info_and_uploader(option):
    """ Sets uploading instructions and uploader info based on file type."""
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
    logger.debug(f"Selected filetype : {option}") 
    # Separated info and uploading information depending on file type for modularity
    instr=info_and_uploader(option)
    st.info(instr[0])
    file=st.file_uploader(instr[1])
    logger.debug(f"Uploaded file {file}")
    if file is not None:
        logger.debug(f"Sent to FileProcessor factory and process method")
        #First send the file to factory to get the processor and then process it to get the contents. Abstraction implemented.
        file_contents=FileProcessorFactory.get_file_processor(option,file).process()
        logger.debug(f"Received from FileProcessor factory and process method")
        user_context=""
        documentation=""

        #Added context adding functionality. This will then be passed in the system prompt later, if input by the user. Otherwise, it'll be left empty.
        if st.toggle("Would you like to provide any additional context about your file?\n(Optional — e.g., purpose, data source, or anything we should know)"):
            user_context=st.text_input("Enter any context related to the file and any info")
        if user_context=="":
            logger.debug("No custom context input by user")
        else:
            logger.debug("Custom context given by user !")
        logger.debug(f"Sending to context factory")
        # Sending these file contents along with the optional user added context to factory gives the context getter which then sets context and returns set of prompts according to file type. Also abstraction implemented.
        prompt=SetContextFactory.get_context(option,file_contents,user_context).set_context()
        logger.debug(f"Received from context factory")

        if st.button("Generate Documentation"):
            with st.spinner("Generating...",show_time=True):
                # This final set of prompts is sent to completion model which then gives a model object, further to be used to generate documentation 
                logger.debug(f"Sending to completion model")
                model=CompletionModel(prompt)
                logger.debug(f"Initialized completionModel object ")
                # Kept on joining to enable download functionality as markdown, at the end
                if documentation=="":
                    logger.debug(f"Documentation starts generating ")
                documentation=documentation.join(st.write_stream(model.generate_documentation))
                if documentation!="":
                    st.success("Documentation generated successfully!!")
                    logger.debug("Documentation generated successfully")
                    col1,col2,col3=st.columns(3)
                    filename=file.name.split(".Report.zip")[0].split(".SemanticModel.zip")[0].split(".zip")[0]
                    try:
                        with col1:
                            st.download_button(
                        label=f" Download as Markdown",
                        data=documentation,
                        file_name=f"{filename}_Documentation.md",
                        icon=":material/markdown:",
                        use_container_width=True,
                        on_click="ignore" # This is so the whole page doesn't refresh when clicked on the download button, i.e to prevent rerunning the app. See here : https://docs.streamlit.io/develop/api-reference/widgets/st.download_button#:~:text=%22ignore%22%3A%20The%20user%20downloads%20the%20file%20and%20the%20app%20doesn%27t%20rerun.%20No%20callback%20function%20is%20called.
                        )
                    except Exception as e:
                        st.warning(f"Error generating markdown text file : {e}")
                    try:
                        with st.spinner("Generating docx..", show_time=True): 
                            docx_documentation=markdown_to_docx(documentation)
                            with col2:
                                st.download_button(
                        label=f"Download as DOCX",
                        data=docx_documentation,
                        file_name=f"{filename}_Documentation.docx",
                        icon=":material/docs:",
                        use_container_width=True,
                        on_click="ignore" # This is so the whole page doesn't refresh when clicked on the download button, i.e to prevent rerunning the app. See here : https://docs.streamlit.io/develop/api-reference/widgets/st.download_button#:~:text=%22ignore%22%3A%20The%20user%20downloads%20the%20file%20and%20the%20app%20doesn%27t%20rerun.%20No%20callback%20function%20is%20called.
                        ) 
                    except Exception as e:
                        st.warning(f"Error generating docx file : {e}")
                    try:
                        with col3:
                            st.download_button(
                                label=f"Download ER Diagram",
                                data=file_contents[2],
                                file_name=f"{filename}_ERDiagram.png",
                                icon=":material/account_tree:",
                                use_container_width=True,
                                on_click="ignore",
                                mime="image/png"
                            )
                    except Exception as e:
                        st.warning(f"Error generating ER diagram : {e}")
if __name__=="__main__":
    main()