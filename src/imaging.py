import cv2
import pygame
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.framework.formats import landmark_pb2
import numpy as np

WIDTH, HEIGHT = 1920, 1080
"""Width and height of the Pygame screen"""
MIN_DETECTION_CONFIDENCE = 0.2
"""Confidence level required to establish a pose detection"""
MIN_TRACKING_CONFIDENCE = 0.2
"""Confidence level required to establish pose tracking"""
MIN_PRESENCE_CONFIDENCE = 0.2
"""Confidence level required to establish a pose presence"""
NUM_POSES = 2
"""Number of poses to detect"""
MODEL_PATH = "pose_landmarker_full.task"
"""Path to the pose landmarker model"""

pygame.init()
infoObject = pygame.display.Info()
# WIDTH, HEIGHT = infoObject.current_w, infoObject.current_h
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
screen = pygame.display.set_mode((infoObject.current_w, infoObject.current_h))

to_window = None
last_timestamp_ms = 0


# detection_result = None


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

    right_shoulder_x = pose_landmarks[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER].x
    left_shoulder_x = pose_landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER].x

    if right_shoulder_x == 0:
        human_center = left_shoulder_x
    elif left_shoulder_x == 0:
        human_center = right_shoulder_x
    else:
        human_center = np.average([right_shoulder_x, left_shoulder_x])

    shoulder_width = np.abs(right_shoulder_x - left_shoulder_x)

    player_number = 0
    player_move = "Resting"

    if human_center < 0.5:
        player_number = 1
    else:
        player_number = 2

    if (
        right_wrist_x == 0
        or left_wrist_x == 0
        or human_center == 0
        or shoulder_width == 0
    ):
        return tuple([player_number, player_move])

    if (
        abs(right_wrist_x - human_center) > 2 * shoulder_width
        or abs(left_wrist_x - human_center) > 2 * shoulder_width
    ):
        player_move = "Attack"

    # if (
    #     abs(right_ankle_x - human_center) > 2 * shoulder_width
    #     or abs(left_ankle_x - human_center) > 2 * shoulder_width
    # ):
    #     player_move = "Kick"

    if (
        abs(
            pose_landmarks[mp.solutions.pose.PoseLandmark.RIGHT_WRIST].x
            - pose_landmarks[mp.solutions.pose.PoseLandmark.LEFT_WRIST].x
        )
        < shoulder_width
        and abs(
            pose_landmarks[mp.solutions.pose.PoseLandmark.RIGHT_WRIST].y
            - pose_landmarks[mp.solutions.pose.PoseLandmark.LEFT_WRIST].y
        )
        < shoulder_width
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
        # print ("Pose ID:", idx)
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

        nose_pose = pose_landmarks[mp.solutions.pose.PoseLandmark.NOSE]
        # print(f"RGB Image Shape: {rgb_image.shape}")

        if detection_result is not None:
            for pose_landmarks in detection_result.pose_landmarks:
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
        # print(action)

        # print("Pose landmarks:", detection_result.pose_landmarks)
        # if detection_result.pose_landmarks:
        #     print("Pose landmarks[0]:", detection_result.pose_landmarks[0])

        if detection_result.pose_landmarks and True:  # Disable for now
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


def scan() -> any:
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

            # if detection_result is not None or detection_result.pose_landmarks:
            #     for pose_landmarks in detection_result.pose_landmarks:
            #         action = define_action(pose_landmarks)
            #         print(action)

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


scan()
