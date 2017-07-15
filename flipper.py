# Template for 2d-graph library.

import pygame, random, math, time, threading
pygame.display.init()
pygame.font.init()
######################################################################
# Classes ############################################################
######################################################################

FONT = pygame.font.SysFont('Arial', 30)

class Direction:
    LEFT= (0,1)
    RIGHT= (0,-1)
    UP= (1,1)
    DOWN= (1,-1)

    def values():
        return [Direction.LEFT, Direction.RIGHT, Direction.UP, Direction.DOWN]
    
class Object2D:
    
    """
    " Parent class for 2D objects.
    """
    def __init__(self, corners, color = 'White'):
        '''
        ' (x,y) is the position of the object.
        ' The default color is white.
        '''
        listOfCorners = []
        for corner in corners:
            listOfCorners.append(list(corner))
        self._position = listOfCorners
        self._color = color
        self._click_handlers = []
        self._mouse_drag_handlers = []
        self._draw_handlers = []
        self._animations = []
        self._rotation = 0
        
        
        
    ##################################################
    #####       MOUSE CLICK HANDLERS          #####
    ##################################################
    def getClickHandlers(self):
        return self._click_handlers
    
    def addClickHandler(self, handler, index = -1):
        index = max(index, min(len(self._click_handlers), 0) )
        self._click_handlers.insert(index, handler)
        return self
        
    def removeClickHandler(self, handler):
        self._click_handlers.remove(handler)
        return self
    
    def click(self, pos):
        for handler in self.getClickHandlers():
            handler(self, pos)
            
            
    
    ##################################################
    #####        MOUSE DRAG HANDLERS          #####
    ##################################################
    def getMouseDragHandlers(self):
        return self._mouse_drag_handlers
    
    def addMouseDragHandler(self, handler, index = -1):
        index = max(index, min(len(self._mouse_drag_handlers), 0) )
        self._mouse_drag_handlers.insert(index, handler)
        return self
        
    def removeMouseDragHandler(self, handler):
        self._mouse_drag_handlers.remove(handler)
        return self

    def mouseDrag(self, pos):
        for handler in self.getMouseDragHandlers():
            handler(self, pos)
            
            
    
    ##################################################
    #####           DRAW HANDLERS             #####
    ##################################################
    def addDrawHandler(self, handler, zindex = -1):
        zindex = max(zindex, min(len(self._draw_handlers), 0) )
        self._draw_handlers.insert(zindex, handler)
        return self
        
    def removeDrawHandler(self, handler):
        self._draw_handlers.remove(handler)
        return self
    
    def getDrawHandlers(self):
        return self._draw_handlers
            
            
    
    
    ##################################################
    #####           GETTER / SETTER           #####
    ##################################################
    def setColor(self, color):
        self._color = color
        
    def setPosition(self, position):
        self._position = list(position)
        
    def getColor(self):
        return self._color
    
    def getPosition(self):
        return self._position
    
    def getRotation(self):
        return self._rotation
            
            
    
    
    ##################################################
    #####              ANIMATIONS             #####
    ##################################################
    def getAnimations(self):
        return self._animations
    
    def addAnimation(self, animation):
        self._animations.append(animation)
        return self
    
    def stopAnimation(self, anim):
        self._animations.remove(anim)
    
    def stopAnimations(self):
        for animation in self.getAnimations():
            animation.stop()
        del self._animations[:]
        self._animations = []
        return self
    
    
    
    
    ##################################################
    #####            MOVE / SCALE             #####
    ##################################################
        
    def move(self, moveDirection, value):
        for i in range( len(self._position)):
            self._position[i][moveDirection[0]] -= moveDirection[1] * value
        return self
                
    def moveToPosition(self, pos):
        xs = []
        ys = []
        for point in self.getPosition():
            xs.append(point[0])
            ys.append(point[1])
        avg = [sum(xs) / len(xs), sum(ys) / len(ys)]
        deltas = []
        deltas.append(pos[0] - avg[0])
        deltas.append(pos[1] - avg[1])
        for i in range(len(self._position)):
            for j in range(2):
                self._position[i][j] += deltas[j]
        return self
        
    def scale(self, factor):            
        minX, minY = self.getPosition()[0]
        for point in self.getPosition()[1:]:
            if point[0] < minX:
                minX = point[0]
            if point[1] < minY:
                minY = point[1]
                
        minCoords = [minX, minY]     
        for i in range(len(self._position)):
            for j in range(2):
                delta = self._position[i][j] - minCoords[j]
                newCoord = minCoords[j] + (delta * factor)
                self._position[i][j] = newCoord
        return self
    
    def rotatePoint(centerPoint, point, angle):
        newPoint = [
            point[0] - centerPoint[0],
            point[1] - centerPoint[1]
        ]
        newPoint = [
            newPoint[0] * math.cos(angle) - newPoint[1] * math.sin(angle) ,
            newPoint[0] * math.sin(angle) + newPoint[1] * math.cos(angle)
        ]
        newPoint = [
            newPoint[0] + centerPoint[0],
            newPoint[1] + centerPoint[1]
        ]
        return newPoint
                
    def rotate(self, angle):
        self._rotation = angle
        xs = []
        ys = []
        for point in self.getPosition():
            xs.append(point[0])
            ys.append(point[1])
        center = [sum(xs) / len(xs), sum(ys) / len(ys)]
        
        angle = math.radians(angle)
        newPositions = []
        for corner in self.getPosition():
            newPositions.append( Object2D.rotatePoint(center, corner, angle) )
        self.setPosition(newPositions)
        return self
    
    def getBoundingRectangle(self):
        minX, minY = maxX, maxY = self.getPosition()[0]
        for point in self.getPosition()[1:]:
            if point[0] < minX:
                minX = point[0]
            elif point[0] > maxX:
                maxX = point[0]
            if point[1] < minY:
                minY = point[1]
            if point[1] > maxY:
                maxY = point[1]
                
        return [
            [minX, minY],
            [maxX, minY],
            [maxX, maxY],
            [minX, maxY],
        ]

    def draw(self, display):
        for handler in self.getDrawHandlers():
            handler(self, display)

        for ani in self.getAnimations():
            if not ani.running():
                self.stopAnimation(ani)
                continue
            elif (time.time() - ani.last) * 1000 >= ani.getInterval():
                ani.doTick()
                ani.last = time.time()
    
class Point( Object2D ):
    def __init__(self, x, y, color = 'White'):
        Object2D.__init__(self, [[x, y]], color = color)
        
    def draw(self, display):
        Object2D.draw(self, display)
        canvas.draw_point(self.getPosition()[0], self.getColor())
        
    def scale(self, factor):
        return
    
    def isPointInside(self, x, y):
        return [x, y] == self.getPosition()[0]

class Text( Object2D ):

    def __init__(self, pos, message, color = "white"):
        Object2D.__init__(self, [pos], color)
        self.message = message

    def draw(self, display):
        global FONT
        Object2D.draw(self, display)
        display.blit(FONT.render(self.message, False, (0, 0, 0)), self.getPosition()[0])

class Line( Object2D ):
    def __init__(self, points, color = 'White'):
        Object2D.__init__(self, points, color)
        
    def draw(self, display):
        Object2D.draw(self, display)
        
    def isPointInside(self, x, y, tolerance = 0):
        a  = self.getPosition()[0]
        b  = self.getPosition()[1]
        lengthca2  = (x - a[0])*(x - a[0]) + (y - a[1])*(y - a[1])
        lengthba2  = (b[0] - a[0])*(b[0] - a[0]) + (b[1] - a[1])*(b[1] - a[1])
        if lengthca2 > lengthba2: return False
        dotproduct = (x - a[0])*(b[0] - a[0]) + (y - a[1])*(b[1] - a[1])
        if dotproduct <= 0.0: return False
        if abs(dotproduct*dotproduct - lengthca2*lengthba2) > (self.getLineWidth() + tolerance) * 62500: return False 
        return True

class Circle( Object2D ):
    """
    " Class for a circle.
    """
    def __init__(self, x, y, r, fillColor = "transparent"):
        Object2D.__init__(self, [[x, y]], color = fillColor)
        assert r > 0, "Radius must be greater than 0"
        self._radius = r
        
    def getRadius(self):
        return self._radius
    
    def getDiameter(self):
        return 2 * self._radius
    
    def setRadius(self, radius):
        self._radius = radius
    
    def getDisplayedDiameter(self):
        return 2 * self.getRadius()
        
    def draw(self, display):
        Object2D.draw(self, display)
    
    def scale(self, factor):
        self._radius *= factor
        
    def getArea(self):
        return math.pi * (self.getRadius() ** 2)
    
    def isPointInside(self, x, y):
        absX = x - self.getPosition()[0][0]
        absY = y - self.getPosition()[0][1]
        return absY ** 2 + absX ** 2 <= self.getRadius() ** 2
    
    def getBoundingRectangle(self):
        rad = self.getDisplayedDiameter() / 2
        x, y = self.getPosition()[0]
        return [
            [x - rad, y - rad],
            [x + rad, y - rad],
            [x + rad, y + rad],
            [x - rad, y + rad],
        ]

class Polygon( Object2D ):
    """
    " Class for a polygon.
    """
    def __init__(self, corners, fillColor = "transparent"):
        
        assert len(corners) >= 2, "Corners must be a list of at least 2 elements"
        Object2D.__init__(self, corners, color = fillColor)
        
        for corner in corners:
            assert len(corner) is 2, "Corner element must be a list of X,Y"
        
    def draw(self, display):
        Object2D.draw(self, display)
        pygame.draw.polygon(display, self.getColor(), self.getPosition())
        
    def isPointInside(self, x, y):
        n = len(self.getPosition())
        inside = False

        p1x,p1y = self.getPosition()[0]
        for i in range(n+1):
            p2x,p2y = self.getPosition()[i % n]
            if y > min(p1y,p2y):
                if y <= max(p1y,p2y):
                    if x <= max(p1x,p2x):
                        if p1y != p2y:
                            xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x,p1y = p2x,p2y

        return inside
    
    def setCorner(self, idx, pos):
        p = self.getPosition()
        p[idx] = pos
        self.setPosition(p)
        
    def addToCorner(self, idx, coord, value):
        p = self.getPosition()
        p[idx][coord] += value
        self.setPosition(p)
    
class Image(Object2D):
    
    def __init__(self, imagePath, x, y):
        Object2D.__init__(self, [[x, y]])
        self.load(imagePath)
        
    def load(self, imagePath):
        self._path = imagePath
        self._img = pygame.image.load(imagePath)
        size = self._img.get_rect().size
        self._img = self._img.convert_alpha()
        self._width = size[0]
        self._height = size[1]
        return self
    
    def rotate(self, angle):
        self._rotation = angle
        self._img = pygame.transform.rotate(self._img, angle)
        self._img = self._img.convert_alpha()
        return self
        
    def getBounds(self):
        return (self._width, self._height)

    def getRealBounds(self):
        return self._img.get_rect().size

    def getWidth(self):
        return self._width

    def getHeight(self):
        return self._height
    
    def getPath(self):
        return self._path
    
    def getImage(self):
        return self._img
        
    def scaleWithFactor(self, factor):
        newBounds = (int(float(self._width) * factor), int(float(self._height) * factor))
        return self.scale(newBounds)

    def scale(self, newBounds):
        self._width = newBounds[0]
        self._height = newBounds[1]
        self._img = pygame.transform.smoothscale(self._img, newBounds).convert_alpha()
        return self
    
    def isPointInside(self, x, y):
        exit("isPointInside is not implemented for Image class")
        
    def draw(self, display):
        Object2D.draw(self, display)
        pos = self.getPosition()[0]
        bounds = self.getRealBounds()
        display.blit(self._img, [pos[0] - bounds[0] / 2, pos[1] - bounds[1] / 2])

    def getBoundingRectangle(self):
        x, y = self.getPosition()[0]
        w = self.getWidth() / 2
        h = self.getWidth() / 2
        return [
            [x - w, y - h],
            [x + w, y - h],
            [x + w, y + h],
            [x - w, y + h]
        ]
    
class Animation():
    
    def doTick(self):
        if self._maxTicks > 0:
            if self._ticks == self._maxTicks:
                self.stop()
                return
        self._action(self, self._obj, self._ticks)
        self._ticks += 1
        
    def running(self):
        return self._running
        
    def stop(self):
        self._running = False
        
    def getTicks(self):
        return self._ticks
    
    def getObject(self):
        return self._obj
    
    def getMaxTicks(self):
        return self._maxTicks
    
    def getInterval(self):
        return self._interval
    
    def __init__(self, obj, interval, action, maxTicks = -1):
        self._maxTicks = maxTicks
        self._action = action
        self._running = True
        self._interval = interval
        self._obj = obj
        self._ticks = 0
        self.last = time.time()
        
class Frame:
    
    def __init__(self, name = "", width = 200, height = 200, fps = 60):
        self._width = width
        self._height = height
        self._display = pygame.display.set_mode((width, height))
        pygame.display.set_caption(name)
        self._key_downs = []
        self._key_up = []
        self._draw_handlers = []
        self._objects = []
        self._click_handlers = []
        self._clock = pygame.time.Clock()
        self._event_handlers = {
            pygame.QUIT           : [],
            pygame.ACTIVEEVENT    : [],
            pygame.KEYDOWN        : [],
            pygame.KEYUP          : [],
            pygame.MOUSEMOTION    : [],
            pygame.MOUSEBUTTONUP  : [],
            pygame.MOUSEBUTTONDOWN: [],
            pygame.JOYAXISMOTION  : [],
            pygame.JOYBALLMOTION  : [],
            pygame.JOYHATMOTION   : [],
            pygame.JOYBUTTONUP    : [],
            pygame.JOYBUTTONDOWN  : [],
            pygame.VIDEORESIZE    : [],
            pygame.VIDEOEXPOSE    : [],
            pygame.USEREVENT      : []
        }
        self._fps = fps
        self._quit = False
        self.fpsval = 0
        
    def getObjects(self):
        return self._objects

    def addObject(self, obj, zindex = -1):
        zindex = max(zindex, min(len(self._objects), 0) )
        self._objects.insert(zindex, obj)
        return self
    
    def addObjects(self, objects):
        for obj in objects:
            self._objects.append(obj)
        return self
    
    def removeObject(self, obj):
        self._objects.remove(obj)
        return self
    
    
    def getWidth(self):
        return self._width
    
    def getHeight(self):
        return self._height
    
    def addDrawHandler(self, handler, zindex = -1):
        zindex = max(zindex, min(len(self._draw_handlers), 0) )
        self._draw_handlers.insert(zindex, handler)
        return self
        
    def removeDrawHandler(self, handler):
        self._draw_handlers.remove(handler)
        return self
    
    def getDrawHandlers(self):
        return self._draw_handlers
    
    def addEventHandler(self, eventType, handler, zindex = -1):
        zindex = max(zindex, min(len(self._event_handlers), 0))
        self._event_handlers[eventType].insert(zindex, handler)
        return self
    
    def getEventHandlers(self):
        return self._event_handlers

    def getEventHandlersForType(self, eventType):
        return self._event_handlers[eventType]

    def callHandlers(self, event):
        for handler in self.getEventHandlersForType(event.type):
            handler(event)

    def handleEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._quit = True
            self.callHandlers(event)
        
    def start(self):
        while not self._quit:
            self.handleEvents()
            self.draw(self._display)
            pygame.display.update()
            self.fpsval = 1000.0 / self._clock.tick(self._fps)
        pygame.display.quit()
        pygame.quit()
        exit()

    
    def draw(self, display):
        for obj in self.getObjects():
            obj.draw(display)
            
        for handler in self.getDrawHandlers():
            handler(display)
    
    def getFps(self):
        return self._fps
                
class CircleWithImage(Image, Circle):
    
    def __init__(self, x, y, r, uri):
        Circle.__init__(self, x, y, r, "transparent")
        Image.__init__(self, uri, x, y)
        self.origBounds = self.getBounds()
        Image.scaleWithFactor(self, r / float(self.getWidth() / 2))
        
    def rotate(self, angle):
        return Image.rotate(self, angle)

    def getOriginalBounds(self):
        return self.origBounds
        
    def draw(self, display):
        Image.draw(self, display)

    def isPointInside(self, x, y):
        return Circle.isPointInside(self, x, y)
    
                
class Ball(CircleWithImage):
    
    def __init__(self, x, y, r, uri):
        CircleWithImage.__init__(self, x, y, r, uri)
        self._angle = self._speed = 0
        
    def getAngle(self):
        return self._angle
    
    def setAngle(self, angle):
        self._angle = angle
        
    def getSpeed(self):
        return self._speed
    
    def setSpeed(self, speed):
        self._speed = speed
        
   
        
class FlipperFrame(Frame):
    
    def __init__(self, name = "", width = 200, height = 200):
        Frame.__init__(self, name, width, height)
        self._back_objs = []
        
    def getBackgroundObjects(self):
        return self._back_objs
    
    def addBackgroundObject(self, obj):
        self._back_objs.append(obj)
        return self
   
    def removeBackgroundObject(self, obj):
        self._back_objs.remove(obj)
        return self
    
    def draw(self, display):
        #display.fill([0,0,0])
        for obj in self.getBackgroundObjects():
            obj.draw(display)
        Frame.draw(self, display)
            
class BackgroundImage(Image):
    
    def __init__(self, frame, image_uri, x, y):
        Image.__init__(self, image_uri, x, y)
        self._frame = frame
        bounds = [self._frame.getWidth(), self._frame.getHeight()]
        self.scale(bounds)
        
class GameObject():
    
    def __init__(self, points, passive, delay):
        self._points = points
        self._passive = passive
        self.last_rollover = 0
        self.delay = delay

    def isPassive(self):
        return self._passive
    
    def getPoints(self):
        return self._points
    
    def action(self, pos, ball):
        return

    def rollOver(self, pos, ball):
        self.last_rollover = time.time()
        self.action(pos, ball)
    
    def isActionApplicable(self):
        return time.time() - self.last_rollover >= self.delay
    
    def shallAccelerate(self):
        return False
    
    def getNewSpeedFactor(self, sect, ballPos):
        return 1
        
class Paddle(GameObject, Polygon):
    
    def __init__(self, corners, isLeft, fillColor = "transparent"):
        Polygon.__init__(self, corners, fillColor)
        self.direction = -1
        self.angle = 0
        self.max_angle = 45
        self.isLeft = isLeft
        self.animation = None
        GameObject.__init__(self, 0, False, 0)
        
    def isInMotion(self):
        return (self.angle < self.max_angle and self.direction == 1) or (self.angle > 0 and self.direction == -1)
    
    def getNewSpeedFactor(self, sect, ballPos):
        return Physics.getNewSpeedFromDistance(sect[1], [sect[0][0], sect[0][1]])
        
    def rotate(self, angle):
        oldX, oldY = self.getPosition()[0]
        Polygon.rotate(self, angle)
        self.move(Direction.LEFT, self.getPosition()[0][0] - oldX)
        self.move(Direction.UP, self.getPosition()[0][1] - oldY)
        
    def changeRotation(self, ani, _, ticks):
        old = self.angle
        val = self.max_angle * self.direction * float(ticks) / float(ani.getMaxTicks())
        self.angle += val
        self.angle = min(self.max_angle, max(0, self.angle))
        rot = -(self.angle - old) if self.isLeft else (self.angle - old)
        self.rotate(rot)
        if ticks == ani.getMaxTicks() - 1:
            self.animation = None
            self.stopAnimation(ani)
            
    def goesUp(self):
        return self.direction == 1
    
    def setDirection(self, direct):
        self.direction = direct
        self.stopAnimations()
        self.animation = Animation(self, 1000.0 / 61.0, self.changeRotation, 15)
        self.addAnimation(self.animation)
        
    def toggleDirection(self):
        self.setDirection(-self.direction)
        
    def shallAccelerate(self):
        return self.goesUp() and self.animation is not None
    
class RolloverPoint(GameObject, CircleWithImage):
    
    def __init__(self, x, y, r, im1, im2, val):
        CircleWithImage.__init__(self, x, y, r, im1)
        GameObject.__init__(self, val, True, 0.5)
        self.imgs = [self._img, Image(im2, x, y).scale([r*2, r*2]).getImage()]
        
    def switchImage(self, ani, _, ticks):
        for img in self.imgs:
            if self._img != img:
                self._img = img
                return
        
   
    def action(self, pos, ball):
        self.switchImage(None, None, 0)
        self.addAnimation(Animation(self, 500, self.switchImage, 1))
        
class Boundary(GameObject, Polygon):
    
    def __init__(self, corners):
        Polygon.__init__(self, corners, pygame.Color("red"))
        GameObject.__init__(self, 0, False, 0)
        self._bounds = Polygon.getBoundingRectangle(self)
        
    def getBoundingRectangle(self):
        return self._bounds
    
    def draw(self, display):
        return
    
class Bouncer(GameObject, CircleWithImage):
    
    def __init__(self, x, y, r, im1, im2):
        CircleWithImage.__init__(self, x, y, r, im1)
        GameObject.__init__(self, 1000, False, 0.2)
        secondImage = Image(im2, x, y)

        factor = (r * 2) / self.getOriginalBounds()[0]
        secondImage.scaleWithFactor(factor)
        self.imgs = [self.scale([r*2, r*2]).getImage(), secondImage.getImage()]
        
    def switchImage(self, ani, _, ticks):
        for img in self.imgs:
            if self._img != img:
                self._img = img
                self._radius = self._img.get_rect().size[0] / 2
                return
   
    def action(self, pos, ball):
        self.switchImage(None, None, 0)
        self.addAnimation(Animation(self, 300, self.switchImage, 1))
    
    def getNewSpeedFactor(self, sect, ballPos):
        return 1.6
    
    
    


######################################################################
# GAME ###############################################################
######################################################################

class Physics():
    
    def getLineLengthSquared(line):
        deltaX = line[0][0] - line[1][0]
        deltaY = line[0][1] - line[1][1]
        return deltaX ** 2 + deltaY ** 2

    def isPointInsideRect(x, y, rect):
        return (x > rect[0][0]) and (x < rect[1][0]) and (y > rect[0][1]) and (y < rect[2][1])

    def rectangleCollision(rect1, rect2):
        for a, b in [(rect1, rect2), (rect2, rect1)]:
            if ((Physics.isPointInsideRect(a[0][0], a[0][1], b)) or
                (Physics.isPointInsideRect(a[0][0], a[2][1], b)) or
                (Physics.isPointInsideRect(a[1][0], a[0][1], b)) or
                (Physics.isPointInsideRect(a[1][0], a[2][1], b))):
                return True
        return False

    def closer(point, first, second):
        return first if abs(first - point) < abs(second - point) else second
    
    def lineDistanceToPoint(point, line):
        """
        Computes the minimum distance between a point (cx, cy) and a line segment with endpoints (ax, ay) and (bx, by).
        :param ax: endpoint 1, x-coordinate
        :param ay: endpoint 1, y-coordinate
        :param bx: endpoint 2, x-coordinate
        :param by: endpoint 2, y-coordinate
        :param cx: point, x-coordinate
        :param cy: point, x-coordinate
        :return: minimum distance between point and line segment
        """
        ax = float(line[0][0])
        ay = float(line[0][1])
        bx = float(line[1][0])
        by = float(line[1][1])
        cx = float(point[0])
        cy = float(point[1])

        if ay == by:
            if ax <= cx <= bx or ax >= cx >= bx:
                return [cx, ay, abs(cy - ay)]
            c = Physics.closer(cx, ax, bx)
            deltaX = cx - c
            deltaY = cy - ay
            return [c, ay, (deltaX ** 2 + deltaY ** 2) ** 0.5]
        elif ax == bx:
            if ay <= cy <= by or ay >= cy >= by:
                return [ax, cy, abs(cx - ax)]
            c = Physics.closer(cy, ay, by)
            deltaX = cx - ax
            deltaY= cy - c
            return [ax, c, (deltaX ** 2 + deltaY ** 2) ** 0.5]

        # avoid divide by zero error
        a = by - ay
        b = ax - bx
        # compute the perpendicular distance to the theoretical infinite line
        dl = abs(a * cx + b * cy - b * ay - a * ax) / math.sqrt(a**2 + b**2)
        # compute the intersection point
        x = ((a / b) * ax + ay + (b / a) * cx - cy) / ((b / a) + (a / b))
        y = -1 * (a / b) * (x - ax) + ay
        # decide if the intersection point falls on the line segment
        if (ax <= x <= bx or bx <= x <= ax) and (ay <= y <= by or by <= y <= ay):
            return [x, y, dl]
        else:
            # if it does not, then return the minimum distance to the segment endpoints
            r1 = math.sqrt((ax - cx)**2 + (ay - cy)**2)
            r2 = math.sqrt((bx - cx)**2 + (by - cy)**2)
            if r1 < r2:
                return [ax, ay, r1]
            else:
                return [bx, by, r2]

    def getNearestPointOnLine(circle, pol):
        pos = pol.getPosition()
        dist = 10000000
        ret = []
        for i in range(-1, len(pos) - 1):
            line = [pos[i], pos[i + 1]]
            sect = Physics.lineDistanceToPoint(circle, line)
            if sect != None:
                if sect[2] < dist:
                    dist = sect[2]
                    ret = [sect, line]
        return ret
    
    def getNearestPointBetweenCircles(circ, pos, r1, r2):        
        x1,y1 = circ
        x2,y2 = pos
        dx,dy = x2-x1,y2-y1
        d = (dx*dx+dy*dy) ** 0.5
        
        if d > r1+r2:
            return None
        if d < abs(r1-r2):
            return None
        if d == 0 and r1 == r2:
            return None
        a = (r1*r1-r2*r2+d*d)/(2*d)
        h = (r1*r1-a*a) ** 0.5
        xm = x1 + a*dx/d
        ym = y1 + a*dy/d
        xs1 = xm + h*dy/d
        xs2 = xm - h*dy/d
        ys1 = ym - h*dx/d
        ys2 = ym + h*dx/d
        point = [(xs1 + xs2) / 2, (ys1 + ys2) /2 ]
        return [[point[0], point[1], d], [ [xs1, ys1], [xs2, ys2] ]]
        
    def addVectors(angle1, length1, angle2, length2):
        x  = math.sin(angle1) * length1 + math.sin(angle2) * length2
        y  = math.cos(angle1) * length1 + math.cos(angle2) * length2

        angle = 0.5 * math.pi - math.atan2(y, x)
        length  = math.hypot(x, y)

        return (angle, length)

    def getNewSpeedFromDistance(line, point):
        dist = math.hypot(line[0][0] - point[0], line[0][1] - point[1])
        lineLen = math.hypot(line[0][0] - line[1][0], line[0][1] - line[1][1])
        return 1 + (dist * 0.9 / lineLen) + (random.random() / 2.0)

class Game():
    
    def __init__(self, title, width, height, startPoints, debug = True):
        self.width = width
        self.height = height
        self.startPoints = startPoints
        self.initialize()
        self.debug = debug
        self.frame = FlipperFrame(title, width, height)

        self.startX = width - 65
        self.startY = height - 40

        self.lose_bounds = [int(float(self.width) * 468.0 / 1080.0),
                            int(float(self.width) * 627.0 / 1080.0)]     #468 627 bei 1080 width 

        self.initializeTexts()
        
        self.frame.addDrawHandler(self.drawFPS)

    def initialize(self):
        self.points = self.startPoints
        self.balls = []
        self.ball_radius = 18
        self.ball_drag = 0.999
        self.max_speed = 20
        self.gravity = 0.34
        self.bounce_elasticity = 0.75
        self.running = False

    def initializeTexts(self):
        if self.debug:
            self.fpsText = Text([10, 10], "FPS", pygame.Color("black"))
            self.spriteText = Text([10, 50], "Sprites", pygame.Color("black"))
            self.speedText = Text([10, 90], "Speed", pygame.Color("black"))
            self.frame.addObject(self.fpsText)
            self.frame.addObject(self.spriteText)
            self.frame.addObject(self.speedText)
        # TODO: add points text
        
    def addBall(self):
        ball = Ball(self.startX, self.startY, self.ball_radius, Game.getUrl("ball.png"))
        ball.addAnimation(Animation(ball, 5, self.ballTick))
        ball.setSpeed(40)
        ball.setAngle(math.pi)
        self.balls.append(ball)
        zindex = len(self.frame.getObjects()) - 1
        self.frame.addObject(ball, zindex)
        
    def addPoints(self, points):
        self.points += points
        #print("New points:", self.points)

    def end(self):
        self.running = False
        self.reset()
        self.addBall()
        self.running = True

    def checkForEnd(self, pos):
        return pos[0] >= self.lose_bounds[0] and pos[0] <= self.lose_bounds[1]
        
    def drawFPS(self, display):
        #display.draw_polygon([[0,0], [300,0], [300,190], [0,190]], 1, "transparent", "rgba(,0.8)")
        #canvas.draw_text( str(self.fps), (20, 50), 40, 'Black', "sans-serif")
        self.spriteText.message = str(len(self.frame.getObjects())) + " sprites"
        self.speedText.message = "%.1f" % round(self.balls[0].getSpeed(),2) + " ball speed"
        self.fpsText.message = "%.1f" % round(self.frame.fpsval,2)
        
    def ballBounce(self, ball):
        pos = ball.getPosition()[0]
        radius = ball.getDisplayedDiameter() / 2
        angle = ball.getAngle()
        speed = ball.getSpeed()
        for obj in self.frame.getObjects():
            if obj == ball:
                continue
            if not isinstance(obj, GameObject):
                continue
            if not Physics.rectangleCollision(ball.getBoundingRectangle(), obj.getBoundingRectangle()):
                continue
                
            if isinstance(obj, Polygon):
                sect = Physics.getNearestPointOnLine(pos, obj)
                # 2 for the Linewidth
                touches = sect[0][2] <= ball.getRadius() + speed * 2.0 / 3.0
            elif isinstance(obj, Circle):
                sect = Physics.getNearestPointBetweenCircles(pos, obj.getPosition()[0], radius, obj.getRadius())
                if sect is None:
                    continue
                touches = sect[0][2] - obj.getRadius() <= ball.getRadius() + speed * 2.0 / 3.0
                
            inside = obj.isPointInside(pos[0], pos[1])

            if inside or touches:
                points = obj.getPoints()
                if obj.isActionApplicable():
                    obj.rollOver([sect[0][0], sect[0][1]], ball)
                    if not isinstance(obj, Paddle) and points > 0:
                        self.addPoints(points)
                if obj.isPassive():
                    continue
                if not obj.shallAccelerate():
                    val = 0.95 if sect[0][1] > pos[1] else 0.6
                    #if isinstance(obj, Paddle):
                    #    print("Not shallAccelerate", val)
                elif isinstance(obj, Boundary):
                    val = 0.7
                else:
                    val = obj.getNewSpeedFactor(sect, pos)
                speed *= val
                
                if touches:
                    tangent = math.atan2(sect[0][1] - pos[1], sect[0][0] - pos[0])
                    angle = 2 * tangent - angle
                    dist = sect[0][2]
                    hitAngle = 0.5 * math.pi + tangent
                    pos[0] -= math.sin(hitAngle) * abs(ball.getRadius() - dist)
                    pos[1] += math.cos(hitAngle) * abs(ball.getRadius() - dist)
                elif inside:
                    oldPos = pos
                    pos = [2 * sect[0][0] - pos[0], 2 * sect[0][1] - pos[1]]
                    pos[1] += (4 if pos[1] >= oldPos[1] else -4)
                    
                if isinstance(obj, Paddle) and obj.goesUp() and obj.angle < obj.max_angle:
                    angle = (0 - obj.direction) * ((obj.angle - 38) * math.pi / 180)
                    
        if pos[0] > self.width - radius:
            pos[0] = 2*(self.width - radius) - pos[0]
            angle = - angle
            speed *= self.bounce_elasticity
        elif pos[0] < radius:
            pos[0] = 2*radius - pos[0]
            angle = - angle
            speed *= self.bounce_elasticity
        if pos[1] > self.height - radius:
            if self.checkForEnd(pos):
                self.end()
                return
            pos[1] = 2 * (self.height - radius) - pos[1]
            angle = math.pi - angle
            speed *= self.bounce_elasticity
        elif pos[1] < radius:
            pos[1] = 2 * radius - pos[1]
            angle = math.pi - angle
            speed *= self.bounce_elasticity
        ball.setSpeed(speed)
        ball.setAngle(angle)
        ball.setPosition( [ pos ] )
        
    def ballTick(self, ani, ball, ticks):
        if not self.running:
            return
        pos = ball.getPosition()[0]
        angle = ball.getAngle()
        speed = ball.getSpeed()

        (angle, speed) = Physics.addVectors(angle, speed, math.pi, self.gravity)

        pos[0] += math.sin(angle) * speed
        pos[1] -= math.cos(angle) * speed

        ball.setAngle(angle)
        ball.setSpeed(min(self.max_speed, speed * self.ball_drag))
        self.ballBounce(ball)

    def getUrl(name):
        return "assets/" + name
        
    def start(self):
        self.running = True
        if self.frame is None or self.frame._quit is True:
            return
        self.frame.start()
        
    def reset(self):
        self.points = self.startPoints
        for ball in self.balls:
            ball.stopAnimations()
            self.frame.removeObject(ball)
        self.balls = []

WIDTH = 720
HEIGHT = 1280

game = Game("Flipper Game", WIDTH, HEIGHT, 1000, True)
game.startX = 300
game.startY = 500
game.addBall()
        
game.frame.addBackgroundObject( BackgroundImage(game.frame, Game.getUrl("Background.png"), WIDTH / 2, HEIGHT / 2) )

padCordLeftLeft = [
    [ int(0.161111111111 * float(WIDTH) ), int( 0.80859375 * float(HEIGHT) )],
    [ int(0.173611111111 * float(WIDTH) ), int( 0.80234375 * float(HEIGHT) )],
    [ int(0.180555555556 * float(WIDTH) ), int( 0.8015625 * float(HEIGHT) )],
    [ int(0.2875 * float(WIDTH) ), int( 0.85546875 * float(HEIGHT) )],
    [ int(0.291666666667 * float(WIDTH) ), int( 0.859375 * float(HEIGHT) )],
    [ int(0.294444444444 * float(WIDTH) ), int( 0.8640625 * float(HEIGHT) )],
    [ int(0.286111111111 * float(WIDTH) ), int( 0.86328125 * float(HEIGHT) )],
    [ int(0.280555555556 * float(WIDTH) ), int( 0.86171875 * float(HEIGHT) )],
    [ int(0.154166666667 * float(WIDTH) ), int( 0.8203125 * float(HEIGHT) )],
    [ int(0.154166666667 * float(WIDTH) ), int( 0.8171875 * float(HEIGHT) )]
]

padCordLeftRight = [ 
    [ int(0.3125 * float(WIDTH) ), int( 0.87890625 * float(HEIGHT) )],
    [ int(0.326388888889 * float(WIDTH) ), int( 0.87265625 * float(HEIGHT) )],
    [ int(0.331944444444 * float(WIDTH) ), int( 0.871875 * float(HEIGHT) )],
    [ int(0.440277777778 * float(WIDTH) ), int( 0.92578125 * float(HEIGHT) )],
    [ int(0.444444444444 * float(WIDTH) ), int( 0.9296875 * float(HEIGHT) )],
    [ int(0.448611111111 * float(WIDTH) ), int( 0.934375 * float(HEIGHT) )],
    [ int(0.440277777778 * float(WIDTH) ), int( 0.93359375 * float(HEIGHT) )],
    [ int(0.431944444444 * float(WIDTH) ), int( 0.93203125 * float(HEIGHT) )],
    [ int(0.308333333333 * float(WIDTH) ), int( 0.890625 * float(HEIGHT) )],
    [ int(0.308333333333 * float(WIDTH) ), int( 0.8875 * float(HEIGHT) )]
]

padCordRight = [
    [ int(0.704166666667 * float(WIDTH) ), int( 0.87890625 * float(HEIGHT) )],
    [ int(0.691666666667 * float(WIDTH) ), int( 0.87265625 * float(HEIGHT) )],
    [ int(0.684722222222 * float(WIDTH) ), int( 0.871875 * float(HEIGHT) )],
    [ int(0.576388888889 * float(WIDTH) ), int( 0.92578125 * float(HEIGHT) )],
    [ int(0.573611111111 * float(WIDTH) ), int( 0.9296875 * float(HEIGHT) )],
    [ int(0.568055555556 * float(WIDTH) ), int( 0.934375 * float(HEIGHT) )],
    [ int(0.577777777778 * float(WIDTH) ), int( 0.93359375 * float(HEIGHT) )],
    [ int(0.586111111111 * float(WIDTH) ), int( 0.93203125 * float(HEIGHT) )],
    [ int(0.709722222222 * float(WIDTH) ), int( 0.890625 * float(HEIGHT) )],
    [ int(0.709722222222 * float(WIDTH) ), int( 0.8875 * float(HEIGHT) )]
]

gameBoundaries = [
    [ int(0.0 * float(WIDTH) ), int( 0.60546875 * float(HEIGHT) )],
    [ int(0.0611111111111 * float(WIDTH) ), int( 0.61015625 * float(HEIGHT) )],
    [ int(0.0611111111111 * float(WIDTH) ), int( 0.25234375 * float(HEIGHT) )],
    [ int(0.0416666666667 * float(WIDTH) ), int( 0.23203125 * float(HEIGHT) )],
    [ int(0.0944444444444 * float(WIDTH) ), int( 0.14609375 * float(HEIGHT) )],
    [ int(0.205555555556 * float(WIDTH) ), int( 0.08203125 * float(HEIGHT) )],
    [ int(0.319444444444 * float(WIDTH) ), int( 0.05390625 * float(HEIGHT) )],
    [ int(0.491666666667 * float(WIDTH) ), int( 0.03984375 * float(HEIGHT) )],
    [ int(0.752777777778 * float(WIDTH) ), int( 0.07265625 * float(HEIGHT) )],
    [ int(0.902777777778 * float(WIDTH) ), int( 0.13671875 * float(HEIGHT) )],
    [ int(0.958333333333 * float(WIDTH) ), int( 0.20859375 * float(HEIGHT) )],
    [ int(0.972222222222 * float(WIDTH) ), int( 0.56484375 * float(HEIGHT) )],
    [ int(1.0 * float(WIDTH) ), int( 0.57734375 * float(HEIGHT) )],
    [ int(1.0 * float(WIDTH) ), int( 0.5625 * float(HEIGHT) )],
    [ int(1.0 * float(WIDTH) ), int( 0.0 * float(HEIGHT) )],
    [ int(0.0 * float(WIDTH) ), int( 0.0 * float(HEIGHT) )]
]

gameBoundariesLowerLeft = [
    [ int(0.0 * float(WIDTH) ), int( 0.8640625 * float(HEIGHT) )],
    [ int(0.0277777777778 * float(WIDTH) ), int( 0.8640625 * float(HEIGHT) )],
    [ int(0.436111111111 * float(WIDTH) ), int( 0.99453125 * float(HEIGHT) )],
    [ int(0.436111111111 * float(WIDTH) ), int( 1.0 * float(HEIGHT) )],
    [ int(0.0 * float(WIDTH) ), int( 1.0 * float(HEIGHT) )]
]

gameBoundariesLowerRight = [
    [ int(0.577777777778 * float(WIDTH) ), int( 0.99453125 * float(HEIGHT) )],
    [ int(0.972222222222 * float(WIDTH) ), int( 0.8640625 * float(HEIGHT) )],
    [ int(1.0 * float(WIDTH) ), int( 0.8640625 * float(HEIGHT) )],
    [ int(1.0 * float(WIDTH) ), int( 1.0 * float(HEIGHT) )],
    [ int(0.577777777778 * float(WIDTH) ), int( 1.0 * float(HEIGHT) )]
]

rollInBoundaries = [
    [ int(0.875 * float(WIDTH) ), int( 0.89609375 * float(HEIGHT) )],
    [ int(0.869444444444 * float(WIDTH) ), int( 0.25546875 * float(HEIGHT) )],
    [ int(0.841666666667 * float(WIDTH) ), int( 0.19609375 * float(HEIGHT) )],
    [ int(0.805555555556 * float(WIDTH) ), int( 0.16640625 * float(HEIGHT) )],
    [ int(0.747222222222 * float(WIDTH) ), int( 0.13828125 * float(HEIGHT) )],
    [ int(0.658333333333 * float(WIDTH) ), int( 0.12109375 * float(HEIGHT) )],
    [ int(0.661111111111 * float(WIDTH) ), int( 0.10078125 * float(HEIGHT) )],
    [ int(0.775 * float(WIDTH) ), int( 0.12265625 * float(HEIGHT) )],
    [ int(0.844444444444 * float(WIDTH) ), int( 0.15859375 * float(HEIGHT) )],
    [ int(0.883333333333 * float(WIDTH) ), int( 0.20390625 * float(HEIGHT) )],
    [ int(0.897222222222 * float(WIDTH) ), int( 0.25390625 * float(HEIGHT) )],
    [ int(0.9 * float(WIDTH) ), int( 0.89453125 * float(HEIGHT) )]
]

bouncerCoords = [
    [ int(0.316666666667 * float(WIDTH) ), int( 0.234375 * float(HEIGHT) )],
    [ int(0.5 * float(WIDTH) ), int( 0.34921875 * float(HEIGHT) )],
    [ int(0.694444444444 * float(WIDTH) ), int( 0.234375 * float(HEIGHT) )]
]

drahtLeftCoords = [
    [ int(0.0388888888889 * float(WIDTH) ), int( 0.8109375 * float(HEIGHT) )],
    [ int(0.0611111111111 * float(WIDTH) ), int( 0.803125 * float(HEIGHT) )],
    [ int(0.144444444444 * float(WIDTH) ), int( 0.88515625 * float(HEIGHT) )],
    [ int(0.108333333333 * float(WIDTH) ), int( 0.890625 * float(HEIGHT) )]
]

drahtRightCoords = [
    [ int(0.831944444444 * float(WIDTH) ), int( 0.821875 * float(HEIGHT) )],
    [ int(0.848611111111 * float(WIDTH) ), int( 0.83671875 * float(HEIGHT) )],
    [ int(0.713888888889 * float(WIDTH) ), int( 0.88359375 * float(HEIGHT) )],
    [ int(0.695833333333 * float(WIDTH) ), int( 0.86796875 * float(HEIGHT) )]
]

for pos in bouncerCoords:
    bouncer = Bouncer(pos[0], pos[1], 50, Game.getUrl("Bouncer_0.png"), Game.getUrl("Bouncer_1.png"))
    game.frame.addObject(bouncer)

paddleColor     = pygame.Color(251, 246, 228, 255)
paddleLeftLeft  = Paddle(padCordLeftLeft , True,  fillColor = paddleColor)
paddleLeftRight = Paddle(padCordLeftRight, True,  fillColor = paddleColor)
paddleRight     = Paddle(padCordRight    , False, fillColor = paddleColor)

SHOULD_MOVE_FOR_DEBUG = False

if SHOULD_MOVE_FOR_DEBUG:
    down = 20
    paddleLeftLeft.move(Direction.DOWN, down)
    paddleLeftRight.move(Direction.DOWN, down)
    paddleRight.move(Direction.DOWN, down)

    print(paddleLeftLeft   .move(Direction.RIGHT, 80).move(Direction.DOWN, 10).getPosition())
    print(paddleLeftRight  .move(Direction.RIGHT, 50).getPosition())
    print(paddleRight      .move(Direction.LEFT, 10).getPosition())






paddles = [paddleLeftLeft, paddleLeftRight]
game.frame.addObjects(paddles).addObject(paddleRight)


rolloverPadding = 40
rowPadding = 25
radius = 25
center = float(WIDTH) / 2.0
startY = 1100
idx = 0
for row in range(4):
    y = startY - ((rowPadding + radius) * row)
    for point in range(row+1):
        idx += 1
        x = center - ((row/2.0 -point) * (rolloverPadding + radius))
        src = "Number{}_{}.png"
        game.frame.addObject(RolloverPoint(x, y, radius, Game.getUrl(src.format(idx,0)), Game.getUrl(src.format(idx,1)), idx*100), 0)

boundaries = [
    gameBoundaries,
    gameBoundariesLowerLeft,
    gameBoundariesLowerRight,
    rollInBoundaries,
    drahtRightCoords,
    drahtLeftCoords   
]

for boundary in boundaries:
    game.frame.addObject(Boundary(boundary))

def togglePaddles(event):
    print(event.pos)
    if event.button == 1:
        global paddles
        for pad in paddles:
            pad.toggleDirection()
    elif event.button == 3:
        global paddleRight
        paddleRight.toggleDirection()

handlers = {
    pygame.MOUSEBUTTONUP: togglePaddles,
    pygame.MOUSEBUTTONDOWN: togglePaddles
}

for event in handlers:
    game.frame.addEventHandler(event, handlers[event])
game.start()
