from abc import ABC,abstractmethod
import zipfile
import streamlit as st
import os
from dotenv import load_dotenv
import requests
from datetime import datetime
import time 
import json
import pypandoc
import sys
from tmdl_to_er import ERDiagramFromTMDL
import cProfile
import pstats
import io
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

def profile_func(func):
    def wrapper(*args,**kwargs):
        profiler=cProfile.Profile()
        profiler.enable()
        result=func(*args,**kwargs)
        profiler.disable()
        s=io.StringIO()
        ps=pstats.Stats(profiler,stream=s).sort_stats('cumtime')
        ps.print_stats(20)
        st.text("Profiling = "+s.getvalue())
        return result
    return wrapper
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
                    elif "/LocalDate" not in file_info.filename and (file_info.filename.endswith('relationships.tmdl') or "/tables/" in file_info.filename): # /cultures/ has a .tmdl file which is language specific and lists out all the nouns and verbs in the whole report, which is very long and not useful to the model. So excluding it to decrease token count.
                        with zip_ref.open(file_info) as semantic_model_file:
                            semantic_model.append(semantic_model_file.read().decode('utf-8'))
                            logger.debug(f"Tokens in semantic model after adding {file_info.filename} : {len(semantic_model)}")
        except zipfile.BadZipFile:
            st.warning(f"Zipfile is corrupt, please upload valid zip file.")
        except Exception as e:
            st.warning(f"Error in handling zip file : {e}")
        #logger.debug("Report = \n ----------------- \n",report,"\n -------------------------- \n")
        #logger.debug("Semantic model = \n ----------------- \n",semantic_model,"\n -------------------------- \n")
        timestamp=datetime.now().strftime("%Y%m%d_%H%M%S")
        er_filename=f"{self.zip_file.name}_ER_diagram"
        if not os.path.exists(er_filename):
            ERDiagramFromTMDL(semantic_model).generate_er_diagram(er_filename)
        logger.debug(f"Report = {len(report)} and Sem_model = {len(semantic_model)}")
        return [report,semantic_model,er_filename]
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
            st.warning(response.json())
            response.raise_for_status()
        except Exception as e:
            st.error(f"{e}")
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
                    st.warning(f"An unexpected error occurred: {e}")
@st.cache_data(show_spinner=False)
def extract(file_type,file):
    return FileProcessorFactory.get_file_processor(file_type,file).process() 
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
def markdown_to_docx(markdown_text):
    """Converts markdown text to DOCX using pypandoc."""
    try:
        # Similar to PDF, we write to a temporary file for DOCX conversion.
        with io.StringIO(markdown_text) as md_buffer:
            with open("temp.md", "w", encoding="utf-8") as f:
                f.write(md_buffer.read())
            
        docx_output_path = "output.docx"
        pypandoc.convert_file("temp.md", 'docx', outputfile=docx_output_path)
        
        with open(docx_output_path, "rb") as f:
            docx_data = f.read()
        
        os.remove("temp.md")  # Clean up temporary file
        os.remove(docx_output_path) # Clean up generated DOCX
        return docx_data
    except Exception as e:
        st.error(f"Error converting to DOCX: {e}")
        return None
@profile_func
def main():
    load_dotenv()
    st.title("ReportIQ - Documentation Generator")
    st.info("""This tool can be used to generate documentation for any kind of document/report/pdf,etc.
            Just select the input file type, upload the files in the specified way, and 
            have documentation in different file formats like Markdown, pdf, docx, etc.""")
    option = st.selectbox(
        "Select the file type below",
        ("--Select file type--","Power BI"))
    logger.debug(f"Selected filetype : {option}") 
    # Separated info and uploading information depending on file type for modularity
    info, uploader_text=info_and_uploader(option)
    st.info(info)
    file=st.file_uploader(uploader_text)
    logger.debug(f"Uploaded file {file}")
    if file:
        logger.debug(f"Sent to FileProcessor factory and process method")
        #First send the file to factory to get the processor and then process it to get the contents. Abstraction implemented.
        file_contents=extract(option,file)
        logger.debug(f"Received from FileProcessor factory and process method")
        user_context=""

        #Added context adding functionality. This will then be passed in the system prompt later, if input by the user. Otherwise, it'll be left empty.
        if st.toggle("Would you like to provide any additional context about your file?\n(Optional — e.g., purpose, data source, or anything we should know)"):
            user_context=st.text_area("Enter any context related to the file and any info")
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
                #if documentation=="":
                #    logger.debug(f"Documentation starts generating ")
                documentation="".join(st.write_stream(model.generate_documentation))
                if documentation!="":
                    st.success("Documentation generated successfully!!")
                    logger.debug("Documentation generated successfully")
                    timestamp=datetime.now().strftime("%Y%m%d_%H%M%S")
                    col1,col2,col3=st.columns(3)
                    with col1:
                        st.download_button(
                        label=f" Download as Markdown",
                        data=documentation,
                        file_name=f"Documentation_{timestamp}.md",
                        icon=":material/markdown:",
                        use_container_width=True,
                        on_click="ignore" # This is so the whole page doesn't refresh when clicked on the download button, i.e to prevent rerunning the app. See here : https://docs.streamlit.io/develop/api-reference/widgets/st.download_button#:~:text=%22ignore%22%3A%20The%20user%20downloads%20the%20file%20and%20the%20app%20doesn%27t%20rerun.%20No%20callback%20function%20is%20called.
                        )
                    with st.spinner("Generating docx..", show_time=True): 
                        docx_documentation=markdown_to_docx(documentation)
                        with col2:
                            st.download_button(
                        label=f"Download as DOCX",
                        data=docx_documentation,
                        file_name=f"Documentation_{timestamp}.docx",
                        icon=":material/docs:",
                        use_container_width=True,
                        on_click="ignore" # This is so the whole page doesn't refresh when clicked on the download button, i.e to prevent rerunning the app. See here : https://docs.streamlit.io/develop/api-reference/widgets/st.download_button#:~:text=%22ignore%22%3A%20The%20user%20downloads%20the%20file%20and%20the%20app%20doesn%27t%20rerun.%20No%20callback%20function%20is%20called.
                        ) 
                    with col3:
                        with open(f"{file_contents[2]}.png","rb") as file:
                            st.download_button(
                                label=f"Download ER Diagram",
                                data=file,
                                file_name=f"{file_contents[2]}.png",
                                icon=":material/account_tree:",
                                use_container_width=True,
                                on_click="ignore"
                            )
if __name__=="__main__":
    main()