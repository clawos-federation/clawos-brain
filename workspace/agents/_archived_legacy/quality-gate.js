/**
 * OpenClaw GM Agent - Quality Gate
 * 
 * 强制执行 7/10 质量阈值，确保所有输出符合标准
 */

const { AgentError } = require('./errors');

class QualityGateError extends AgentError {
  constructor(score, threshold, dimensions) {
    super(
      `Quality gate failed: ${score.toFixed(2)} < ${threshold}`,
      'E_QUALITY_GATE_FAILED'
    );
    this.score = score;
    this.threshold = threshold;
    this.dimensions = dimensions;
  }
}

class QualityGate {
  constructor(threshold = 7.0) {
    this.threshold = threshold;
    
    // 质量评估维度和权重
    this.dimensions = {
      completeness: 0.30,   // 完整性
      correctness: 0.25,    // 正确性
      maintainability: 0.20, // 可维护性
      robustness: 0.15,     // 健壮性
      innovation: 0.10      // 创新性
    };
  }

  /**
   * 评估输出质量
   */
  async evaluate(output, task, context = {}) {
    console.log('\n🔍 Quality Gate Evaluation');
    
    const scores = {};
    
    // 1. 完整性评估
    scores.completeness = this.evaluateCompleteness(output, task);
    
    // 2. 正确性评估
    scores.correctness = this.evaluateCorrectness(output, task);
    
    // 3. 可维护性评估
    scores.maintainability = this.evaluateMaintainability(output);
    
    // 4. 健壮性评估
    scores.robustness = this.evaluateRobustness(output);
    
    // 5. 创新性评估
    scores.innovation = this.evaluateInnovation(output, context);
    
    // 计算加权总分
    const totalScore = Object.entries(scores).reduce((sum, [dim, score]) => {
      return sum + (score * this.dimensions[dim]);
    }, 0);
    
    console.log('\n📊 Quality Scores:');
    console.log(`   完整性 (30%): ${scores.completeness.toFixed(1)}/10`);
    console.log(`   正确性 (25%): ${scores.correctness.toFixed(1)}/10`);
    console.log(`   可维护性 (20%): ${scores.maintainability.toFixed(1)}/10`);
    console.log(`   健壮性 (15%): ${scores.robustness.toFixed(1)}/10`);
    console.log(`   创新性 (10%): ${scores.innovation.toFixed(1)}/10`);
    console.log(`\n   总分: ${totalScore.toFixed(2)}/10`);
    console.log(`   阈值: ${this.threshold}/10`);
    
    const passed = totalScore >= this.threshold;
    
    if (passed) {
      console.log(`\n✅ Quality Gate: PASSED`);
    } else {
      console.log(`\n❌ Quality Gate: FAILED`);
      console.log(`   差距: ${(this.threshold - totalScore).toFixed(2)} 分`);
    }
    
    return {
      passed,
      totalScore,
      threshold: this.threshold,
      scores,
      timestamp: new Date().toISOString()
    };
  }

  /**
   * 完整性评估
   */
  evaluateCompleteness(output, task) {
    // 简化实现：检查输出长度和关键信息
    let score = 5.0; // 基础分
    
    if (!output || !output.response) {
      return 0;
    }
    
    const responseLength = output.response.length;
    
    // 长度评估
    if (responseLength > 500) score += 2.0;
    if (responseLength > 1000) score += 1.0;
    
    // 结构评估
    if (output.artifacts && output.artifacts.length > 0) score += 1.0;
    if (output.metadata) score += 0.5;
    
    // 需求匹配度（简化版）
    const taskKeywords = task.toLowerCase().split(/\s+/);
    const matchCount = taskKeywords.filter(kw => 
      output.response.toLowerCase().includes(kw)
    ).length;
    
    if (matchCount >= taskKeywords.length * 0.7) score += 0.5;
    
    return Math.min(10, score);
  }

  /**
   * 正确性评估
   */
  evaluateCorrectness(output, task) {
    let score = 7.0; // 假设基本正确
    
    // 检查常见错误标志
    const errorIndicators = [
      'error', 'undefined', 'null reference', 'exception',
      '错误', '异常', '失败'
    ];
    
    const hasErrors = errorIndicators.some(indicator =>
      output.response.toLowerCase().includes(indicator)
    );
    
    if (hasErrors) score -= 2.0;
    
    // 检查是否有明确的解决方案
    if (output.response.includes('```') || 
        output.response.includes('代码') ||
        output.response.includes('实现')) {
      score += 1.0;
    }
    
    return Math.max(0, Math.min(10, score));
  }

  /**
   * 可维护性评估
   */
  evaluateMaintainability(output) {
    let score = 6.0;
    
    const response = output.response || '';
    
    // 检查是否有注释或说明
    if (response.includes('//') || 
        response.includes('#') ||
        response.includes('/**') ||
        response.includes('说明') ||
        response.includes('注释')) {
      score += 1.5;
    }
    
    // 检查是否有文档或README
    if (response.includes('README') ||
        response.includes('文档') ||
        response.includes('使用方法')) {
      score += 1.0;
    }
    
    // 检查代码结构
    if (response.includes('function') ||
        response.includes('class') ||
        response.includes('module')) {
      score += 0.5;
    }
    
    // 检查命名规范
    const hasDescriptiveNames = /[a-zA-Z_][a-zA-Z0-9_]{3,}/.test(response);
    if (hasDescriptiveNames) score += 1.0;
    
    return Math.min(10, score);
  }

  /**
   * 健壮性评估
   */
  evaluateRobustness(output) {
    let score = 5.0;
    
    const response = output.response || '';
    
    // 检查错误处理
    const errorHandling = [
      'try', 'catch', 'error handling', 'exception',
      'validate', 'check', 'if', 'else',
      '错误处理', '异常', '验证', '检查'
    ];
    
    const hasErrorHandling = errorHandling.some(keyword =>
      response.toLowerCase().includes(keyword)
    );
    
    if (hasErrorHandling) score += 2.5;
    
    // 检查边界条件处理
    const boundaryHandling = [
      'null', 'undefined', 'empty', 'edge case',
      '边界', '空值', '极端情况'
    ];
    
    const hasBoundaryHandling = boundaryHandling.some(keyword =>
      response.toLowerCase().includes(keyword)
    );
    
    if (hasBoundaryHandling) score += 1.5;
    
    // 检查输入验证
    if (response.includes('validate') || 
        response.includes('验证') ||
        response.includes('校验')) {
      score += 1.0;
    }
    
    return Math.min(10, score);
  }

  /**
   * 创新性评估
   */
  evaluateInnovation(output, context) {
    let score = 5.0; // 基础分（标准实现）
    
    const response = output.response || '';
    
    // 检查是否使用了先进技术或方法
    const advancedKeywords = [
      'optimize', 'performance', 'cache', 'async',
      'parallel', 'distributed', 'ai', 'ml',
      '优化', '性能', '缓存', '异步', '并行'
    ];
    
    const usesAdvanced = advancedKeywords.some(kw =>
      response.toLowerCase().includes(kw)
    );
    
    if (usesAdvanced) score += 2.0;
    
    // 检查是否有独特的解决方案或见解
    if (response.includes('创新') || 
        response.includes('新颖') ||
        response.includes('独特') ||
        response.includes('alternative')) {
      score += 1.5;
    }
    
    // 检查是否超出了基本要求
    if (output.artifacts && output.artifacts.length > 2) {
      score += 1.0;
    }
    
    // 检查是否提供了多种方案
    if (response.includes('方案一') || 
        response.includes('Option 1') ||
        response.includes('Approach')) {
      score += 0.5;
    }
    
    return Math.min(10, score);
  }

  /**
   * 强制执行质量门
   */
  async enforce(output, task, context = {}) {
    const evaluation = await this.evaluate(output, task, context);
    
    if (!evaluation.passed) {
      throw new QualityGateError(
        evaluation.totalScore,
        evaluation.threshold,
        evaluation.scores
      );
    }
    
    return evaluation;
  }

  /**
   * 生成改进建议
   */
  generateImprovementSuggestions(evaluation) {
    const suggestions = [];
    
    const { scores } = evaluation;
    
    if (scores.completeness < 7) {
      suggestions.push('完整性不足：请确保完全满足任务需求，补充缺失的功能或信息');
    }
    
    if (scores.correctness < 7) {
      suggestions.push('正确性问题：请检查逻辑错误，确保代码或方案的正确性');
    }
    
    if (scores.maintainability < 7) {
      suggestions.push('可维护性较低：请添加注释、文档和清晰的命名，提升代码可读性');
    }
    
    if (scores.robustness < 7) {
      suggestions.push('健壮性不足：请添加错误处理、输入验证和边界条件检查');
    }
    
    if (scores.innovation < 5) {
      suggestions.push('创新性一般：考虑是否有更优的解决方案或技术选型');
    }
    
    return suggestions;
  }
}

module.exports = { QualityGate, QualityGateError };
