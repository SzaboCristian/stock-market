import os
import unittest

from util.logger.logger import Logger


class TestLogger(unittest.TestCase):

    def setUp(self) -> None:
        """
        Setup logger.
        @return: None
        """
        self.test_logger_name = 'test_logger'
        self.test_logger_filename = 'test.log'
        Logger.get_logger(logger_name=self.test_logger_name, file_name=self.test_logger_filename)
        Logger.set_file_logging(self.test_logger_filename)

    def tearDown(self) -> None:
        """
        Delete test log file.
        @return: None
        """
        Logger.close_log_file()
        if os.path.isfile(os.path.join(Logger.LOG_DIR, self.test_logger_filename)):
            os.remove(os.path.join(Logger.LOG_DIR, self.test_logger_filename))

    def test_ensure_log_directory(self) -> None:
        """
        Test default log directory.
        @return: None
        """
        Logger.ensure_log_directory()
        self.assertTrue(os.path.isdir(Logger.LOG_DIR))

    def test_get_logger(self) -> None:
        """
        Test logger and logger instances. Ensure log file exists.
        @return: None
        """

        test_logger = Logger.get_logger(logger_name=self.test_logger_name, file_name=self.test_logger_filename)
        self.assertIn(self.test_logger_name, Logger.LOGGER_INSTANCES)

        same_logger = Logger.get_logger(logger_name=self.test_logger_name, file_name=self.test_logger_filename)
        self.assertEqual(id(test_logger), id(same_logger))

        Logger.ensure_log_directory()
        self.assertTrue(os.path.isdir(Logger.LOG_DIR))

        log_file_fullpath = os.path.join(Logger.LOG_DIR, self.test_logger_filename)
        self.assertTrue(os.path.isfile(log_file_fullpath))

    def test_logger_info(self) -> None:
        """
        Test log INFO.
        @return: None
        """
        Logger.info('TEST LOG 1')
        with open(os.path.join(Logger.LOG_DIR, self.test_logger_filename), 'r') as f:
            log_data = ''.join(f.readlines())
            self.assertIn('INFO', log_data)
            self.assertIn('TEST LOG 1', log_data)

    def test_logger_warning(self) -> None:
        """
        Test log WARNING.
        @return: None
        """
        Logger.warning('TEST LOG 2')
        with open(os.path.join(Logger.LOG_DIR, self.test_logger_filename), 'r') as f:
            log_data = ''.join(f.readlines())
            self.assertIn('WARNING', log_data)
            self.assertIn('TEST LOG 2', log_data)

    def test_logger_error(self) -> None:
        """
        Test log ERROR.
        @return: None
        """

        Logger.error('TEST LOG 3')
        with open(os.path.join(Logger.LOG_DIR, self.test_logger_filename), 'r') as f:
            log_data = ''.join(f.readlines())
            self.assertIn('ERROR', log_data)
            self.assertIn('TEST LOG 3', log_data)

    def test_logger_exception(self) -> None:
        """
        Test log exception.
        @return: None
        """
        try:
            _ = open(None, 'r')
        except:
            Logger.exception('TEST LOG 4')

        with open(os.path.join(Logger.LOG_DIR, self.test_logger_filename), 'r') as f:
            log_data = ''.join(f.readlines())
            self.assertIn('ERROR', log_data)
            self.assertIn('TEST LOG 4', log_data)
