import RPi.GPIO as GPIO # For controlling the raspberry pi's GPIO pins
import curses # For keyboard input to control robot
import datetime # For testing time passed in time_check(). Necessary for dead man switch
from time import sleep # Necessary for LED_flash and testing time_check() and by extension, dead_man()

def gpio_setup_outputs(pins):
	#Sets the GPIO pins in a list to outputs
	for pin in pins:
		GPIO.setup(pin, GPIO.OUT)
	return;

def LED_on(pin):
	# Turns on a specified LED
	#pin is the number of the GPIO pin to be turned on
	GPIO.output(pin, True)
	print("LED on")

def LED_off(pin):
	# Turns off a specified LED
	#pin is the number of the GPIO pin to be turned off
	GPIO.output(pin, False)
	print("LED off")

def LED_flash(pin):
	# Flashes a specified LED
	#pin is the number of the GPIO pin to be flashed
	for i in range(0, 2):
		LED_on(pin)
		sleep(.500)
		LED_off(pin)
		sleep(.500)

def motors_stop(l_motor_pins, r_motor_pins):
	#Stop both motors regardless of direction
	for pin in l_motor_pins: #Stopping left motor
		GPIO.output(pin, False)
	for pin in r_motor_pins: #Stopping right motor
		GPIO.output(pin, False)
	print("Stop motors")

def motor_forward(motor_pins):
	# Sets specified motor to move forward
	GPIO.output(motor_pins[1], False) # Ensures the motor isn't also trying to reverse
	GPIO.output(motor_pins[0], True) # Sets the motor to move forward
	print("motor_forward, pin: " + str(motor_pins[0]))

def motor_reverse(motor_pins):
	# Sets specified motor to reverse
	GPIO.output(motor_pins[0], False) # Ensures the motor isn't also trying to move forward
	GPIO.output(motor_pins[1], True) # Sets the motor to reverse
	print("motor_reverse, pin: " + str(motor_pins[1]))

def motor_set_speed(motor_pins, speed):
	motor_speed = []
	for pin in motor_pins:
		motor_speed.append(GPIO.PWM(pin, speed))
	return motor_speed

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

def test_functions(l_motor_pins, r_motor_pins, LEDs):
	print("TEST FUNCTIONS")
	motor_forward(l_motor_pins)
	motor_reverse(r_motor_pins)
	sleep(1)
	motor_forward(r_motor_pins)
	motor_reverse(l_motor_pins)
	sleep(1)
	motor_forward(l_motor_pins)
	motor_forward(r_motor_pins)
	sleep(1)
	motor_reverse(l_motor_pins)
	motor_reverse(r_motor_pins)
	sleep(1)
	motors_stop(l_motor_pins, r_motor_pins)
	sleep(.500)
	last_time = datetime.datetime.now()
	motor_forward(l_motor_pins)
	motor_reverse(r_motor_pins)
	for i in range(4):
		sleep(1)
		dead = dead_man(last_time, l_motor_pins, r_motor_pins)
		if dead:
			break
	LED_flash(LEDs[0])
	return(1)

def pilot_control(input, l_motor_pins, r_motor_pins):
	if input == 10:
		motors_stop(l_motor_pins, r_motor_pins)
		time = datetime.datetime.now()
	elif input == curses.KEY_UP:
		motor_forward(l_motor_pins)
		motor_forward(r_motor_pins)
		time = datetime.datetime.now()
	elif input == curses.KEY_DOWN:
		motor_reverse(l_motor_pins)
		motor_reverse(r_motor_pins)
		time = datetime.datetime.now()
	elif input == curses.KEY_RIGHT:
		motor_forward(l_motor_pins)
		motor_reverse(r_motor_pins)
		time = datetime.datetime.now()
	elif input == curses.KEY_LEFT:
		motor_forward(r_motor_pins)
		motor_reverse(l_motor_pins)
		time = datetime.datetime.now()
	return(time)

#main code execution
try:

	left_motor = [4, 17] # List of the GPIO pins that control the left motor
	right_motor = [27, 22] # List of the GPIO pins that control the right motor
	LED_pins = [23] # List of the GPIO pins that control the LEDS

	GPIO.setmode(GPIO.BCM) # Set the pin reference mode
	gpio_setup_outputs(left_motor) # Set up the left motor pins
	gpio_setup_outputs(right_motor) # Set up the right motor pins
	motors_stop(left_motor, right_motor) # Stops both motors
	gpio_setup_outputs(LED_pins) # Set up the LED GPIO pins

	"""
	I think for now it's best to leave out the attempt at PWM
	 until I actually build the bot.
	 Based on my understanding, I think my current implementations of
	 motors_stop(), motor_forward(), and motor_reverse() don't
	 work with PWM.
	 I *think* that motor_set_speed() might cause the motors to begin moving which is not my intention yet.
	 right_motor_speed = motor_set_speed(right_motor, 100) # Setting right motor speed to 100
	 left_motor_speed = motor_set_speed(left_motor, 100) # Setting left_motor speed to 100
	 print(right_motor_speed) 
	"""


	screen = curses.initscr()
	curses.noecho()
	curses.cbreak()
	screen.keypad(True)

	last_input = datetime.datetime.now()

	while True:
		# current implementation of dead_man() will not work because screen.getch() pauses the while loop
		# This means that dead_man() only checks how much time has passed when a key has been pressed
		# dead_man print statement usually reads about 0.0001 seconds

		input = screen.getch()
		if input == ord('q'):
			break
		else:
			last_input = pilot_control(input, left_motor, right_motor)
		#dead_man(last_input, left_motor, right_motor)
	# test_functions(left_motor, right_motor, LED_pins)

	print("Code works") # Only prints if all code runs

	""" 
	TO DO
	 Add PWM speed control for motors
	 Allow two or three selectable speeds for motors
	 Purpose of this is to allow pilot finer resolution movement control 
	"""

finally:
	curses.nocbreak(); screen.keypad(0); curses.echo()
	curses.endwin()

	motors_stop(left_motor, right_motor) # Stops motors once code is completed
	LED_off(LED_pins) # Turns off all LEDs once code is completed
	GPIO.cleanup() # Cleans up GPIO after code is completed
	print("Code Finished") # Prints once execution is complete
