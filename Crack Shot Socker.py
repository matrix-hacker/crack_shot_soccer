import pygame, sys, math
from time import sleep

"""
Pro soccer players need to be able to put the ball on target at will.
Crack Shot Soccer wants to help you get to their level.
Every play gets you 10 shots to prove your skills. Can you hack it?
"""

pygame.init()

# define fonts and colors used throughout
largeText = pygame.font.Font('freesansbold.ttf',90)
medText = pygame.font.Font('freesansbold.ttf',75)
medSmallText = pygame.font.Font('freesansbold.ttf',30)
smallText = pygame.font.Font('freesansbold.ttf',20)
black = (0,0,0)
white = (255,255,255)
red = (255,0,0)
blue = (0,0,255)

# set screen variables used throughout
width = 900
height = 700
screenDim = (width,height)

# create the screen
screen = pygame.display.set_mode((screenDim))
pygame.display.set_caption("Crack Shot Soccer")

class Game:
    '''The class from which all classes are born'''
    def __init__(self,screen,screenDimensions):
        self.fps = 30
        self.screenDimensions = screenDimensions
        self.frame = pygame.time.Clock()
        self.screen = screen
        
    def updateFrame(self):
        self.frame.tick(self.fps)
        pygame.display.flip()

class Background(Game):
    '''White backgrounds went out of style YEARS ago'''
    def __init__(self,screen,screenDimensions):
        Game.__init__(self,screen,screenDimensions)
        self.goalLeft = None
        self.goalMiddle = None
        self.goalRight = None
        self.adjust = 12
        self.grassImage = None

    def loadGrass(self,name):
        self.grassImage = pygame.image.load(name).convert()
        self.grassImage = pygame.transform.scale(self.grassImage,
                                    self.screenDimensions)

    def cropSurface(self,newWidth,newHeight,cropWidth,cropHeight,image):
        newSurf = pygame.Surface((newWidth,newHeight),pygame.SRCALPHA,32)
        newSurf.blit(image,(0,0),(cropWidth,cropHeight,newWidth,newHeight))
        return newSurf

    def loadGoalLeft(self,name):
        self.goalLeft = pygame.image.load(name).convert_alpha()
        self.goalLeft = pygame.transform.scale(self.goalLeft,(250,270))
        goalLeftWidth = self.goalLeft.get_rect().width
        goalLeftHeight = self.goalLeft.get_rect().height
        self.goalLeft = self.cropSurface(goalLeftWidth/2+self.adjust,goalLeftHeight/2+self.adjust,goalLeftWidth/2-self.adjust,goalLeftHeight/2-self.adjust,self.goalLeft)

    def loadGoalMiddle(self,name):
        self.goalMiddle = pygame.image.load(name).convert_alpha()
        self.goalMiddle = pygame.transform.scale(self.goalMiddle,(250,270))
        goalMiddleWidth = self.goalMiddle.get_rect().width
        goalMiddleHeight = self.goalMiddle.get_rect().height
        self.goalMiddle = self.cropSurface(goalMiddleWidth,goalMiddleHeight/2+self.adjust,0,goalMiddleHeight/2-self.adjust,self.goalMiddle)

    def loadGoalRight(self,name):
        self.goalRight = pygame.image.load(name).convert_alpha()
        self.goalRight = pygame.transform.scale(self.goalRight,(250,270))
        goalRightWidth = self.goalRight.get_rect().width
        goalRightHeight = self.goalRight.get_rect().height
        self.goalRight = self.cropSurface(goalRightWidth/2+self.adjust,goalRightHeight/2+self.adjust,0,goalRightHeight/2-self.adjust,self.goalRight)

    def setStart(self):
        self.goalStart = (self.screenDimensions[0]-self.goalLeft.get_rect().width-self.goalMiddle.get_rect().width-self.goalRight.get_rect().width)/2

    def blitBackground(self):
        self.screen.blit(self.grassImage,(0,0))
        self.screen.blit(self.goalLeft,(self.goalStart,0))
        self.screen.blit(self.goalMiddle,(self.goalStart+self.goalLeft.get_rect().width,0))
        self.screen.blit(self.goalRight,(self.goalStart+self.goalLeft.get_rect().width+self.goalMiddle.get_rect().width,0))

class Ball(Game):
    '''Hard to play with no ball.'''
    def __init__(self,screen,screenDimensions):
        Game.__init__(self,screen,screenDimensions)
        self.ballX = self.screenDimensions[0]/2
        self.ballY = 450
        self.ballXOriginal = self.ballX
        self.ballYOriginal = self.ballY
        self.ball = None

    def resetBall(self):
        '''Return ball to original position'''
        self.ballX = self.ballXOriginal
        self.ballY = self.ballYOriginal

    def loadBall(self,name,rescaleBall):
        self.ball = pygame.image.load(name).convert_alpha()
        ballWidth = self.ball.get_rect().width
        ballHeight = self.ball.get_rect().height
        self.ball = pygame.transform.scale(self.ball,(ballWidth*rescaleBall,ballHeight*rescaleBall))
        
    def blitBall(self):
        self.screen.blit(self.ball,(self.ballX-self.ball.get_rect().width/2,self.ballY-self.ball.get_rect().height/2))

    def setKickDirection(self,playerX,playerY):
        xMove = (playerX-self.ballX)/10
        yMove = (playerY-self.ballY)/10
        normMove = 1/math.sqrt(xMove**2+yMove**2)
        self.ballXDirection = xMove*normMove
        self.ballYDirection = yMove*normMove

    def kickBall(self,speed):
        self.ballX -= speed*self.ballXDirection
        self.ballY -= speed*self.ballYDirection


class Player(Game):
    '''It's you. You're the star.'''
    def __init__(self,screen,screenDimensions):
        Game.__init__(self,screen,screenDimensions)
        self.player = None
        self.playerStart = self.player
        self.foot = None
        self.footStart = self.foot
        self.playerX = self.screenDimensions[0]/2
        self.playerY = 530
        self.playerXOriginal = self.playerX
        self.playerYOriginal = self.playerY
        self.footX = None
        self.footY = None
        self.currentRotation = 0
        self.radius = 80
        self.deltaTheta = int(90/(self.radius/5))
        self.font = pygame.font.Font('freesansbold.ttf',25)
        self.score = 0
        self.scoreText = self.font.render("Score: " + str(self.score),True,white)

    def shoot(self, scored=False):
        '''They shoot, they score!...Maybe.'''
        goal_font = pygame.font.SysFont('comicsans',300)
        if scored == True:
            self.score += 1
            color = blue
            shoot_message = 'HIT!'
        else:
            color = red
            shoot_message = 'MISS!'
        goal_text = goal_font.render(shoot_message, True, color)
        screen.blit(goal_text,(width/2-(goal_text.get_width()/2), height/2-(goal_text.get_height()/2)))
        pygame.display.update()
        i = 0
        while i < 100:
            pygame.time.delay(5)
            i += 1
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    i = 101
                    pygame.quit()
        
        self.scoreText = self.font.render("Score: " + str(self.score),True, white)

    def blitScore(self):
        self.screen.blit(self.scoreText,(800-self.scoreText.get_width()/2,50-self.scoreText.get_height()/2))

    def resetPlayer(self):
        '''Return player to original position behind the ball'''
        self.playerX = self.playerXOriginal
        self.playerY = self.playerYOriginal
        self.currentRotation = 0
        self.rotatePlayer(self.currentRotation)

    def loadPlayer(self,name,rescale):
        self.player = pygame.image.load(name).convert_alpha()
        playerWidth = self.player.get_rect().width
        playerHeight = self.player.get_rect().height
        self.player = pygame.transform.scale(self.player,(playerWidth*rescale,playerHeight*rescale))
        self.player = pygame.transform.rotate(self.player,90)
        self.playerStart = self.player

    def loadFoot(self,name,rescale):
        self.foot = pygame.image.load(name).convert_alpha()
        footWidth = self.foot.get_rect().width
        footHeight = self.foot.get_rect().height
        self.foot = pygame.transform.scale(self.foot,(footWidth*rescale,footHeight*rescale))
        self.foot = pygame.transform.rotate(self.foot,90)
        self.footStart = self.foot

    def rotatePlayer(self,angle):
        self.player = pygame.transform.rotate(self.playerStart,angle)

    def rotateFoot(self,angle):
        self.foot = pygame.transform.rotate(self.footStart,angle)

    def movePlayer(self,direction):
        if direction == "Left":
            self.deltaTheta *= -1

        finalRot = (self.currentRotation+self.deltaTheta)*math.pi/225
        
        Hypotenuse = (self.radius*math.sin(finalRot)/(math.sin((math.pi-finalRot)/2)))

        changeX = Hypotenuse*math.cos(math.pi/2-(math.pi-finalRot)/2)
        changeY = Hypotenuse*math.sin(math.pi/2-(math.pi-finalRot)/2)


        self.currentRotation = self.currentRotation + self.deltaTheta
        self.player = pygame.transform.rotate(self.playerStart,self.currentRotation)
        self.playerX = self.playerXOriginal + changeX
        self.playerY = self.playerYOriginal - changeY

        
        if direction == "Left": # reverts self.delta_theta, otherwise player won't rotate correctly
            self.deltaTheta *= -1 
               
    def blitPlayer(self):
        self.screen.blit(self.player,(self.playerX-self.player.get_rect().width/2,self.playerY-self.player.get_rect().height/2))
        
    def blitFoot(self):
        self.screen.blit(self.foot,(self.footX - self.foot.get_rect().width/2,self.footY - self.foot.get_rect().height/2))

    def playerShoot(self,ballX,ballY):
        xMove = (self.playerX-ballX)/10
        yMove = (self.playerY-ballY)/10
        self.playerX -= xMove
        self.playerY -= yMove

    def positionFoot(self,ballX,ballY):
        xMove = (self.playerX-ballX)/10
        yMove = (self.playerY-ballY)/10
        normMove = 1/math.sqrt(xMove**2+yMove**2)
        distanceToShoulder = 20
        shoulderAngle = self.currentRotation*math.pi/180

        self.footX = (self.playerX+distanceToShoulder*math.cos(shoulderAngle)-20*xMove*normMove)
        self.footY = (self.playerY-distanceToShoulder*math.sin(shoulderAngle)-20*yMove*normMove)
        self.foot = pygame.transform.rotate(self.footStart,self.currentRotation)

class Target(Game):
    '''You don't have to hit it dead center, but you do have to hit it.'''
    def __init__(self,screen,screenDimensions,start,goalHeight,goalEnd):
        Game.__init__(self,screen,screenDimensions)
        self.targetX = start
        self.targetY = goalHeight
        self.target = None
        self.xDirection = 1
        self.goalEnd = goalEnd
        self.start = start

    def loadTarget(self,name):
        self.target = pygame.image.load(name).convert_alpha()
        self.target = pygame.transform.scale(self.target,(50,50))
        self.targetWidth = self.target.get_rect().width
        self.targetHeight = self.target.get_rect().height

    def blitTarget(self):
        self.screen.blit(self.target,(self.targetX,self.targetY-self.targetHeight/2))

    def moveTarget(self,speed):
        self.targetX += self.xDirection*speed
        if self.targetX + self.targetWidth >= self.goalEnd - 10:
            self.xDirection = -1
        elif self.targetX <= self.start + 10:
            self.xDirection = 1

    def checkTargetHit(self,ballXLeft,ballWidth,ballYTop,ballHeight):
        ballBoxX = (ballXLeft,ballXLeft+ballWidth)
        ballBoxY = (ballYTop,ballYTop+ballHeight)
        targetBoxX = (self.targetX,self.targetX+self.targetWidth)
        targetBoxY = (self.targetY-self.targetHeight/2,self.targetY+self.targetHeight/2)

        if ballBoxX[0]>=targetBoxX[0] and ballBoxX[0]<=targetBoxX[1]:
            if ballBoxY[0]>=targetBoxY[0] and ballBoxY[0]<=targetBoxY[1]:
                return True
            elif ballBoxY[1]>=targetBoxY[0] and ballBoxY[1]<=targetBoxY[1]:
                return True
        elif ballBoxX[1]>=targetBoxX[0] and ballBoxX[1]<=targetBoxX[1]:
            if ballBoxY[0]>=targetBoxY[0] and ballBoxY[0]<=targetBoxY[1]:
                return True
            elif ballBoxY[1]>=targetBoxY[0] and ballBoxY[1]<=targetBoxY[1]:
                return True
        return False
            

def updateFrameImages(showFoot = False):
    '''reload the screen so it's nice and pretty'''
    global background,newPlayer,newBall
    background.blitBackground()
    newPlayer.blitScore()
    if showFoot:
        newPlayer.blitFoot()
    target.blitTarget()    
    newPlayer.blitPlayer()
    newBall.blitBall()

def text_objects(text,font,color,bg=False):
    textSurface = font.render(text, True, color,bg)
    return textSurface, textSurface.get_rect()

def game_intro():
    '''Main menu'''
    intro = True

    while intro:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        screen.fill(white)
        grass = pygame.image.load('grass.jpg')
        grass = pygame.transform.scale(grass,(screenDim))
        screen.blit(grass,(0,0))
        backimg = pygame.image.load("socc_player.png").convert_alpha()
        backimg = pygame.transform.scale(backimg, (438,225))
        screen.blit(backimg,(25,15))
        
        TextSurf1, TextRect1 = text_objects(" Crack Shot Soccer ", largeText, blue, white)
        TextSurf2, TextRect2 = text_objects(" [press ENTER to play] ", medSmallText, blue, white)
        TextSurf3, TextRect3 = text_objects(" [press C for controls] ", medSmallText, blue, white)
        
        TextRect1.center = ((width/2),((height/2)-40))
        TextRect2.center = ((width/2), ((height/2)+75))
        TextRect3.center = ((width/2), ((height/2)+125))
        
        screen.blit(TextSurf1, TextRect1)
        screen.blit(TextSurf2, TextRect2)
        screen.blit(TextSurf3, TextRect3)
        
        pygame.display.update()

        pressedKeys = pygame.key.get_pressed()
        if pressedKeys[pygame.K_RETURN]:
            intro = False
        elif pressedKeys[pygame.K_c]:
            game_controls()

def game_controls():
    '''control menu'''
    controls = True
    while controls:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        grass = pygame.image.load('grass.jpg')
        grass = pygame.transform.scale(grass,(screenDim))
        screen.blit(grass,(0,0))

        backimg = pygame.image.load("socc_player.png").convert_alpha()
        backimg = pygame.transform.scale(backimg, (438,225))
        screen.blit(backimg,((width/2),460))

        TextSurf1, TextRect1 = text_objects(" the game is simple: kick the ball and hit and the target ", medSmallText, blue, white)
        TextSurf2, TextRect2 = text_objects(" you get 10 shots, make them count! ", medSmallText, blue, white)
        TextSurf3, TextRect3 = text_objects(" use the LEFT and RIGHT arrow keys to move the player ", smallText,blue, white)
        TextSurf4, TextRect4 = text_objects(" press the SPACE bar to kick the ball; it will automatically reset ", smallText, blue, white)
        TextSurf5, TextRect5 = text_objects(" [press TAB to return to home screen] ", medSmallText, blue, white)

        TextRect1.center = ((width/2),((125)))
        TextRect2.center = ((width/2), ((175)))
        TextRect3.center = ((width/2), ((255)))
        TextRect4.center = ((width/2), ((300)))
        TextRect5.center = ((width/2),((415)))

        screen.blit(TextSurf1, TextRect1)
        screen.blit(TextSurf2, TextRect2)
        screen.blit(TextSurf3, TextRect3)
        screen.blit(TextSurf4, TextRect4)
        screen.blit(TextSurf5, TextRect5)

        pressedKeys = pygame.key.get_pressed()
        pygame.display.update()
        if pressedKeys[pygame.K_TAB]:
            controls = False

def end_of_practice(score):
    '''Practice is over. How'd you do?'''

    TextSurf1, TextRect1 = text_objects(" That's it! ", largeText, blue, white)
    TextSurf2, TextRect2 = text_objects(f" You scored {score} out of 10! ", medText, blue, white)
    TextSurf3, TextRect3 = text_objects(f" ...returning to main menu... ", smallText, blue, white)

    TextRect1.center = ((width/2),((height/2)-40))
    TextRect2.center = ((width/2), ((height/2)+75))
    TextRect3.center = ((width/2), ((height/2)+160))

    screen.blit(TextSurf1, TextRect1)
    screen.blit(TextSurf2, TextRect2)
    screen.blit(TextSurf3, TextRect3)

    pygame.display.update()

    i = 0
    while i < 100:
        pygame.time.delay(50)
        i += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                i = 101
                pygame.quit()

    game_intro()


# main loop
game_intro()
game = Game(screen,screenDim)
newPlayer = Player(screen,screenDim)
newBall = Ball(screen,screenDim)
background = Background(screen,screenDim)
background.loadGrass("grass.jpg")
rescale = 3
newPlayer.loadPlayer("characterBody.png",rescale)
newPlayer.loadFoot("characterFoot.png",rescale)
rescaleBall = 2
newBall.loadBall("ball.png",rescaleBall)
background.loadGoalLeft("goalLeft.png")
goalHeight = background.goalLeft.get_rect().height
background.loadGoalMiddle("goalMiddle.png")
background.loadGoalRight("goalRight.png")
background.setStart()
goalEnd = (background.goalStart+background.goalLeft.get_rect().width+background.goalMiddle.get_rect().width+background.goalRight.get_rect().width)
target = Target(screen,screenDim,background.goalStart,goalHeight,goalEnd)
target.loadTarget("target.png")
background.blitBackground()
newPlayer.blitScore()
target.blitTarget()
newPlayer.blitPlayer()
newBall.blitBall()

finished = False
hitTarget = False
score = 0
shots = 0
while finished == False:

    if shots < 10:
        finished = False
    if shots == 10:
        finished = True
        end_of_practice(score)

    for event in pygame.event.get(): 
        if event.type == pygame.QUIT:
            finished = True
            pygame.quit()
            sys.exit()

    pressedKeys = pygame.key.get_pressed()
    if pressedKeys[pygame.K_LEFT] == 1:
        if newPlayer.currentRotation > -90:
            newPlayer.movePlayer("Left")
    elif pressedKeys[pygame.K_RIGHT] == 1:
        if newPlayer.currentRotation < 90:
            newPlayer.movePlayer("Right")
    elif pressedKeys[pygame.K_SPACE] == 1:
        for i in range(3):
            target.moveTarget(5)
            newPlayer.playerShoot(newBall.ballX,newBall.ballY)
            updateFrameImages()
            game.updateFrame()

        newPlayer.positionFoot(newBall.ballX,newBall.ballY)
        updateFrameImages(True)
        game.updateFrame()

        newBall.setKickDirection(newPlayer.playerX,newPlayer.playerY)
        speed = 30
        while newBall.ballY >= goalHeight:
            target.moveTarget(5)
            newBall.kickBall(speed)

            ballWidth = newBall.ball.get_rect().width
            ballXLeft = newBall.ballX - ballWidth/2

            ballHeight = newBall.ball.get_rect().height
            ballYTop = newBall.ballY - ballHeight/2
            
            hitTarget = target.checkTargetHit(ballXLeft,ballWidth,ballYTop,ballHeight)
            updateFrameImages()
            game.updateFrame()

        if hitTarget:
            score += 1
            shots += 1
            newPlayer.shoot(True)
            game.updateFrame()
        else:
            shots += 1
            newPlayer.shoot(False)
            game.updateFrame()
            
        newPlayer.resetPlayer()
        newBall.resetBall()
        sleep(1)

    target.moveTarget(5)   
    updateFrameImages()
    game.updateFrame()
