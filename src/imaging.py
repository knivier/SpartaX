import cv2
import pygame
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.framework.formats import landmark_pb2

pygame.init()

WIDTH, HEIGHT = 1920, 1080
"""Width and height of the Pygame screen"""
MIN_DETECTION_CONFIDENCE = 0.8
"""Confidence level required to establish a pose detection"""
MIN_TRACKING_CONFIDENCE = 0.5
"""Confidence level required to establish pose tracking"""
MIN_PRESENCE_CONFIDENCE = 0.99
"""Confidence level required to establish a pose presence"""
NUM_POSES = 2
"""Number of poses to detect"""
MODEL_PATH = "pose_landmarker_full.task"
"""Path to the pose landmarker model"""

screen = pygame.display.set_mode((WIDTH, HEIGHT))

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)


def draw_landmarks_on_image(rgb_image, detection_result):
    pose_landmarks_list = detection_result.pose_landmarks
    annotated_image = rgb_image.copy()

    # Loop through the detected poses to visualize.
    for idx in range(len(pose_landmarks_list)):
        pose_landmarks = pose_landmarks_list[idx]

        pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
        pose_landmarks_proto.landmark.extend(
            [
                landmark_pb2.NormalizedLandmark(
                    x=landmark.x, y=landmark.y, z=landmark.z
                )
                for landmark in pose_landmarks
            ]
        )
        mp.solutions.drawing_utils.draw_landmarks(
            annotated_image,
            pose_landmarks_proto,
            mp.solutions.pose.POSE_CONNECTIONS,
            mp.solutions.drawing_styles.get_default_pose_landmarks_style(),
        )

        # print("Pose landmarks:", detection_result.pose_landmarks)
        # if detection_result.pose_landmarks:
        #     print("Pose landmarks[0]:", detection_result.pose_landmarks[0])

        if detection_result.pose_landmarks and True:  # Disable for now
            # pose_landmarks = detection_result.pose_landmarks[0]
            left_wrist = pose_landmarks[mp.solutions.pose.PoseLandmark.LEFT_WRIST]
            right_wrist = pose_landmarks[mp.solutions.pose.PoseLandmark.RIGHT_WRIST]

            if left_wrist.visibility > MIN_TRACKING_CONFIDENCE:
                cv2.putText(
                    annotated_image,
                    "Left wrist",
                    (
                        int(left_wrist.x * to_window.shape[1]),
                        int(left_wrist.y * to_window.shape[0]),
                    ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2,
                    cv2.LINE_AA,
                )

            if right_wrist.visibility > MIN_TRACKING_CONFIDENCE:
                cv2.putText(
                    annotated_image,
                    "Right wrist",
                    (
                        int(right_wrist.x * to_window.shape[1]),
                        int(right_wrist.y * to_window.shape[0]),
                    ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255),
                    2,
                    cv2.LINE_AA,
                )

    return annotated_image


to_window = None
last_timestamp_ms = 0


def print_result(
    detection_result: vision.PoseLandmarkerResult,  # type: ignore
    output_image: mp.Image,
    timestamp_ms: int,
):
    global to_window
    global last_timestamp_ms
    if timestamp_ms < last_timestamp_ms:
        return
    last_timestamp_ms = timestamp_ms
    to_window = cv2.cvtColor(
        draw_landmarks_on_image(output_image.numpy_view(), detection_result),
        cv2.COLOR_RGB2BGR,
    )


base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
options = vision.PoseLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.LIVE_STREAM,
    num_poses=NUM_POSES,
    min_pose_detection_confidence=MIN_DETECTION_CONFIDENCE,
    min_pose_presence_confidence=MIN_PRESENCE_CONFIDENCE,
    min_tracking_confidence=MIN_TRACKING_CONFIDENCE,
    output_segmentation_masks=False,
    result_callback=print_result,
)

def scan():
    with vision.PoseLandmarker.create_from_options(options) as landmarker:
        # Main loop to display the stream
        running = True
        while running:
            # Check for Pygame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Capture frame from the camera
            ret, frame = cap.read()
            if not ret:
                break

            # Flip and convert the frame to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Convert the frame to a MediaPipe Image object
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            timestamp_ms = int(cv2.getTickCount() / cv2.getTickFrequency() * 1000)

            # Perform pose detection asynchronously
            landmarker.detect_async(mp_image, timestamp_ms)

            if to_window is not None:
                # Rotate the frame 270 degrees
                frame_rotated = cv2.rotate(to_window, cv2.ROTATE_90_COUNTERCLOCKWISE)
                # Convert the frame from BGR to RGB (Pygame uses RGB)
                frame_rgb = cv2.cvtColor(frame_rotated, cv2.COLOR_BGR2RGB)
                # Convert the frame to a Pygame surface
                frame_surface = pygame.surfarray.make_surface(frame_rgb)
                # Display the surface on the Pygame screen
                screen.blit(frame_surface, (0, 0))

                # Update the Pygame display
                pygame.display.flip()

            # Exit on pressing 'q'
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        pygame.quit()
        
scan()