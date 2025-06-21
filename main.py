from langgraph.graph import StateGraph
from nodes.analyse_node import node1_parse_srs
from nodes.setup_node import node2_generate_setup
from nodes.testcase_node import node_generate_tests
from nodes.codegen_node import generate_code_from_requirements
from nodes.downloadzip_node import download_project_zip
# from nodes.feedback_node import generate_feedback
from nodes.readme_node import generate_readme

class FlowState(dict): pass

builder = StateGraph(FlowState)

builder.add_node("node1_parse_srs", node1_parse_srs)
builder.add_node("node2_generate_setup", node2_generate_setup)
builder.add_node("node_generate_tests", node_generate_tests)
builder.add_node("generate_code", generate_code_from_requirements)
builder.add_node("generate_readme", generate_readme)
builder.add_node("download_zip", download_project_zip)
# builder.add_node("feedback_node", generate_feedback)

builder.set_entry_point("node1_parse_srs")
builder.add_edge("node1_parse_srs", "node2_generate_setup")
builder.add_edge("node2_generate_setup", "node2_generate_tests")
builder.add_edge("node_generate_tests", "generate_code")
# builder.add_edge("generate_code", "feedback_node")
# builder.add_edge("feedback_node", "generate_code")
builder.add_edge("generate_code", "generate_readme") 
builder.add_edge("generate_readme", "download_zip") 

flow_app = builder.compile()

if __name__ == "__main__":
    inputs = {"srs_file": "srs.docx"}  
    output = flow_app.invoke(inputs)  




