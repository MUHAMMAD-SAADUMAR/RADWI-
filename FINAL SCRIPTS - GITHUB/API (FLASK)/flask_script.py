from flask import Flask, Response, render_template, request , jsonify
import time
import base64

app = Flask(__name__)

def generate():
        
        while True:
            if latest_frame is not None:
                # frame = latest_frame
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + latest_frame + b'\r\n')
            time.sleep(0.04)  # 25 frames per second

# Global variable to hold the latest frame data
latest_frame = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
       
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/upload', methods=['PUT'])
def upload():
    global latest_frame
    if request.data:
        latest_frame = request.data
    return '', 204

@app.route('/testencoding', methods=['GET'])
def testencoding():
    if latest_frame is None:
        return jsonify({"error": "No frame available"}), 404
    try:
        # Encode Base64
        base64_data = base64.b64encode(latest_frame).decode('utf-8')
        return jsonify({"image": base64_data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True , host='0.0.0.0',port=4949)
