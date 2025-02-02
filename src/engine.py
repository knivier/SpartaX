import pygame
import imaging
import cv2
import mediapipe as mp
def run():
    # Initialize Pygame
    pygame.init()

    # Set up the display
    screen = pygame.display.set_mode((imaging.WIDTH, imaging.HEIGHT))
    pygame.display.set_caption('SpartaX Game')

    # Main game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Capture frame from the camera
        ret, frame = imaging.cap.read()
        if not ret:
            break

        # Flip and convert the frame to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Convert the frame to a MediaPipe Image object
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        timestamp_ms = int(cv2.getTickCount() / cv2.getTickFrequency() * 1000)

        # Perform pose detection asynchronously
        imaging.landmarker.detect_async(mp_image, timestamp_ms)

        if imaging.to_window is not None:
            # Rotate the frame 270 degrees
            frame_rotated = cv2.rotate(imaging.to_window, cv2.ROTATE_90_COUNTERCLOCKWISE)
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

    imaging.cap.release()
    pygame.quit()

if __name__ == "__main__":
    run()
