import cv2


class CenterFinder():
    def __init__(self):
        self.whiteOnBlack = False

        self.SCREEN_HEIGHT = 480
        self.SCREEN_WIDTH = 640

        self.ROI_WIDTH_X = 250
        self.ROI_WIDTH_Y = 250

        # self.ROI_OFFSET_X = int(self.SCREEN_WIDTH / 2 - self.ROI_WIDTH_X / 2)
        # self.ROI_OFFSET_Y = int(self.SCREEN_HEIGHT / 2 - self.ROI_WIDTH_Y / 2)

    def showCenters(self, image, centers):
        """
        utility function to show center points on an image.
        :param image:
        :param centers:
        Array of centerpoint pairs
        :return:
        A drawn image
        """
        for centerPair in centers:
            circle_center_x = centerPair[0]
            circle_center_y = centerPair[1]
            cv2.circle(image, center=(circle_center_x, circle_center_y), radius=3, color=(0, 0, 255),
                       thickness=3)

        return image

    def sort_contours(self,cnts, method="left-to-right"):
        # initialize the reverse flag and sort index
        reverse = False
        i = 0
        # handle if we need to sort in reverse
        if method == "right-to-left" or method == "bottom-to-top":
            reverse = True
        # handle if we are sorting against the y-coordinate rather than
        # the x-coordinate of the bounding box
        if method == "top-to-bottom" or method == "bottom-to-top":
            i = 1
        # construct the list of bounding boxes and sort them from top to
        # bottom
        boundingBoxes = [cv2.boundingRect(c) for c in cnts]
        (cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes),
                                            key=lambda b: b[1][i], reverse=reverse))
        # return the list of sorted contours and bounding boxes
        return (cnts, boundingBoxes)

    def findCentersOfCircles(self,image, roi_boundingBox):
        """
        :param image:
        :param roi_boundingBox:
        array containing: [x,y,w,h]
        where x,y is top left corner of the roi
        where w,h is width and height respectively
        :return:
        returns an image for debugging purposes
        returns an array of coordinate pairs, in absolute terms (based on the original image) of the centerpoint of the circles.
        """
        imgray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # cv2.imshow("thresh", thresh)
        x = roi_boundingBox[0]
        w = roi_boundingBox[2]

        y = roi_boundingBox[1]
        h = roi_boundingBox[3]

        roi = imgray[y:y + h, x:x + w]
        color_roi = image[y:y + h, x:x + w]

        if self.whiteOnBlack:
            ret, roi = cv2.threshold(roi, 150, 255, cv2.THRESH_OTSU)
            # ret, roi = cv2.threshold(roi, 50, 255, cv2.THRESH_BINARY)
        else:
            ret, roi = cv2.threshold(roi, 150, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        try:
            im, contours, hierarchy = cv2.findContours(roi, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            contours, _ = self.sort_contours(contours)
            # cv2.imshow("Roi", roi)
            cv2.drawContours(color_roi, contours, -1, (0, 255, 0), 3)
            # Get center using moments
        except Exception as e:
            print(e)
            return roi, []

        height_text = 20
        centerPoints = []

        for cnt in contours:
            try:
                moment = cv2.moments(cnt)
                circle_center_x = int(moment['m10'] / (moment['m00'] + 0.0001))
                circle_center_y = int(moment['m01'] / (moment['m00'] + 0.0001))
                cv2.circle(color_roi, center=(circle_center_x, circle_center_y), radius=3, color=(0, 0, 255),
                           thickness=3)
                # cv2.putText(color_roi, "CENTER_X: " + str(circle_center_x), (0, height_text), cv2.FONT_HERSHEY_SIMPLEX,
                #             0.6, (255, 0, 0))
                # height_text += 20
                # cv2.putText(color_roi, "CENTER_Y: " + str(circle_center_y), (0, height_text), cv2.FONT_HERSHEY_SIMPLEX,
                #             0.6, (255, 0, 0))
                # height_text += 20
                centerPoints.append([circle_center_x + x, circle_center_y + y])
            except Exception as e:
                return roi, centerPoints
                print(e)

        return roi, centerPoints