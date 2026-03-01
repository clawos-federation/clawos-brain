/**
 * OpenClaw Dynamic Context Pruner (Evolution 7.0)
 * 
 * Implements Observation Masking and Signal-to-Noise filtering.
 * Goal: Reduce Titan Tier token consumption by ~30%.
 */

class ContextPruner {
  constructor(threshold = 0.4) {
    this.threshold = threshold; // Signal threshold
  }

  /**
   * Prune context by masking low-signal observations
   */
  prune(history) {
    console.log(`[Pruner] Analyzing ${history.length} context items...`);
    
    let prunedCount = 0;
    const prunedHistory = history.map(item => {
      const signal = this.calculateSignalScore(item);
      
      if (signal < this.threshold) {
        prunedCount++;
        return {
          ...item,
          content: `[PRUNED: Low Signal (${signal.toFixed(2)}) - Observation Masked]`,
          isMasked: true
        };
      }
      return item;
    });

    const reduction = ((prunedCount / history.length) * 100).toFixed(1);
    console.log(`[Pruner] Context pruned. Reduction: ${reduction}% (${prunedCount} items masked).`);
    
    return prunedHistory;
  }

  /**
   * Calculate signal score (0.0 - 1.0)
   * A real implementation would use embeddings or heuristics.
   */
  calculateSignalScore(item) {
    // Heuristic: Code blocks and error messages are high signal
    if (item.content.includes('```') || item.content.includes('Error:')) return 0.9;
    
    // Heuristic: Short acknowledgments are low signal
    if (item.content.length < 50) return 0.2;
    
    // Default: Moderate signal
    return 0.5;
  }
}

module.exports = { ContextPruner };
