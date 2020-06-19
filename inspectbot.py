import RPi.GPIO as GPIO # For controlling the raspberry pi's GPIO pins
import datetime # For testing time passed in time_check(). Necessary for dead man switch
from time import sleep # Necessary for LED_flash and testing time_check() and by extension, dead_man()

def gpio_setup_outputs(pins):
	#Sets the GPIO pins in a list to outputs
	for pin in pins:
		GPIO.setup(pin, GPIO.OUT)
	return;

def time_check(last_time):
	# Time check will be used to test if a specified amount of time has passed
	# since the last pilot input was recieved.
	time_passed = datetime.datetime.now() - last_time # finding the difference between the last time and time now
	print("Time Passed = " + str(time_passed)) # Printing the amount of time that passed. (debug)
	if (time_passed > datetime.timedelta(seconds=3)): # If the time passed is greater than 3 seconds
		return(True)
	else: # if the time passed is not greater than 3 seconds
		return(False)

def dead_man(last_time, l_motor_pins, r_motor_pins):
    # Dead man switch stops motors if not pilot input recieved for 3 seconds
	if not time_check(last_time): # If time_check() returns false
		print("Dead man: Continue movement")	# Test statement
		return(False) # Do nothing
	else: # If time_check() returns True
		print("Dead man: Stop motors") # Test statement
		motors_stop(l_motor_pins, r_motor_pins) # Stop both motors
		return(True)

def test_functions(Robot):
	print("TEST FUNCTIONS")
	Robot.motor_forward(Robot.left_motor)
	Robot.motor_reverse(Robot.right_motor)
	sleep(1)
	Robot.motor_forward(Robot.right_motor)
	Robot.motor_reverse(Robot.left_motor)
	sleep(1)
	Robot.motor_forward(Robot.left_motor)
	Robot.motor_forward(Robot.right_motor)
	sleep(1)
	Robot.motor_reverse(Robot.left_motor)
	Robot.motor_reverse(Robot.right_motor)
	sleep(1)
	Robot.motors_stop
	sleep(.500)
	Robot.motor_forward(Robot.left_motor)
	Robot.motor_reverse(Robot.right_motor)
	Robot.LED_flash(Robot.LEDs[0])
	return(1)

def pilot_control(input, Robot):
	if input == 10:
		Robot.motors_stop()
	elif input == curses.KEY_UP:
		Robot.motor_forward(Robot.left_motor)
		Robot.motor_forward(Robot.right_motor)
	elif input == curses.KEY_DOWN:
		Robot.motor_reverse(Robot.left_motor)
		Robot.motor_reverse(Robot.right_motor)
	elif input == curses.KEY_RIGHT:
		Robot.motor_forward(Robot.left_motor)
		Robot.motor_reverse(Robot.right_motor)
	elif input == curses.KEY_LEFT:
		Robot.motor_forward(Robot.right_motor)
		Robot.motor_reverse(Robot.left_motor)
	return()


class Robot:

	left_motor_speed = 0
	right_motor_speed = 0

	#Contructor
	def __init__(self, left_motor, right_motor, LEDs):
		self.left_motor = left_motor
		self.right_motor = right_motor
		self.LEDs = LEDs

	def LED_on(self, pin):
		# Turns on a specified LED
		#pin is the number of the GPIO pin to be turned on
		GPIO.output(pin, True)
		print("LED on")

	def LED_off(self, pin):
		# Turns off a specified LED
		#pin is the number of the GPIO pin to be turned off
		GPIO.output(pin, False)
		print("LED off")

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
		return motor_speed


#main code execution
try:
	inspectbot = Robot([4, 17], [27, 22], [23]) # initializing a Robot object

	# Testing if Robot object was properly created
	print(inspectbot.left_motor) # printing the left_motor pin numbers
	print(inspectbot.right_motor) # printing the right_motor pin numbers
	print(inspectbot.LEDs) # printing the LEDs pin numbers

	# Setting up the GPIO pins
	GPIO.setmode(GPIO.BCM) # Set the pin reference mode
	gpio_setup_outputs(inspectbot.left_motor) # Set up the left motor pins
	gpio_setup_outputs(inspectbot.right_motor) # Set up the right motor pins
	inspectbot.motors_stop() # Stops both motors
	gpio_setup_outputs(inspectbot.LEDs) # Set up the LED GPIO pins

	# Setting up curses to recieve pilot input
	#screen = curses.initscr()
	#curses.noecho()
	#curses.cbreak()
	#screen.keypad(True)


	"""
	# While loop listens for pilot input 
	while True:
		input = screen.getch()
		if input == ord('q'):
			break
		else:
			pilot_control(input, left_motor, right_motor)
	"""


	test_functions(inspectbot)
	print("Code works") # Only prints if all code runs

finally:
	#curses.nocbreak(); screen.keypad(0); curses.echo()
	#curses.endwin()

	inspectbot.motors_stop() # Stops motors once code is completed
	inspectbot.LED_off(inspectbot.LEDs) # Turns off all LEDs once code is completed
	GPIO.cleanup() # Cleans up GPIO after code is completed
	print("Code Finished") # Prints once execution is complete
