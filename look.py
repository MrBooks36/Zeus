def look():
    import cv2
    from ohbotfix import ohbot
    from time import sleep, time
    import random

    ohbot.reset()

    cascPath = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    print("Haar definitions loaded from:", cascPath)
    faceCascade = cv2.CascadeClassifier(cascPath)

    print("Initializing camera")
    video_capture = cv2.VideoCapture(0)

    if video_capture.isOpened():
        print("Camera Initialized")
        ohbot.setEyeColour(g=10, r=0, b=0)
        sleep(0.5)
        ohbot.setEyeColour(g=0, r=0, b=0)

        last_blink_time = time()
        blink_interval = random.uniform(3, 7)

        while True:
            ret, frame = video_capture.read()
            if not ret or frame is None:
                print("No frame received")
                continue

            height, width, _ = frame.shape
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            faces = faceCascade.detectMultiScale(
                gray,
                scaleFactor=1.3,
                minNeighbors=5,
                minSize=(50, 50)
            )

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                faceX = (x + w / 2) / width * 10
                faceY = (y + h / 2) / height * 10

                ohbot.move(ohbot.HEADNOD, 10 - faceY, 10)
                ohbot.move(ohbot.EYETURN, faceX, 10)
                ohbot.move(ohbot.EYETILT, faceY, 10)

                break

            current_time = time()
            if current_time - last_blink_time > blink_interval:
                ohbot.move(ohbot.LIDBLINK, 0, 5)  # Close lids
                sleep(0.2)
                ohbot.move(ohbot.LIDBLINK, 10, 5)   # Open lids
                last_blink_time = current_time
                blink_interval = random.uniform(3, 7)

            cv2.imshow("Video", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        video_capture.release()
        cv2.destroyAllWindows()
    else:
        print("No camera found")
