import cv2
import pygame
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.framework.formats import landmark_pb2
import numpy as np
import threading

WIDTH, HEIGHT = 1920, 1080
"""Width and height of the Pygame screen"""
MIN_DETECTION_CONFIDENCE = 0.75
"""Confidence level required to establish a pose detection"""
MIN_TRACKING_CONFIDENCE = 0.8
"""Confidence level required to establish pose tracking"""
MIN_PRESENCE_CONFIDENCE = 0.4
"""Confidence level required to establish a pose presence"""
TORSO_LENGTH_ARM_RATIO = 0.35

NUM_POSES = 2
"""Number of poses to detect"""
MODEL_PATH = "pose_landmarker_full.task"
"""Path to the pose landmarker model"""

pygame.init()
infoObject = pygame.display.Info()
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
screen = pygame.display.set_mode((infoObject.current_w, infoObject.current_h))

to_window = None
last_timestamp_ms = 0


detection_result = None


def print_result(
    result: vision.PoseLandmarkerResult,  # type: ignore
    output_image: mp.Image,
    timestamp_ms: int,
):
    global to_window
    global last_timestamp_ms
    global detection_result
    if timestamp_ms < last_timestamp_ms:
        return
    last_timestamp_ms = timestamp_ms
    detection_result = result
    to_window = cv2.cvtColor(
        draw_landmarks_on_image(output_image.numpy_view(), detection_result),
        cv2.COLOR_RGB2BGR,
    )


def get_player_number(pose_landmarks):
    nose_pose_x = pose_landmarks[mp.solutions.pose.PoseLandmark.NOSE].x
    player_number = 0

    if nose_pose_x < 0.5:
        player_number = 1
    else:
        player_number = 2

    return player_number


def define_action(pose_landmarks):
    right_wrist_x = pose_landmarks[mp.solutions.pose.PoseLandmark.RIGHT_WRIST].x
    left_wrist_x = pose_landmarks[mp.solutions.pose.PoseLandmark.LEFT_WRIST].x

    right_wrist_y = pose_landmarks[mp.solutions.pose.PoseLandmark.RIGHT_WRIST].y
    left_wrist_y = pose_landmarks[mp.solutions.pose.PoseLandmark.LEFT_WRIST].y

    right_shoulder_x = pose_landmarks[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER].x
    left_shoulder_x = pose_landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER].x

    right_shoulder_y = pose_landmarks[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER].y
    left_shoulder_y = pose_landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER].y

    right_hip_y = pose_landmarks[mp.solutions.pose.PoseLandmark.RIGHT_HIP].y
    left_hip_y = pose_landmarks[mp.solutions.pose.PoseLandmark.LEFT_HIP].y

    if right_shoulder_x == 0:
        human_center_x = left_shoulder_x
    elif left_shoulder_x == 0:
        human_center_x = right_shoulder_x
    else:
        human_center_x = np.average([right_shoulder_x, left_shoulder_x])

    if right_hip_y == 0:
        torso_length = np.abs(left_hip_y - left_shoulder_y)
    elif left_hip_y == 0:
        torso_length = np.abs(right_hip_y - right_shoulder_y)
    else:
        torso_length = np.average(
            [
                np.abs(right_hip_y - right_shoulder_y),
                np.abs(left_hip_y - left_shoulder_y),
            ]
        )

    player_number = 0
    player_move = "Resting"

    player_number = get_player_number(pose_landmarks)

    if (
        right_wrist_x == 0
        or left_wrist_x == 0
        or human_center_x == 0
        or torso_length == 0
    ):
        return tuple([player_number, player_move])

    if (
        abs(right_wrist_x - human_center_x) > TORSO_LENGTH_ARM_RATIO * torso_length
        or abs(left_wrist_x - human_center_x) > TORSO_LENGTH_ARM_RATIO * torso_length
    ):
        player_move = "Attack"

    elif (
        right_wrist_y < (right_hip_y + 0.2 * (right_shoulder_y - right_hip_y))
        and right_wrist_y > right_shoulder_y
    ) or (
        left_wrist_y < (left_hip_y + 0.2 * (left_shoulder_y - left_hip_y))
        and left_wrist_y > left_shoulder_y
    ):
        player_move = "Defending"

    return tuple([player_number, player_move])


options = vision.PoseLandmarkerOptions(
    base_options=python.BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=vision.RunningMode.LIVE_STREAM,
    num_poses=NUM_POSES,
    min_pose_detection_confidence=MIN_DETECTION_CONFIDENCE,
    min_pose_presence_confidence=MIN_PRESENCE_CONFIDENCE,
    min_tracking_confidence=MIN_TRACKING_CONFIDENCE,
    output_segmentation_masks=True,
    result_callback=print_result,
)


def draw_landmarks_on_image(rgb_image, detection_result):
    if (rgb_image is None) or (detection_result is None):
        return

    pose_object_list = detection_result.pose_landmarks
    annotated_image = rgb_image.copy()

    # Loop through the detected poses to visualize.
    for idx in range(len(pose_object_list)):
        pose_landmarks = pose_object_list[idx]

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

        if False:  # ! Disable for production
            nose_pose = pose_landmarks[mp.solutions.pose.PoseLandmark.NOSE]
            action = define_action(pose_landmarks)

            cv2.putText(
                annotated_image,
                f"Player {action[0]}: {action[1]}",
                (
                    int(nose_pose.x * WIDTH),
                    int(nose_pose.y * HEIGHT),
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )
            
            left_wrist = pose_landmarks[mp.solutions.pose.PoseLandmark.LEFT_WRIST]
            right_wrist = pose_landmarks[mp.solutions.pose.PoseLandmark.RIGHT_WRIST]

            if left_wrist.visibility > MIN_TRACKING_CONFIDENCE:
                cv2.putText(
                    annotated_image,
                    "Left wrist",
                    (
                        int(left_wrist.x * WIDTH),
                        int(left_wrist.y * HEIGHT),
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
                        int(right_wrist.x * WIDTH),
                        int(right_wrist.y * HEIGHT),
                    ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255),
                    2,
                    cv2.LINE_AA,
                )

    return annotated_image


def scan(seconds) -> any:
    def timer_callback():
        nonlocal running
        running = False
    timer = threading.Timer(seconds, timer_callback)
    timer.start()
    
    p1_actions = [0, 0, 0]
    """[Attacking, Defending, Resting]"""
    p2_actions = [0, 0, 0]
    """[Attacking, Defending, Resting]"""
    
    actions = ["Attack", "Defending", "Resting"]
    
    with vision.PoseLandmarker.create_from_options(options) as landmarker:
        global to_window
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            ret, frame = cap.read()
            if not ret:
                break

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            timestamp_ms = int(cv2.getTickCount() / cv2.getTickFrequency() * 1000)

            landmarker.detect_async(mp_image, timestamp_ms)
            
            if detection_result is not None:
                for pose_landmarks in detection_result.pose_landmarks:
                    action = define_action(pose_landmarks)
                    print(f"Player {action[0]}: {action[1]}")
                    if action[0] == 1:
                        if action[1] == "Attack":
                            p1_actions[0] += 1
                        elif action[1] == "Defending":
                            p1_actions[1] += 1
                        else:
                            p1_actions[2] += 1
                    else:
                        if action[1] == "Attack":
                            p2_actions[0] += 1
                        elif action[1] == "Defending":
                            p2_actions[1] += 1
                        else:
                            p2_actions[2] += 1
                    


            if to_window is not None:
                # Flip the frame horizontally
                flip_frame = cv2.flip(to_window, 1)
                # Rotate the frame 270 degrees
                frame_rotated = cv2.rotate(flip_frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
                # Convert the frame from BGR to RGB (Pygame uses RGB)
                frame_rgb = cv2.cvtColor(frame_rotated, cv2.COLOR_BGR2RGB)
                # Convert the frame to a Pygame surface
                frame_surface = pygame.surfarray.make_surface(frame_rgb)
                # Display the surface on the Pygame screen
                screen.blit(frame_surface, (0, 0))

                pygame.display.flip()

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        pygame.quit()
        
    max_action_index_p1 = np.argmax(p1_actions)
    max_action_index_p2 = np.argmax(p2_actions)
    return tuple([actions[max_action_index_p1], actions[max_action_index_p2]])

print(scan(5))
