import streamlit as st
import os
from graphviz import Digraph
class ERDiagramFromTMDL:
    def __init__(self, semantic_model):
        self.semantic_model = semantic_model
        self.table_columns = {}
        self.foreign_keys = []
        #These statements below are only when you want to test this in windows with the graphviz binaries downloaded at this location below. This won't be necessary in linux.
        #graphviz_bin_path = r"C:\Users\bhaskarahemanth.gant\Downloads\windows_10_cmake_Release_Graphviz-13.1.1-win64\Graphviz-13.1.1-win64\bin"
        #os.environ["PATH"] += os.pathsep + graphviz_bin_path
    
    def parse_tmdl_files(self):
        for file in self.semantic_model:
            #st.write(f"Starting = {file[0:12]} \n {file}")
            if file[0:12]!="relationship" and file!="":
                #st.write(self.semantic_model)
                #st.write(file)
                word=file.split(' ',2)
                if word[1].startswith("'"):
                    end=file.find("'",file.find("'")+1)
                    table_name=file[file.find("'"):end+1]
                else:
                    table_name=word[1].split()[0]
                #st.write(f"Table name = ...{table_name}...")
                lines = file.split('\n')
                columns = []
                for line in lines:
                    word=line.split(' ')
                    #for i in word:
                    #    print(f"--{i}--") 
                    if word[0].strip()=="column":
                        column_name=""
                        if word[1].startswith("'"):
                            end=line.find("'",line.find("'")+1)
                            column_name=line[line.find("'"):end+1]
                        else:
                            column_name=word[1]
                        columns.append(column_name)
                self.table_columns[table_name]=columns

    def parse_relationships(self):
        lines = self.semantic_model[0].split('\n')
        from_col, to_col = None, None
        for line in lines:
            line = line.strip()
            if line.startswith("fromColumn:"):
                from_col = line.split("fromColumn:")[1].strip()
            elif line.startswith("toColumn:"):
                to_col = line.split("toColumn:")[1].strip()
                if from_col and to_col:
                    if(from_col.startswith("LocalDate") or to_col.startswith("LocalDate")):
                        continue
                    fk_table, fk_column = from_col.split(".")
                    ref_table, ref_column = to_col.split(".")
                    self.foreign_keys.append((fk_table, fk_column, ref_table, ref_column))
                    from_col, to_col = None, None

    def generate_table_node(self, table_name, columns):
        label = f"""<
    <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0">
        <TR><TD BGCOLOR="lightblue"><B>{table_name}</B></TD></TR>"""
        for col_name in columns:
            label += f'<TR><TD ALIGN="LEFT" PORT="{col_name}">{col_name}</TD></TR>'
        label += """</TABLE>
    >"""
        return label


    def generate_er_diagram(self):
        dot = Digraph(format='png', engine='fdp')
        dot.attr(rankdir='TB', size='10,10!', concentrate='true', splines='polyline', dpi="600")

        self.parse_tmdl_files()
        self.parse_relationships()

        for table_name, columns in self.table_columns.items():
            print(f"TABLE NAMEE {table_name } AND COLUMNSSS {columns}")
            label = self.generate_table_node(table_name, columns)
            dot.node(table_name, label=label, shape="plaintext")

        for fk_table, fk_column, ref_table, ref_column in self.foreign_keys:
            dot.edge(f"{fk_table}:{fk_column}", f"{ref_table}:{ref_column}",
                     label=f"{fk_column} → {ref_column}", color="blue", arrowhead="crow", fontsize="10")

        image_bytes=dot.pipe(format='png')
        return image_bytes

# Example usage
#if __name__ == "__main__":
#    semantic_model = r"C:\Users\bhaskarahemanth.gant\Downloads\New folder"
#    graphviz_bin_path = r"C:\Users\bhaskarahemanth.gant\Downloads\windows_10_cmake_Release_Graphviz-13.1.1-win64\Graphviz-13.1.1-win64\bin"
#    os.environ["PATH"] += os.pathsep + graphviz_bin_path
#
#    er_gen = ERDiagramFromTMDL(semantic_model)
 #   er_gen.generate_er_diagram()



