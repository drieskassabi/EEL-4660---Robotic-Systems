#include <msp430fr5994.h>
#include <stdio.h>


/**
 * main.c
 */
int main(void) {

    // Watchdog and FRAM configuration
    PM5CTL0 &= ~LOCKLPM5;
	WDTCTL = WDTPW | WDTHOLD;

	// setting up clock system
	CSCTL0_H = CSKEY>>8; // CSKey=A500. Unlock clock registers
	CSCTL1 = DCOFSEL_0 | DCORSEL; // set DCO to 1 MHZ
	CSCTL2 = SELS__DCOCLK; // assign DCO to SCLK
	CSCTL3 = DIVS__8; // Divide SCLK by 8
	CSCTL0_H = 0; // Lock CS registers


	// set up pins to read input from Pi
	P3DIR &=~BIT0; // P3.0 reads command to move down
	P3SEL0&=~BIT0; // activates motor when it receives 1

	P3DIR &=~BIT1; // P3.1 reads command to move up
	P3SEL0&=~BIT1; // activates motor when it receives 1

    P3DIR &=~BIT2; // P3.2 reads command to move left
    P3SEL0&=~BIT2; // activates motor when it receives 1

    P3DIR &=~BIT3; // P3.3 reads command to move right
    P3SEL0&=~BIT3; // activates motor when it receives 1

	// set up pins for motor PWM
	P1DIR |= BIT2; // set p1.2 as output
	P1SEL0 |= BIT2; // set p1.2 to timer1_A
	P1DIR |= BIT4; // set p1.4 as output
	P1SEL0 |= BIT4; // set p1.4 to timerB0


	// set up timer for motor 1
	TA1CCTL1 |= OUTMOD_7; // set/reset for PWM
	TA1CCR0 = 2713; // set 20ms pause between pulses
	TA1CCR1 = 188; // initialize to 1.5 ms pulse
	TA1CTL |= TASSEL_2 + MC_1; // use smclk and up mode

	// set up timer for motor 2
	TB0CCTL1 |= OUTMOD_7; // set/reset for PWM
	TB0CCR0 = 2713; // set 20ms pause between pulses
	TB0CCR1 = 188; // initialize to 1.5 ms pulse
	TB0CTL |= TBSSEL_2 +MC_1; // use smclk and up mode


	// infinite loop
	for(;;){

	    // Pitch Motor Control

	    if((P3IN & BIT0) == BIT0) // if receiving command to move down
	        TA1CCR1 = 187; // change PWM pulse to move down
	    else if((P3IN & BIT1) == BIT1) // if receiving command to move up
	        TA1CCR1 = 189; // change PWM pulse to move up
	    else // if no Pitch commands
	        TA1CCR1 = 188; // change PWM for no movement

	    // Yaw Motor Control

	    if((P3IN & BIT2) == BIT2) // if receiving command to move left
	        TB0CCR1 = 187; // change PWM pulse to move left
        else if((P3IN & BIT3) == BIT3) // if receiving command to move right
            TB0CCR1 = 189; // change PWM pulse to move right
        else // if no Yaw commands
            TB0CCR1 = 188; // change PWM for no movement
	}





}

