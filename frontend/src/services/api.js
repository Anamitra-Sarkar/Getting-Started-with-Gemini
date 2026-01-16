// Comprehensive API Service for Vaelis AI
// Use environment variable if defined, otherwise fallback to production backend
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'https://getting-started-with-gemini.onrender.com';

class APIService {
  constructor() {
    this.baseURL = BACKEND_URL;
    this.token = null;
  }

  setToken(token) {
    this.token = token;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    // Always try to get token from localStorage if not set in memory
    // This ensures consistency even if setToken wasn't called
    const token = this.token || localStorage.getItem('vaelis_token');
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
        credentials: 'include',  // Support cookie-based auth flows
      });

      if (!response.ok) {
        // Parse error response - handle new backend format with "ok": false
        const error = await response.json().catch(() => ({ 
          ok: false,
          error: 'request_failed',
          message: `HTTP ${response.status}` 
        }));
        
        // Create a detailed error object
        const errorObj = new Error(error.message || error.error || `HTTP ${response.status}`);
        errorObj.status = response.status;
        errorObj.ok = error.ok !== undefined ? error.ok : false;
        errorObj.errorCode = error.error;
        errorObj.details = error;
        
        throw errorObj;
      }

      return await response.json();
    } catch (error) {
      console.error(`API Error [${endpoint}]:`, error);
      
      // Check if it's a network error (server down) - be specific about TypeError
      if (error instanceof TypeError && error.message === 'Failed to fetch') {
        const serverDownError = new Error('Server down');
        serverDownError.isServerDown = true;
        throw serverDownError;
      }
      
      throw error;
    }
  }

  // Dashboard APIs
  async getDashboardStats() {
    return this.request('/agents/stats');
  }

  // Agent APIs
  async getAgents() {
    return this.request('/agents/');
  }

  async createAgent(data) {
    return this.request('/agents/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateAgent(agentId, data) {
    return this.request(`/agents/${agentId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteAgent(agentId) {
    return this.request(`/agents/${agentId}`, {
      method: 'DELETE',
    });
  }

  async runAgent(agentId, inputData) {
    return this.request(`/agents/${agentId}/run`, {
      method: 'POST',
      body: JSON.stringify({ input_data: inputData }),
    });
  }

  async getAgentRuns(agentId) {
    return this.request(`/agents/${agentId}/runs`);
  }

  // Intelligence APIs
  async detectIntent(text, conversationId = null) {
    return this.request('/intelligence/intent/detect', {
      method: 'POST',
      body: JSON.stringify({ text, conversation_id: conversationId }),
    });
  }

  async detectBias(content, contentType = 'message') {
    return this.request('/intelligence/bias/detect', {
      method: 'POST',
      body: JSON.stringify({ content, content_type: contentType }),
    });
  }

  async analyzeDecision(decisionContext, options = null) {
    return this.request('/intelligence/decision/analyze', {
      method: 'POST',
      body: JSON.stringify({ decision_context: decisionContext, options }),
    });
  }

  async detectContradiction(statements) {
    return this.request('/intelligence/contradiction/detect', {
      method: 'POST',
      body: JSON.stringify({ statements }),
    });
  }

  async scoreConfidence(content) {
    return this.request('/intelligence/confidence/score', {
      method: 'POST',
      body: JSON.stringify({ content }),
    });
  }

  async getDecisionHistory() {
    return this.request('/intelligence/decision/history');
  }

  async chatWithAI(prompt, mode = 'chat', useSearch = false) {
    return this.request('/ai/generate', {
      method: 'POST',
      body: JSON.stringify({ 
        prompt, 
        mode, 
        use_search: useSearch 
      }),
    });
  }

  // Tools APIs
  async getTools() {
    return this.request('/tools/');
  }

  async getToolCategories() {
    return this.request('/tools/categories');
  }

  async getTool(toolId) {
    return this.request(`/tools/${toolId}`);
  }

  async executeTool(toolId, parameters) {
    return this.request(`/tools/${toolId}/execute`, {
      method: 'POST',
      body: JSON.stringify({ parameters }),
    });
  }

  async getToolUsage(toolId) {
    return this.request(`/tools/${toolId}/usage`);
  }

  async getAllToolUsage() {
    return this.request('/tools/usage/all');
  }

  // Markets APIs
  async analyzeEarnings(ticker, reportData) {
    return this.request('/markets/earnings/analyze', {
      method: 'POST',
      body: JSON.stringify({ ticker, report_data: reportData }),
    });
  }

  async analyzeSectorRotation(currentSector, economicIndicators) {
    return this.request('/markets/sector/rotation', {
      method: 'POST',
      body: JSON.stringify({ current_sector: currentSector, economic_indicators: economicIndicators }),
    });
  }

  async simulateMacro(scenario) {
    return this.request('/markets/macro/simulate', {
      method: 'POST',
      body: JSON.stringify({ scenario }),
    });
  }

  async analyzeCryptoRisk(asset, marketData) {
    return this.request('/markets/crypto/risk', {
      method: 'POST',
      body: JSON.stringify({ asset, market_data: marketData }),
    });
  }

  async analyzeDefi(protocol, metrics) {
    return this.request('/markets/defi/analyze', {
      method: 'POST',
      body: JSON.stringify({ protocol, metrics }),
    });
  }

  async analyzePortfolio(holdings) {
    return this.request('/markets/portfolio/analyze', {
      method: 'POST',
      body: JSON.stringify({ holdings }),
    });
  }

  async getMarketsHistory() {
    return this.request('/markets/analysis/history');
  }

  // Health APIs
  async analyzeWellness(data) {
    return this.request('/health/wellness/analyze', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async analyzeLongevity(profile) {
    return this.request('/health/longevity/analyze', {
      method: 'POST',
      body: JSON.stringify(profile),
    });
  }

  async analyzeNutrition(foodLog) {
    return this.request('/health/nutrition/analyze', {
      method: 'POST',
      body: JSON.stringify({ food_log: foodLog }),
    });
  }

  async createFitnessPlan(goals, profile) {
    return this.request('/health/fitness/plan', {
      method: 'POST',
      body: JSON.stringify({ goals, profile }),
    });
  }

  async simplifyResearch(paperUrl, focusArea) {
    return this.request('/health/research/simplify', {
      method: 'POST',
      body: JSON.stringify({ paper_url: paperUrl, focus_area: focusArea }),
    });
  }

  async getHealthHistory() {
    return this.request('/health/analysis/history');
  }

  // Education APIs
  async detectLearningGaps(resume, targetRole) {
    return this.request('/education/learning-gaps/detect', {
      method: 'POST',
      body: JSON.stringify({ resume, target_role: targetRole }),
    });
  }

  async analyzeResume(resumeText) {
    return this.request('/education/resume/analyze', {
      method: 'POST',
      body: JSON.stringify({ resume_text: resumeText }),
    });
  }

  async analyzeSalary(jobDetails) {
    return this.request('/education/salary/analyze', {
      method: 'POST',
      body: JSON.stringify(jobDetails),
    });
  }

  async getCareerPath(currentRole, targetRole, skills) {
    return this.request('/education/career/path', {
      method: 'POST',
      body: JSON.stringify({ current_role: currentRole, target_role: targetRole, skills }),
    });
  }

  async analyzeSkillsGap(currentSkills, targetSkills) {
    return this.request('/education/skills/gap', {
      method: 'POST',
      body: JSON.stringify({ current_skills: currentSkills, target_skills: targetSkills }),
    });
  }

  async prepareInterview(jobDescription, experience) {
    return this.request('/education/interview/prepare', {
      method: 'POST',
      body: JSON.stringify({ job_description: jobDescription, experience }),
    });
  }

  async getEducationHistory() {
    return this.request('/education/analysis/history');
  }

  // Business APIs
  async analyzeMarketSizing(description) {
    return this.request('/business/market-sizing', {
      method: 'POST',
      body: JSON.stringify({ description }),
    });
  }

  async analyzeMoat(company, industry) {
    return this.request('/business/moat/analyze', {
      method: 'POST',
      body: JSON.stringify({ company, industry }),
    });
  }

  async simulatePricing(product, market, costs) {
    return this.request('/business/pricing/simulate', {
      method: 'POST',
      body: JSON.stringify({ product, market, costs }),
    });
  }

  async createGTMPlan(product, targetMarket) {
    return this.request('/business/gtm/plan', {
      method: 'POST',
      body: JSON.stringify({ product, target_market: targetMarket }),
    });
  }

  async analyzeSWOT(company) {
    return this.request('/business/swot', {
      method: 'POST',
      body: JSON.stringify({ company }),
    });
  }

  async createBusinessModel(idea) {
    return this.request('/business/business-model', {
      method: 'POST',
      body: JSON.stringify({ idea }),
    });
  }

  async createFinancialProjection(assumptions) {
    return this.request('/business/financial-projection', {
      method: 'POST',
      body: JSON.stringify({ assumptions }),
    });
  }

  async getBusinessHistory() {
    return this.request('/business/analysis/history');
  }

  // Personal APIs
  async createConstraint(type, description, severity) {
    return this.request('/personal/constraints', {
      method: 'POST',
      body: JSON.stringify({ type, description, severity }),
    });
  }

  async getConstraints() {
    return this.request('/personal/constraints');
  }

  async updateConstraint(constraintId, data) {
    return this.request(`/personal/constraints/${constraintId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteConstraint(constraintId) {
    return this.request(`/personal/constraints/${constraintId}`, {
      method: 'DELETE',
    });
  }

  async createGoal(title, description, targetDate, constraints) {
    return this.request('/personal/goals', {
      method: 'POST',
      body: JSON.stringify({ title, description, target_date: targetDate, constraints }),
    });
  }

  async getGoals() {
    return this.request('/personal/goals');
  }

  async updateGoal(goalId, data) {
    return this.request(`/personal/goals/${goalId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async decomposeGoal(goalId) {
    return this.request(`/personal/goals/${goalId}/decompose`, {
      method: 'POST',
    });
  }

  async modelConsequences(decision, context, constraints) {
    return this.request('/personal/consequences/model', {
      method: 'POST',
      body: JSON.stringify({ decision, context, constraints }),
    });
  }

  async minimizeRegret(options, values, uncertainties) {
    return this.request('/personal/regret/minimize', {
      method: 'POST',
      body: JSON.stringify({ options, values, uncertainties }),
    });
  }

  async analyzeDontLose(scenario, valuables, risks) {
    return this.request('/personal/dont-lose', {
      method: 'POST',
      body: JSON.stringify({ scenario, valuables, risks }),
    });
  }

  async runLifeSimulation(profile, decisions, timeHorizon) {
    return this.request('/personal/life-simulation', {
      method: 'POST',
      body: JSON.stringify({ profile, decisions, time_horizon: timeHorizon }),
    });
  }

  async getConsequencesHistory() {
    return this.request('/personal/consequences/history');
  }

  // Security APIs
  async detectPromptInjection(text) {
    return this.request('/security/prompt-injection/detect', {
      method: 'POST',
      body: JSON.stringify({ text }),
    });
  }

  async calculateTrustScore(entity, interactions) {
    return this.request('/security/trust/score', {
      method: 'POST',
      body: JSON.stringify({ entity, interactions }),
    });
  }

  async explainPrivacy(service, dataTypes) {
    return this.request('/security/privacy/explain', {
      method: 'POST',
      body: JSON.stringify({ service, data_types: dataTypes }),
    });
  }

  async checkCompliance(data, regulations) {
    return this.request('/security/compliance/check', {
      method: 'POST',
      body: JSON.stringify({ data, regulations }),
    });
  }

  async getSecurityIncidents() {
    return this.request('/security/incidents');
  }

  async resolveIncident(incidentId, resolution) {
    return this.request(`/security/incidents/${incidentId}/resolve`, {
      method: 'POST',
      body: JSON.stringify({ resolution }),
    });
  }

  async logAudit(action, details) {
    return this.request('/security/audit/log', {
      method: 'POST',
      body: JSON.stringify({ action, details }),
    });
  }

  async getAuditLogs(filters = {}) {
    const params = new URLSearchParams(filters);
    return this.request(`/security/audit/logs?${params}`);
  }

  // Web APIs
  async summarizeWebContent(url) {
    return this.request('/web/summarize', {
      method: 'POST',
      body: JSON.stringify({ url }),
    });
  }

  async checkCredibility(url, content) {
    return this.request('/web/credibility/check', {
      method: 'POST',
      body: JSON.stringify({ url, content }),
    });
  }

  async detectWebBias(content, topic) {
    return this.request('/web/bias/detect', {
      method: 'POST',
      body: JSON.stringify({ content, topic }),
    });
  }

  async generateNewsHeatmap(topic, timeRange) {
    return this.request('/web/news/heatmap', {
      method: 'POST',
      body: JSON.stringify({ topic, time_range: timeRange }),
    });
  }

  async detectNarrativeShifts(topic, sources) {
    return this.request('/web/narrative/shifts', {
      method: 'POST',
      body: JSON.stringify({ topic, sources }),
    });
  }

  async factCheck(claim, sources) {
    return this.request('/web/fact-check', {
      method: 'POST',
      body: JSON.stringify({ claim, sources }),
    });
  }

  async getCredibilityHistory() {
    return this.request('/web/credibility/history');
  }

  // Admin APIs
  async seedTools() {
    return this.request('/admin/seed/tools', {
      method: 'POST',
    });
  }

  async listFeatures() {
    return this.request('/admin/features/list');
  }

  // Account APIs
  async getAccountInfo() {
    return this.request('/account/me');
  }

  async addCredits(amount) {
    return this.request('/account/credits/add', {
      method: 'POST',
      body: JSON.stringify({ amount }),
    });
  }

  async getTransactions() {
    return this.request('/account/transactions');
  }

  // Assets APIs
  async uploadAsset(file) {
    const formData = new FormData();
    formData.append('file', file);

    const url = `${this.baseURL}/assets/upload`;
    const headers = {};
    
    // Always try to get token from localStorage if not set in memory
    const token = this.token || localStorage.getItem('vaelis_token');
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(url, {
      method: 'POST',
      headers,
      body: formData,
      credentials: 'include',  // Support cookie-based auth
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Upload failed' }));
      throw new Error(error.message || error.error || 'Upload failed');
    }

    return await response.json();
  }

  async getAssets() {
    return this.request('/assets/');
  }
}

// Create a singleton instance
const apiService = new APIService();

export default apiService;
