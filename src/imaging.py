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
MIN_PRESENCE_CONFIDENCE = 0.7
"""Confidence level required to establish a pose presence"""
TORSO_LENGTH_ARM_RATIO = 0.35
"""Ratio of the torso length to the arm length"""
SOLO_PLAY = False
"""Whether the player is playing alone"""
NUM_POSES = 2
"""Number of poses to detect"""
MODEL_PATH = "/Users/ankur/Coding-Projects/Hackathon/SpartahackX/SpartaX/src/pose_landmarker_full.task"
# MODEL_PATH = "./src/pose_landmarker_full.task"
"""Path to the pose landmarker model"""

# pygame.init()
# cap = cv2.VideoCapture(0)
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
# screen = pygame.display.set_mode((WIDTH, HEIGHT))
# pygame.display.set_caption("WizViz Pose Detection")

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

    if nose_pose_x == 0:
        return 0

    if SOLO_PLAY:
        return 1

    if nose_pose_x < 0.5:
        player_number = 1
    else:
        player_number = 2

    return player_number


def define_action(pose_landmarks):
    right_wrist = pose_landmarks[mp.solutions.pose.PoseLandmark.RIGHT_WRIST]
    left_wrist = pose_landmarks[mp.solutions.pose.PoseLandmark.LEFT_WRIST]

    right_shoulder = pose_landmarks[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER]
    left_shoulder = pose_landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER]

    right_hip = pose_landmarks[mp.solutions.pose.PoseLandmark.RIGHT_HIP]
    left_hip = pose_landmarks[mp.solutions.pose.PoseLandmark.LEFT_HIP]

    if right_shoulder.x == 0:
        human_center_x = left_shoulder.x
    elif left_shoulder.x == 0:
        human_center_x = right_shoulder.x
    else:
        human_center_x = np.average([right_shoulder.x, left_shoulder.x])

    if right_hip.y == 0:
        torso_length = np.abs(left_hip.y - left_shoulder.y)
    elif left_hip.y == 0:
        torso_length = np.abs(right_hip.y - right_shoulder.y)
    else:
        torso_length = np.average(
            [
                np.abs(right_hip.y - right_shoulder.y),
                np.abs(left_hip.y - left_shoulder.y),
            ]
        )

    player_number = get_player_number(pose_landmarks)
    player_move = "Resting"
    
    print(f"Right wrist visibility: {right_wrist.visibility}")
    print(f"Left wrist visibility: {left_wrist.visibility}")
    print(f"Right shoulder visibility: {right_shoulder.visibility}")
    print(f"Left shoulder visibility: {left_shoulder.visibility}")
    print(f"Right hip visibility: {right_hip.visibility}")
    print(f"Left hip visibility: {left_hip.visibility}")
    
    if (
        right_wrist.visibility == 0
        or left_wrist.visibility == 0
        or right_shoulder.visibility == 0
        or left_shoulder.visibility == 0
        or right_hip.visibility == 0
        or left_hip.visibility == 0
    ):
        return tuple([player_number, player_move])

    if (
        abs(right_wrist.x - human_center_x) > TORSO_LENGTH_ARM_RATIO * torso_length
        or abs(left_wrist.x - human_center_x) > TORSO_LENGTH_ARM_RATIO * torso_length
    ):
        
        player_move = "Attack"
        
        if (
            right_wrist.y < (right_hip.y - (TORSO_LENGTH_ARM_RATIO * torso_length))
            and abs(left_wrist.x - human_center_x) > TORSO_LENGTH_ARM_RATIO * torso_length
        ) or (
            left_wrist.y < (left_hip.y - (TORSO_LENGTH_ARM_RATIO * torso_length))
            and abs(right_wrist.x - human_center_x) > TORSO_LENGTH_ARM_RATIO * torso_length
        ):
            player_move = "Special Attack"

    elif (
        right_wrist.y < (right_hip.y - (0.2 * torso_length))
        and right_wrist.y > right_shoulder.y
    ) or (
        left_wrist.y < (left_hip.y - (0.2 * torso_length))
        and left_wrist.y > left_shoulder.y
    ):
        player_move = "Defending"

    elif right_wrist.y < (right_shoulder.y + 0.15 * torso_length) or left_wrist.y < (
        left_shoulder.y + 0.15 * torso_length
    ):
        player_move = "Healing"

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

        if True:  # ! Disable for production
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


def scan(seconds, solo_play):
    global SOLO_PLAY
    
    pygame.init()
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("WizViz Pose Detection")


    def timer_callback():
        nonlocal running
        running = False

    timer = threading.Timer(seconds, timer_callback)
    timer.start()

    if solo_play:
        SOLO_PLAY = True
    p1_actions = [0, 0, 0, 0, 0]
    """[Resting, Defending, Attacking, Healing, Special Attack]"""
    p2_actions = [0, 0, 0, 0, 0]
    """[Resting, Defending, Attacking, Healing, Special Attack]"""

    actions = ["Resting", "Defending", "Attacking", "Healing", "Special Attack"]

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
                    # print(f"Player {action[0]}: {action[1]}")
                    if action[0] == 1:
                        if action[1] == "Resting":
                            p1_actions[0] += 1
                        elif action[1] == "Defending":
                            p1_actions[1] += 1
                        elif action[1] == "Attacking":
                            p1_actions[2] += 1
                        elif action[1] == "Healing":
                            p1_actions[3] += 1
                        else:
                            p1_actions[4] += 1
                    elif action[0] == 2:
                        if action[1] == "Resting":
                            p2_actions[0] += 1
                        elif action[1] == "Defending":
                            p2_actions[1] += 1
                        elif action[1] == "Attacking":
                            p2_actions[2] += 1
                        elif action[1] == "Healing":
                            p2_actions[3] += 1
                        else:
                            p2_actions[4] += 1
                    else:
                        continue

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
        # pygame.display.quit()
        
    max_action_index_p1 = np.argmax(p1_actions)
    max_action_index_p2 = np.argmax(p2_actions)
    if (SOLO_PLAY):
        return actions[max_action_index_p1]
    
    else:
        return tuple([actions[max_action_index_p1], actions[max_action_index_p2]])

print(scan(5, True))
