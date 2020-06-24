import RPi.GPIO as GPIO # For controlling the raspberry pi's GPIO pins
import datetime # For testing time passed in time_check(). Necessary for dead man switch
import curses # Used to receive input from the controller keyboard
from time import sleep # Necessary for LED_flash and testing time_check() and by extension, dead_man()
import threading # Used to allow pseudo parallelization of main thread and deadThread

exitFlag = 0 # Flag used to exit deadThread
lastPilotInput = datetime.datetime.now() # Global variable used to keep track of the time at which the last pilot input was received

def gpio_setup_outputs(pins):
	#Sets the GPIO pins in a list to outputs
	for pin in pins:
		GPIO.setup(pin, GPIO.OUT)

def dead_man(Robot):
    # Dead man switch stops motors if not pilot input recieved for 3 seconds
	while exitFlag == 0:
		if ((datetime.datetime.now() - lastPilotInput) > datetime.timedelta(seconds=2)): # If it has been longer than 3 seconds since last pilot input
			print("Dead man")
			#Robot.motors_stop()	# Stop motors
			sleep(0.500) # Sleep thread for half a second
		else: # If it has not been more than 3 seconds since the last pilot input
			print("Alive man") # lol
			sleep(0.500) # Sleep thread for half a second
	print("Exiting dead_man")

def dead_man():
	while exitFlag == 0:
		if ((datetime.datetime.now() - lastPilotInput) > datetime.timedelta(seconds=3)):
			print "STOP MOTORS"
			sleep(0.500)
			print(datetime.datetime.now() - lastPilotInput)
		else:
			print("Do nothing")
			sleep(0.500)

def test_functions(Robot):
	# Function used for testing feature of the robot
	
	global exitFlag
	global lastPilotInput

	print("TEST FUNCTIONS")
	Robot.motor_forward(Robot.left_motor)
	Robot.motor_reverse(Robot.right_motor)
	sleep(2)
	Robot.motor_forward(Robot.right_motor)
	Robot.motor_reverse(Robot.left_motor)
	sleep(1)
	print("new input")
	lastPilotInput = datetime.datetime.now()
	Robot.motor_forward(Robot.left_motor)
	Robot.motor_forward(Robot.right_motor)
	sleep(1)
	Robot.motor_reverse(Robot.left_motor)
	Robot.motor_reverse(Robot.right_motor)
	sleep(1)
	Robot.motors_stop
	print("LEFT SPEED: " + str(Robot.left_motor_speed))
	print("RIGHT SPEED: " + str(Robot.right_motor_speed))
	Robot.motor_forward(Robot.left_motor)
	Robot.motor_reverse(Robot.right_motor)
	Robot.LED_flash(Robot.LEDs[0])
	exitFlag  = 1
	return(1)

def curses_start():
	# Sets up curses to allow keyboard to be used as input
	screen = curses.initscr()
	curses.noecho()
	curses.cbreak()
	screen.keypad(True)
	return(screen)

def curses_stop(screen):
	# Sets the terminal back to its original state
	curses.nocbreak(); screen.keypad(0); curses.echo()
	curses.endwin()
	print("Curses stopped")

def listen_for_input(Robot, screen):
	global exitFlag # Allows the global variable exitFlag to be manipulated
	while True:
		input = screen.getch()
		if input == ord('q'): # If pilot input is q, break while loop
			exitFlag = 1 # Informs the deadThread to stop
			break # Breaks the while loop
		else: # If not q, check if input matches one of the conditions in Robot.pilot_control
			Robot.pilot_control(input) # Checks what to do with the received input
	exitFlag = 1 # Just in case
	print("Input finished")

class Robot:

	left_motor_speed = 0
	right_motor_speed = 0

	#Contructor
	def __init__(self, left_motor, right_motor, LEDs):
        #First pin in motor is forward pin.
        #Second pin in motor is reverse pin
		self.left_motor = left_motor
		self.right_motor = right_motor
		self.LEDs = LEDs
        self.motors_stop()

	#Deconstructor

	def __del__(self):
		print("Destructor called")
		self.motors_stop()
		self.LED_off(self.LEDs)

	def LED_on(self, pin):
		# Turns on a specified LED
		#pin is the number of the GPIO pin to be turned on
		GPIO.output(pin, True)
		print("LED " + str(pin) + " on")

	def LED_off(self, pin):
		# Turns off a specified LED
		#pin is the number of the GPIO pin to be turned off
		GPIO.output(pin, False)
		print("LED " + str(pin) + " off")

	def LED_flash(self, pin):
		# Flashes a specified LED
		#pin is the number of the GPIO pin to be flashed
		for i in range(0, 2):
			self.LED_on(pin)
			sleep(.500)
			self.LED_off(pin)
			sleep(.500)

	def motors_stop(self):
		#Stop both motors regardless of direction
		for pin in self.left_motor: #Stopping left motor
			GPIO.output(pin, False)
		for pin in self.right_motor: #Stopping right motor
			GPIO.output(pin, False)
		print("Stop motors")

	def motor_forward(self, motor_pins):
		# Sets specified motor to move forward
		GPIO.output(motor_pins[1], False) # Ensures the motor isn't also trying to reverse
		GPIO.output(motor_pins[0], True) # Sets the motor to move forward
		print("motor_forward, pin: " + str(motor_pins[0]))

	def motor_reverse(self, motor_pins):
		# Sets specified motor to reverse
		GPIO.output(motor_pins[0], False) # Ensures the motor isn't also trying to move forward
		GPIO.output(motor_pins[1], True) # Sets the motor to reverse
		print("motor_reverse, pin: " + str(motor_pins[1]))

	def motor_set_speed(self, motor_pin, speed):
	 	motor_speed = (GPIO.PWM(motor_pin, speed))
		print("Speed set")
		return motor_speed

	def motor_PWM_start(self, motor_speed):
		print("PWM started")
		print("Motor speed: " + str(motor_speed))
		motor_speed.start()

	def pilot_control(self, input):
		if input == 10: # Robot Stops
			self.motors_stop()
			self.set_last_pilot_input()
		elif input == curses.KEY_UP: # Robot Moves Forward
			self.motor_forward(self.left_motor)
			self.motor_forward(self.right_motor)
			self.set_last_pilot_input()
		elif input == curses.KEY_DOWN: # Robot Moves Backwards
			self.motor_reverse(self.left_motor)
			self.motor_reverse(self.right_motor)
			self.set_last_pilot_input()
		elif input == curses.KEY_RIGHT: # Robot rotates right
			self.motor_forward(self.left_motor)
			self.motor_reverse(self.right_motor)
			self.set_last_pilot_input()
		elif input == curses.KEY_LEFT: # Robot rotates left
			self.motor_forward(self.right_motor)
			self.motor_reverse(self.left_motor)
			self.set_last_pilot_input()
		else:
			try:
				print("Invalid input: " + str(ord(chr(input))))
				set_last_pilot_input() # Improper input is still input
			except:
				print("Invalid input")
				set_last_pilot_input() # Improper input is still input

	def set_last_pilot_input(self):
		# Sets the time the last input was received by pilot_control
		global lastPilotInput
		lastPilotInput = datetime.datetime.now()


#main code execution
if __name__ == '__main__':
	try:
		inspectbot = Robot([4, 17], [27, 22], [23]) # initializing a Robot object

		# Setting up the GPIO pins
		GPIO.setmode(GPIO.BCM) # Set the pin reference mode
		gpio_setup_outputs(inspectbot.left_motor) # Set up the left motor pins
		gpio_setup_outputs(inspectbot.right_motor) # Set up the right motor pins
		inspectbot.motors_stop() # Stops both motors
		gpio_setup_outputs(inspectbot.LEDs) # Set up the LED GPIO pins

		# PWM Set up
		#inspectbot.motor_set_speed(inspectbot.left_motor[0], 50)
		#inspectbot.motor_PWM_start(inspectbot.left_motor_speed)

		# Setting up curses to recieve pilot input
		screen = curses_start()

		# Initializing the threada for the dead man switch
		#deadThread = threading.Thread(target=dead_man, args=(inspectbot,))
		deadThread = threading.Thread(target=dead_man, args=())
		inputThread = threading.Thread(target=listen_for_input, args=(inspectbot, screen,))

		# Starting the threads
		deadThread.start()
		inputThread.start()

		#test_functions(inspectbot)

		"""
		for i in range(0, 4):
			print(i)
			sleep(1) # I believe these calls to time.sleep are what is allowing the functions to work
		lastPilotInput = datetime.datetime.now()
		for i in range(0, 3):
			print(i)
			sleep(1)
		"""

		inputThread.join()
		deadThread.join()
		print("Code works") # Only prints if all code runs

	finally:
		print
		print("Cleaning up")
		if deadThread:
			exitFlag = 1
			deadThread.join()
		if inputThread:
			inputThread.join()
		curses_stop(screen)
		del inspectbot
		GPIO.cleanup() # Cleans up GPIO after code is completed
		print("Code Finished") # Prints once execution is complete
