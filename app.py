import os
import json
from flask import Flask, request, render_template, jsonify
import vertexai
from vertexai.language_models import CodeChatModel

app = Flask(__name__)

# Configuration settings
class Config:
    GOOGLE_APPLICATION_CREDENTIALS = 'C:/Users/neosu/webapp3/mlproj1-403203-c24f2a45ebd5.json'
    PROJECT_ID = "mlproj1-403203"
    LOCATION = "us-central1"
    ALLOWED_EXTENSIONS = {'txt', 'json'}
    UPLOAD_FOLDER = "C:/Users/neosu/webapp3/temp"  # Ensure this directory exists

# Ensure the upload folder exists
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

# Set the credentials environment variable
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = Config.GOOGLE_APPLICATION_CREDENTIALS

# Initialize Vertex AI with the project and location
vertexai.init(project=Config.PROJECT_ID, location=Config.LOCATION)

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

# Helper function to analyze error logs
def analyze_error_logs(error_logs):
    analysis_results = []
    try:
        # Instantiates the model
        chat_model = CodeChatModel.from_pretrained("codechat-bison")
        chat = chat_model.start_chat()
        for error_log in error_logs:
            # Prepend "analyze this --" to each log for context
            response = chat.send_message(f"analyze this -- {error_log.strip()}")
            analysis_results.append(response.text)
    except Exception as e:
        analysis_results = {"error": str(e)}
    return analysis_results

# Main route to handle file uploads and analysis
@app.route("/", methods=["GET", "POST"])
def handle_main_page():
    if request.method == "GET":
        return render_template("index.html")

    # Process file upload
    file = request.files.get("logFile")
    if file and allowed_file(file.filename):
        file_path = os.path.join(Config.UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        # Process the file based on its extension
        if file.filename.rsplit('.', 1)[1].lower() == 'json':
            with open(file_path, "r") as f:
                data = json.load(f)
                error_logs = data if isinstance(data, list) else data.get("logs", [])
        else:
            with open(file_path, "r") as f:
                error_logs = f.readlines()

        # Remove the temporary file after processing
        os.remove(file_path)

        # Analyze the error logs and return results
        analysis_results = analyze_error_logs(error_logs)
        return jsonify(analysis_results)

    # If a non-allowed file is uploaded
    return render_template("index.html", error="Please upload a valid log file (.txt or .json).")

# Run the Flask application
if __name__ == "__main__":
    app.run(debug=True)
