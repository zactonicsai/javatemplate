import React, { useState, useEffect, useCallback, useRef } from 'react';

const INACTIVITY_TIMEOUT_SECONDS = 5 * 60; // 5 minutes

const InactivityTimer = () => {
  // State for the remaining time in seconds
  const [timeLeft, setTimeLeft] = useState(INACTIVITY_TIMEOUT_SECONDS);
  // State to track if the countdown is currently active
  const [isCountingDown, setIsCountingDown] = useState(false);
  // Ref to hold the ID of the timer that tracks inactivity (the initial 5 min wait)
  const inactivityTimerRef = useRef(null);
  // Ref to hold the ID of the countdown interval (the 5 min -> 0 countdown)
  const countdownIntervalRef = useRef(null);

  // --- Utility Functions for Time Management ---

  const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    const pad = (num) => String(num).padStart(2, '0');
    return `${pad(minutes)}:${pad(remainingSeconds)}`;
  };

  const resetTimer = useCallback(() => {
    // 1. Clear the countdown interval if it's running
    if (countdownIntervalRef.current) {
      clearInterval(countdownIntervalRef.current);
      countdownIntervalRef.current = null;
    }

    // 2. Stop the countdown state
    setIsCountingDown(false);

    // 3. Reset the time left display to the full timeout
    setTimeLeft(INACTIVITY_TIMEOUT_SECONDS);

    // 4. Clear the existing inactivity timer (to prevent it from triggering)
    if (inactivityTimerRef.current) {
      clearTimeout(inactivityTimerRef.current);
    }

    // 5. Start a new inactivity timer: after this time, the countdown will start
    inactivityTimerRef.current = setTimeout(() => {
      setIsCountingDown(true);
    }, 5); // Wait 5 minutes before starting the countdown

  }, []);

  // --- Main Effects ---

  // 1. Setup/Cleanup for the Inactivity Detector
  useEffect(() => {
    // List of events to listen for user activity
    const activityEvents = [
      'mousemove', 'mousedown', 'keydown', 'scroll', 'touchstart'
    ];

    // Reset the timer on any user activity
    activityEvents.forEach(event => {
      window.addEventListener(event, resetTimer);
    });

    // Initial call to start the first inactivity timer
    resetTimer();

    // Cleanup function for the effect
    return () => {
      // Clear all timers
      clearTimeout(inactivityTimerRef.current);
      if (countdownIntervalRef.current) {
        clearInterval(countdownIntervalRef.current);
      }
      
      // Remove all event listeners
      activityEvents.forEach(event => {
        window.removeEventListener(event, resetTimer);
      });
    };
  }, [resetTimer]); // Dependency array includes resetTimer

  // 2. Countdown Effect
  useEffect(() => {
    if (isCountingDown) {
      // Start the countdown interval (runs every second)
      countdownIntervalRef.current = setInterval(() => {
        setTimeLeft((prevTime) => {
          if (prevTime <= 1) {
            // Timer finished! You can add an action here, like logging out.
            clearInterval(countdownIntervalRef.current);
            countdownIntervalRef.current = null;
            console.log("Inactivity timer reached zero. Taking action...");
            // Optional: Call a function like logoutUser() here
            return 0;
          }
          return prevTime - 1;
        });
      }, 1000); // Interval runs every 1000ms (1 second)
    } else {
      // Clear the interval if the countdown is stopped
      if (countdownIntervalRef.current) {
        clearInterval(countdownIntervalRef.current);
        countdownIntervalRef.current = null;
      }
    }

    // Cleanup for the interval when the component unmounts or state changes
    return () => {
      if (countdownIntervalRef.current) {
        clearInterval(countdownIntervalRef.current);
      }
    };
  }, [isCountingDown]); // Dependency array includes isCountingDown

  // --- Render ---

  return (
    <div style={{ padding: '20px', border: '1px solid #ccc', borderRadius: '8px' }}>
      <h3>Inactivity Timer</h3>
      <p>
        **Status:** {isCountingDown ? '**Counting Down**' : 'Waiting for Inactivity'}
      </p>
      <p style={{ fontSize: '24px', fontWeight: 'bold', color: isCountingDown ? 'red' : 'green' }}>
        **Time Left:** {formatTime(timeLeft)}
      </p>
      <p style={{ fontSize: '12px', color: '#666' }}>
        *The timer will start counting down from 5:00 **after** 5 minutes of no activity.*
      </p>
    </div>
  );
};

export default InactivityTimer;