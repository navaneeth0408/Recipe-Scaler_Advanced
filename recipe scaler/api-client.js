/**
 * API Client for Recipe Scaler Backend
 * 
 * Centralized helper for all backend API communication
 * Handles:
 * - Configuration of API base URL
 * - Request/response formatting
 * - Error handling
 * - Loading states
 */

// Configuration
// Always use explicit backend address for API calls. When the frontend is
// opened via file:// or via a simple static server, window.location.origin may
// be "null" or different; using BASE_URL avoids CORS problems.
// Use 127.0.0.1 so the origin matches http://127.0.0.1:5501 where the frontend runs.
const BASE_URL = "http://127.0.0.1:8000";

const API_CONFIG = {
  // use constant directly; can be modified for deployments if needed
  BASE_URL,
  TIMEOUT: 30000, // 30 seconds
  RETRY_ATTEMPTS: 2,
};

/**
 * Recipe Scaler API Client
 * All methods return promises that resolve with response data
 */
const apiClient = {
  /**
   * Generic fetch wrapper with error handling
   */
  async request(endpoint, method = 'POST', body = null) {
    const url = `${API_CONFIG.BASE_URL}${endpoint}`;

    const options = {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
    };

    if (body) {
      options.body = JSON.stringify(body);
    }

    try {
      const response = await fetch(url, options);

      if (!response.ok) {
        const error = await response.json().catch(() => ({
          error: `HTTP ${response.status}: ${response.statusText}`
        }));
        throw new Error(error.detail || error.error || 'API request failed');
      }

      return await response.json();
    } catch (error) {
      console.error(`API Error [${endpoint}]:`, error.message);
      throw error;
    }
  },

  /**
   * POST request helper
   */
  async post(endpoint, body) {
    return this.request(endpoint, 'POST', body);
  },

  /**
   * GET request helper
   */
  async get(endpoint) {
    return this.request(endpoint, 'GET');
  },

  // ========================================================================
  // YOUTUBE ENDPOINTS
  // ========================================================================

  /**
   * Extract metadata from a YouTube video
   * @param {string} url - YouTube video URL
   * @returns {Promise<{metadata: Object, success: boolean}>}
   */
  async extractYouTubeMetadata(url) {
    return this.post('/api/youtube/extract', {
      url,
      extract_ingredients: false,
    });
  },

  /**
   * Search YouTube for recipe videos
   * @param {string} query - Search query
   * @param {string} category - Optional recipe category
   * @param {string} pageToken - Optional pagination token
   * @returns {Promise<{results: Array, next_page_token: string, success: boolean}>}
   */
  async searchYouTube(query, category = '', pageToken = '') {
    return this.post('/api/youtube/search', {
      query,
      category: category || null,
      page_token: pageToken || null,
      max_results: 6,
    });
  },

  /**
   * Extract ingredients from YouTube video audio
   * Uses speech-to-text when description/transcript unavailable
   * @param {string} youtubeUrl - YouTube video URL
   * @returns {Promise<{video_id: string, video_title: string, transcript: string, ingredients: Array, success: boolean}>}
   */
  async extractAudioIngredients(youtubeUrl) {
    return this.post('/api/youtube/extract-audio-ingredients', {
      youtube_url: youtubeUrl,
    });
  },

  // ========================================================================
  // INGREDIENT ENDPOINTS
  // ========================================================================

  /**
   * Parse ingredients from raw text (e.g., YouTube description)
   * Mimics the frontend parseIngredients() function
   * @param {string} text - Raw ingredient text
   * @param {number} servingSize - Optional serving size
   * @returns {Promise<{ingredients: Array, extracted_count: number, success: boolean}>}
   */
  async parseIngredients(text, servingSize = null) {
    return this.post('/api/ingredients/parse', {
      text,
      serving_size: servingSize,
    });
  },

  /**
   * Extract structured ingredients from comma/newline-separated text
   * @param {string} text - Ingredient list
   * @param {number} servingSize - Serving size
   * @returns {Promise<{ingredients: Array, success: boolean}>}
   */
  async extractIngredients(text, servingSize = 1) {
    return this.post('/api/ingredients/extract', {
      text,
      serving_size: servingSize,
    });
  },

  // ========================================================================
  // SCALING ENDPOINTS
  // ========================================================================

  /**
   * Scale recipe ingredients
   * @param {Array} ingredients - List of ingredients
   * @param {number} originalServings - Original serving size
   * @param {number} targetServings - Target serving size
   * @returns {Promise<{ingredients: Array, scale_factor: number, success: boolean}>}
   */
  async scaleRecipe(data) {
    const response = await fetch("http://127.0.0.1:8000/api/scale", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(data)
    });

    return await response.json();
  },

  // ========================================================================
  // AI ENDPOINTS
  // ========================================================================

  /**
   * Get AI-based ingredient substitutions
   * @param {string} ingredient - Ingredient name
   * @param {number} quantity - Quantity
   * @param {string} unit - Unit of measurement
   * @param {string} dietaryPreference - Optional dietary preference
   * @returns {Promise<{substitutions: Array, success: boolean}>}
   */
  async getSubstitutions(ingredient, quantity, unit) {
    return this.post('/api/substitute', {
      ingredient,
      quantity,
      unit
    });
  },

  /**
   * Analyze nutrition of ingredients
   * @param {Array} ingredients - List of ingredients
   * @param {number} servings - Number of servings
   * @returns {Promise<{total: Object, per_serving: Object, success: boolean}>}
   */
  async analyzeNutrition(ingredients, servings = 1) {
    return this.post('/api/ai/nutrition', {
      ingredients,
      servings,
    });
  },

  /**
   * Chat with cooking assistant
   * @param {string} message - User message
   * @param {string} sessionId - Optional session ID
   * @param {Object} recipeContext - Optional recipe context
   * @returns {Promise<{assistant_response: string, session_id: string, success: boolean}>}
   */
  async chatWithAssistant(message, sessionId = null, recipeContext = null) {
    return this.post('/api/ai/chat', {
      session_id: sessionId,
      message,
      recipe_context: recipeContext,
    });
  },

  /**
   * Translate recipe or ingredients
   * @param {Array|string} content - Content to translate (ingredients or text)
   * @param {string} targetLanguage - Target language code
   * @returns {Promise<{translated: Array|string, success: boolean}>}
   */
  async translate(content, targetLanguage) {
    const isArrayContent = Array.isArray(content);
    const isObjectArray = isArrayContent && content.every(item => item && typeof item === 'object');
    const isStringArray = isArrayContent && content.every(item => typeof item === 'string');

    return this.post('/api/ai/translate', {
      ingredients: isObjectArray ? content : null,
      texts: isStringArray ? content : null,
      text: typeof content === 'string' ? content : null,
      target_language: targetLanguage,
    });
  },

  // ========================================================================
  // HEALTH CHECKS
  // ========================================================================

  /**
   * Check if backend API is available
   * @returns {Promise<boolean>}
   */
  async isHealthy() {
    try {
      const response = await this.get('/api/health');
      return response.status === 'healthy';
    } catch (error) {
      console.warn('Backend API is not available:', error.message);
      return false;
    }
  },

  /**
   * Test backend connectivity with timeout
   * @returns {Promise<boolean>}
   */
  async testConnectivity() {
    return Promise.race([
      this.isHealthy(),
      new Promise((_, reject) =>
        setTimeout(() => reject(new Error('Timeout')), API_CONFIG.TIMEOUT)
      )
    ]).catch(() => false);
  },
};

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = apiClient;
}
