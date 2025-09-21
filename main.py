from flask import Flask, request, jsonify
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import os

app = Flask(__name__)

# Initialize LLM
llm = ChatOpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Define the learning paths
learning_paths = {
    'programming': ['Python Basics', 'Data Structures', 'Algorithms'],
    'data_science': ['Statistics', 'Machine Learning', 'Data Visualization'],
    'web_development': ['HTML/CSS', 'JavaScript', 'Backend Development']
}

# Define the agent nodes
def assess_knowledge(state):
    prompt = ChatPromptTemplate.from_template(
        "Based on the user's response: {response}, assess their understanding of {topic}."
    )
    response = llm.invoke(prompt.format(response=state['user_response'], topic=state['current_topic']))
    state['assessment'] = response.content
    return state

def recommend_next_step(state):
    prompt = ChatPromptTemplate.from_template(
        "Given the assessment: {assessment}, recommend the next learning step for {topic}."
    )
    response = llm.invoke(prompt.format(assessment=state['assessment'], topic=state['current_topic']))
    state['recommendation'] = response.content
    return state

# Create the learning graph
workflow = StateGraph(dict)  # state is a dictionary
workflow.add_node("assess", assess_knowledge)
workflow.add_node("recommend", recommend_next_step)

# Define edges
workflow.add_edge("assess", "recommend")
workflow.add_edge("recommend", END)

# Set start and end points
workflow.set_entry_point("assess")

# Compile the workflow
app_workflow = workflow.compile()

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy'})

@app.route('/start_learning', methods=['POST'])
def start_learning():
    data = request.get_json()
    path = data.get('learning_path')
    if path not in learning_paths:
        return jsonify({'error': 'Invalid learning path'}), 400
    
    return jsonify({
        'learning_path': path,
        'curriculum': learning_paths[path]
    })

@app.route('/submit_response', methods=['POST'])
def submit_response():
    data = request.get_json()
    initial_state = {
        'user_response': data.get('response'),
        'current_topic': data.get('topic')
    }
    
    # Run the workflow
    final_state = app_workflow.invoke(initial_state)
    
    return jsonify({
        'assessment': final_state['assessment'],
        'recommendation': final_state['recommendation']
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
