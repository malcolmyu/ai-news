import { describe, it, beforeEach, afterEach, mock } from 'node:test';
import assert from 'node:assert/strict';
import { Logger } from '../../utils/config.js';
import { mockConsole } from './test-utils.js';

describe('Logger', () => {
  let logger: Logger;
  let consoleMock: ReturnType<typeof mockConsole>;

  beforeEach(() => {
    logger = new Logger('TestLogger');
    consoleMock = mockConsole();
  });

  afterEach(() => {
    consoleMock.restore();
  });

  describe('constructor', () => {
    it('should create logger instance with default prefix', () => {
      const defaultLogger = new Logger();
      assert.ok(defaultLogger);
    });

    it('should create logger instance with custom prefix', () => {
      assert.ok(logger);
    });
  });

  describe('log methods', () => {
    it('should log info messages', () => {
      const testMessage = 'Test info message';
      logger.info(testMessage);

      const infoLogs = consoleMock.logs.filter(msg => msg.includes(`INFO: ${testMessage}`));
      assert.equal(infoLogs.length, 1);
    });

    it('should log debug messages', () => {
      const testMessage = 'Test debug message';

      logger.debug(testMessage);
      assert.equal(consoleMock.logs.filter(msg => msg.includes(`DEBUG: ${testMessage}`)).length, 0);

      process.env.DEBUG = 'true';
      logger.debug(testMessage);
      const debugLogs = consoleMock.logs.filter(msg => msg.includes(`DEBUG: ${testMessage}`));
      assert.equal(debugLogs.length, 1);

      delete process.env.DEBUG;
    });

    it('should log error messages', () => {
      const testMessage = 'Test error message';
      logger.error(testMessage);

      const errorLogs = consoleMock.errors.filter(msg => msg.includes(testMessage));
      assert.equal(errorLogs.length, 1);
    });

    it('should log warning messages', () => {
      const testMessage = 'Test warning message';
      logger.warn(testMessage);

      const warningLogs = consoleMock.warnings.filter(msg => msg.includes(testMessage));
      assert.equal(warningLogs.length, 1);
    });

    it('should log error messages with Error objects', () => {
      const testMessage = 'Test error with stack';
      const testError = new Error('Test error');

      logger.error(testMessage, testError);

      const errorLogs = consoleMock.errors.join('\n');
      assert.ok(errorLogs.includes(testMessage));
      assert.ok(errorLogs.includes(testError.stack || testError.message));
    });

    it('should log warning messages with Error objects', () => {
      const testMessage = 'Test warning with stack';
      const testError = new Error('Test warning error');

      logger.warn(testMessage, testError);

      const warningLogs = consoleMock.warnings.join('\n');
      assert.ok(warningLogs.includes(testMessage));
      assert.ok(warningLogs.includes(testError.stack || testError.message));
    });

    it('should handle variable arguments in log method', () => {
      logger.log('Message with', 'variables', 123, true);
      assert.ok(consoleMock.logs.length > 0);
    });
  });

  describe('prefix format', () => {
    it('should include prefix in all log messages', () => {
      logger.log('Test log');
      logger.error('Test error');
      logger.warn('Test warning');
      logger.info('Test info');

      const allLogs = [
        ...consoleMock.logs,
        ...consoleMock.errors,
        ...consoleMock.warnings,
      ];

      allLogs.forEach(log => {
        assert.ok(log.includes('[TestLogger]'));
      });
    });
  });

  describe('timestamp format', () => {
    it('should include ISO timestamp in log messages', () => {
      logger.log('Test message with timestamp');

      const log = consoleMock.logs[0];
      const timestampMatch = log.match(/\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z/);
      assert.ok(timestampMatch);
    });
  });
});
