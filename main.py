from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
import os
import tempfile

# Flask app
app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["UPLOAD_FOLDER"] = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {"pdf", "docx", "txt", "py", "c", "cpp", "java"}

gemini_api_key = "AIzaSyAne5D5MFKo7Qd1Ry44uW8DrnxTAC_1hxg"

# Initialize Gemini model
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=gemini_api_key)

# ---- Helpers ----
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def safe_text(resp):
    """Extract text safely from LangChain AIMessage"""
    if hasattr(resp, "content"):
        if isinstance(resp.content, list):
            return " ".join([part.text for part in resp.content if hasattr(part, "text")])
        return str(resp.content)
    return str(resp)

# ---- LangGraph workflow ----
def tutor_node(state: dict):
    # File context if uploaded
    file_context = state.get("file_text", "")
    prompt = f"User asked: {state['user_input']}."
    if file_context:
        prompt += f"\nAlso consider this file content:\n{file_context[:2000]}"  # trim long files
    response = llm.invoke(prompt)
    state["answer"] = safe_text(response)
    return state

workflow = StateGraph(dict)
workflow.add_node("tutor", tutor_node)
workflow.set_entry_point("tutor")
workflow.add_edge("tutor", END)

chatbot_flow = workflow.compile()

# ----------------------------

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/health")
def health():
    return {"status": "healthy"}, 200

@app.route("/chat", methods=["POST"])
def chat():
    data = request.form or request.get_json()
    user_input = data.get("message")
    file_text = ""

    # Handle uploaded file if exists
    if "file" in request.files:
        file = request.files["file"]
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(path)

            # Extract text based on extension
            ext = filename.rsplit(".", 1)[1].lower()
            if ext == "txt" or ext in {"py", "c", "cpp", "java"}:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    file_text = f.read()
            elif ext == "pdf":
                import PyPDF2
                reader = PyPDF2.PdfReader(path)
                file_text = " ".join([p.extract_text() for p in reader.pages if p.extract_text()])
            elif ext == "docx":
                import docx
                doc = docx.Document(path)
                file_text = " ".join([p.text for p in doc.paragraphs])
    # Run LangGraph
    state = {"user_input": user_input, "file_text": file_text}
    result = chatbot_flow.invoke(state)
    return jsonify({"answer": result["answer"]})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
