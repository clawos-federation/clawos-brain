#!/usr/bin/env node

/**
 * OpenClaw Agent Router with GM Agent Integration
 *
 * Routes tasks to most appropriate agent(s) based on capability matching.
 * Automatically triggers GM Agent for complex tasks (P0 priority feature).
 */

const path = require('path');
const fs = require('fs');
const { AgentFactory } = require('./agent-factory');
const { GMTrigger } = require('./gm-trigger');
const { QualityGate } = require('./quality-gate');

class AgentRouter {
  constructor(workspacePath = '/Users/henry/openclaw-system/workspace') {
    this.factory = new AgentFactory(workspacePath);
    this.logsDir = path.join(workspacePath, 'agents', 'logs');
    this.cooldowns = new Map(); // agentId -> cooldownUntil
    this.gmTrigger = new GMTrigger();
    this.qualityGate = new QualityGate(7.0);
    this.enableGM = true; // P1 feature: GM Agent trigger
    
    this.taskKeywords = {
