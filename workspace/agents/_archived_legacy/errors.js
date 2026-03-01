/**
 * OpenClaw Agents - Custom Error Classes
 */

class AgentError extends Error {
  constructor(message, code) {
    super(message);
    this.name = this.constructor.name;
    this.code = code;
    this.timestamp = new Date().toISOString();
  }
}

class RegistryError extends AgentError {
  constructor(message) {
    super(message, 'E_REGISTRY_FAILED');
  }
}

class AgentNotFoundError extends AgentError {
  constructor(agentId) {
    super(`Agent '${agentId}' not found in registry.`, 'E_AGENT_NOT_FOUND');
    this.agentId = agentId;
  }
}

class CapabilityMismatchError extends AgentError {
  constructor(required, available) {
    super(`Capability mismatch. Required: ${required.join(', ')}.`, 'E_CAPABILITY_MISMATCH');
    this.required = required;
    this.available = available;
  }
}

class ExecutionTimeoutError extends AgentError {
  constructor(agentId, timeout) {
    super(`Execution timeout for agent '${agentId}' after ${timeout}ms.`, 'E_EXECUTION_TIMEOUT');
    this.agentId = agentId;
    this.timeout = timeout;
  }
}

class ContextError extends AgentError {
  constructor(message) {
    super(message, 'E_CONTEXT_FAILED');
  }
}

module.exports = {
  AgentError,
  RegistryError,
  AgentNotFoundError,
  CapabilityMismatchError,
  ExecutionTimeoutError,
  ContextError
};
