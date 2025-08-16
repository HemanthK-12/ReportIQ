import os
import re
from graphviz import Digraph

class ERDiagramFromTMDL:
    def __init__(self, tmdl_folder):
        self.tmdl_folder = tmdl_folder
        self.table_columns = {}
        self.foreign_keys = []

    def generate_table_node(self, table_name, columns):
        label = f"<<TABLE BORDER='1' CELLBORDER='1' CELLSPACING='0'>"
        label += f"<TR><TD BGCOLOR='lightblue'><B>{table_name}</B></TD></TR>"
        for col_name, col_type in columns.items():
            label += f"<TR><TD ALIGN='LEFT' PORT='{col_name}'>{col_name} ({col_type})</TD></TR>"
        label += "</TABLE>>"
        return label

    def generate_er_diagram(self, output_file='er_diagram3.png'):
        dot = Digraph(format='png', engine='fdp')
        dot.attr(rankdir='TB', size='10,10!', concentrate='true', splines='polyline', dpi="600")

        for filename in os.listdir(self.tmdl_folder):
            if filename.endswith(".tmdl") and filename != "relationships.tmdl":
                table_name = filename.replace(".tmdl", "")
                with open(os.path.join(self.tmdl_folder, filename), 'r') as file:
                    lines = file.readlines()
                    columns = {}
                    for line in lines:
                        match = re.match(r"(\w+)\s+(\w+)", line.strip())
                        if match:
                            col_name, col_type = match.groups()
                            columns[col_name] = col_type
                    self.table_columns[table_name] = columns

        rel_path = os.path.join(self.tmdl_folder, "relationships.tmdl")
        if not os.path.exists(rel_path):
            return
        with open(rel_path, 'r') as file:
            lines = file.readlines()
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

        for table_name, columns in self.table_columns.items():
            label = self.generate_table_node(table_name, columns)
            dot.node(table_name, label=label, shape="plaintext")

        for fk_table, fk_column, ref_table, ref_column in self.foreign_keys:
            dot.edge(f"{fk_table}:{fk_column}", f"{ref_table}:{ref_column}",
                     label=f"{fk_column} → {ref_column}", color="blue", arrowhead="crow", fontsize="10")

        dot.render(output_file, cleanup=True)
        print(f"ER diagram generated: {output_file}")

# Example usage
if __name__ == "__main__":
    tmdl_folder = r"C:\Users\bhaskarahemanth.gant\Downloads\vhhh"
    graphviz_bin_path = r"C:\Users\bhaskarahemanth.gant\Downloads\windows_10_cmake_Release_Graphviz-13.1.1-win64\Graphviz-13.1.1-win64\bin"
    os.environ["PATH"] += os.pathsep + graphviz_bin_path

    er_gen = ERDiagramFromTMDL(tmdl_folder)
    er_gen.generate_er_diagram()

