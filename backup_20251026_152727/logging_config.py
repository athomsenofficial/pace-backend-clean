import logging
import os
from datetime import datetime
from pathlib import Path

# Create logs directory if it doesn't exist
LOGS_DIR = Path(__file__).parent / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

# Log file paths for general logging
UPLOAD_LOG_FILE = LOGS_DIR / 'uploads.log'
GENERAL_LOG_FILE = LOGS_DIR / 'general.log'


class LoggerSetup:
    """Centralized logger setup for the application"""

    _loggers = {}
    _session_loggers = {}

    @classmethod
    def get_logger(cls, name: str, log_file: str = None, level=logging.INFO):
        """
        Get or create a logger with the specified name and configuration.

        Args:
            name: Logger name (typically __name__ of the module)
            log_file: Path to log file. If None, uses general.log
            level: Logging level (default: INFO)

        Returns:
            Configured logger instance
        """
        if name in cls._loggers:
            return cls._loggers[name]

        logger = logging.getLogger(name)
        logger.setLevel(level)

        # Prevent duplicate handlers
        if logger.handlers:
            return logger

        # Use general log file if none specified
        if log_file is None:
            log_file = GENERAL_LOG_FILE

        # Create file handler with detailed formatting
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)

        # Create console handler for errors
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.ERROR)

        # Detailed formatter with timestamp, logger name, level, and message
        detailed_formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        file_handler.setFormatter(detailed_formatter)
        console_handler.setFormatter(detailed_formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        cls._loggers[name] = logger
        return logger

    @classmethod
    def get_session_logger(cls, session_id: str, cycle: str, year: int, level=logging.INFO):
        """
        Get or create a session-specific logger.

        Args:
            session_id: Unique session identifier
            cycle: Promotion cycle (e.g., 'SRA', 'SSG')
            year: Promotion year
            level: Logging level (default: INFO)

        Returns:
            Configured logger instance for this session
        """
        logger_key = f"session_{session_id}"

        if logger_key in cls._session_loggers:
            return cls._session_loggers[logger_key]

        # Create session-specific log filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_filename = f"{cycle}_{year}_{timestamp}_{session_id[:8]}.log"
        log_file = LOGS_DIR / log_filename

        # Create a new logger instance for this session
        logger = logging.getLogger(logger_key)
        logger.setLevel(level)
        # Prevent propagation to avoid duplicate logs
        logger.propagate = False

        # Create file handler with detailed formatting
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)

        # Detailed formatter with timestamp and message (no logger name needed for session logs)
        detailed_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)

        cls._session_loggers[logger_key] = logger

        # Log the session start info
        logger.info("=" * 80)
        logger.info(f"ROSTER PROCESSING LOG - {cycle} {year}")
        logger.info(f"Session ID: {session_id}")
        logger.info(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Log File: {log_filename}")
        logger.info("=" * 80)
        logger.info("")

        return logger

    @classmethod
    def close_session_logger(cls, session_id: str):
        """
        Close and remove a session-specific logger.

        Args:
            session_id: Session identifier
        """
        logger_key = f"session_{session_id}"

        if logger_key in cls._session_loggers:
            logger = cls._session_loggers[logger_key]

            # Log session end
            logger.info("")
            logger.info("=" * 80)
            logger.info(f"SESSION COMPLETED")
            logger.info(f"Ended: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("=" * 80)

            # Close all handlers
            for handler in logger.handlers[:]:
                handler.close()
                logger.removeHandler(handler)

            # Remove from cache
            del cls._session_loggers[logger_key]


def log_session_start(logger, session_id: str, event_type: str):
    """Log the start of a session processing event"""
    logger.info("=" * 80)
    logger.info(f"SESSION START: {event_type}")
    logger.info(f"Session ID: {session_id}")
    logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80)


def log_session_end(logger, session_id: str, event_type: str, status: str = "SUCCESS"):
    """Log the end of a session processing event"""
    logger.info("-" * 80)
    logger.info(f"SESSION END: {event_type}")
    logger.info(f"Session ID: {session_id}")
    logger.info(f"Status: {status}")
    logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80)
    logger.info("")  # Add blank line for readability


def log_member_processing(logger, member_name: str, ssan: str, step: str, details: str = None):
    """Log individual member processing steps"""
    msg = f"Member: {member_name} (SSAN: {ssan}) | Step: {step}"
    if details:
        msg += f" | {details}"
    logger.info(msg)


def log_board_filter_decision(logger, member_name: str, ssan: str, eligible: bool,
                               reason: str = None, is_btz: bool = False):
    """Log board filter eligibility decision"""
    status = "ELIGIBLE" if eligible else "INELIGIBLE"
    if is_btz:
        status = "ELIGIBLE (BTZ)"

    msg = f"DECISION: {member_name} (SSAN: {ssan}) | {status}"
    if reason:
        msg += f" | Reason: {reason}"

    if eligible:
        logger.info(msg)
    else:
        logger.warning(msg)


# Initialize default loggers (for general use only)
upload_logger = LoggerSetup.get_logger('upload', str(UPLOAD_LOG_FILE))
general_logger = LoggerSetup.get_logger('general', str(GENERAL_LOG_FILE))

# Note: board_filter logging is now handled per-session via LoggerSetup.get_session_logger()
