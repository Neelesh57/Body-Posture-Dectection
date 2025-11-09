from flask import Flask, render_template, Response, request, jsonify
import cv2
import mediapipe as mp
import time

print("OpenCV version:", cv2.__version__)
print("MediaPipe version:", mp.__version__)

app = Flask(__name__)

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

# Global toggle states
show_skeleton = True
show_keypoints = True

# Try opening the USB camera
cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)  # change index if needed
time.sleep(2)  # give camera time to warm up

if not cap.isOpened():
    print("❌ Camera not opened — try index 0 or 2")
else:
    print("✅ USB Camera opened successfully!")

def generate_frames():
    global show_skeleton, show_keypoints
    while True:
        success, frame = cap.read()
        if not success:
            print("⚠️ No frame captured from camera.")
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb)

        if results.pose_landmarks:
            if show_skeleton or show_keypoints:
                mp_drawing.draw_landmarks(
                    frame,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS if show_skeleton else None,
                    landmark_drawing_spec=mp_drawing.DrawingSpec(
                        color=(0, 0, 255) if show_keypoints else (0, 0, 0),
                        thickness=5 if show_keypoints else 0,
                        circle_radius=4 if show_keypoints else 0
                    )
                )

        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue

        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video')
def video():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/toggle', methods=['POST'])
def toggle():
    global show_skeleton, show_keypoints
    data = request.get_json()
    if 'skeleton' in data:
        show_skeleton = not show_skeleton
    if 'keypoints' in data:
        show_keypoints = not show_keypoints
    return jsonify({'skeleton': show_skeleton, 'keypoints': show_keypoints})

if __name__ == "__main__":
    app.run(debug=False)
