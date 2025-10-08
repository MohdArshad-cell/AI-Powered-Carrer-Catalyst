package com.backend.careercatalyst.exception;

public class PythonServiceException extends RuntimeException {

    /**
     * Constructor that takes a custom message.
     * @param message The detail message for the exception.
     */
    public PythonServiceException(String message) {
        super(message);
    }

    /**
     * Constructor that takes a custom message and wraps the original cause.
     * This is useful for maintaining the original stack trace.
     * @param message The detail message for the exception.
     * @param cause The original exception that was caught.
     */
    public PythonServiceException(String message, Throwable cause) {
        super(message, cause);
    }
}