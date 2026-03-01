/**
 * OpenClaw Git Controller - Evolution 7.4
 * 
 * Provides physical isolation and atomic commits for AI agents.
 */
const { execSync } = require('child_process');

class GitController {
  constructor(repoPath = '/Users/henry/openclaw-system') {
    this.repoPath = repoPath;
  }

  createExpeditionBranch(id) {
    const branchName = `expedition/${id}`;
    console.log(`[Git] 🛡️ Creating isolation branch: ${branchName}`);
    try {
      execSync(`git checkout -b ${branchName}`, { cwd: this.repoPath });
      return branchName;
    } catch (e) {
      // If branch exists, just switch
      execSync(`git checkout ${branchName}`, { cwd: this.repoPath });
      return branchName;
    }
  }

  commitSuccess(message) {
    console.log('[Git] ✅ Committing successful iteration...');
    execSync('git add .', { cwd: this.repoPath });
    execSync(`git commit -m "${message}"`, { cwd: this.repoPath });
  }

  rollback(targetBranch = 'main') {
    console.log(`[Git] ⚠️ Rolling back to ${targetBranch}...`);
    execSync('git add .', { cwd: this.repoPath });
    execSync('git stash', { cwd: this.repoPath });
    execSync(`git checkout ${targetBranch}`, { cwd: this.repoPath });
  }

  mergeSuccess(branch) {
    console.log(`[Git] 🤝 Merging ${branch} into main...`);
    execSync('git checkout main', { cwd: this.repoPath });
    execSync(`git merge ${branch}`, { cwd: this.repoPath });
    execSync(`git branch -D ${branch}`, { cwd: this.repoPath });
  }
}

module.exports = { GitController };
