/**
 * Tests for API Service - Authorization Header
 */

import apiService from './api';

// Mock fetch
global.fetch = jest.fn();

beforeEach(() => {
  // Clear mocks before each test
  fetch.mockClear();
  localStorage.clear();
});

describe('APIService Authorization Header', () => {
  test('should attach Authorization header when token is set in memory', async () => {
    // Setup
    const mockToken = 'test-token-123';
    apiService.setToken(mockToken);
    
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ success: true }),
    });

    // Make request
    await apiService.request('/test-endpoint');

    // Assert fetch was called with Authorization header
    expect(fetch).toHaveBeenCalledTimes(1);
    const [url, options] = fetch.mock.calls[0];
    expect(options.headers['Authorization']).toBe(`Bearer ${mockToken}`);
  });

  test('should attach Authorization header when token is in localStorage', async () => {
    // Setup - token only in localStorage, not set via setToken
    const mockToken = 'localStorage-token-456';
    localStorage.setItem('vaelis_token', mockToken);
    apiService.setToken(null); // Ensure memory token is not set
    
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ success: true }),
    });

    // Make request
    await apiService.request('/test-endpoint');

    // Assert fetch was called with Authorization header from localStorage
    expect(fetch).toHaveBeenCalledTimes(1);
    const [url, options] = fetch.mock.calls[0];
    expect(options.headers['Authorization']).toBe(`Bearer ${mockToken}`);
  });

  test('should prioritize memory token over localStorage token', async () => {
    // Setup - both tokens present
    const memoryToken = 'memory-token-789';
    const localStorageToken = 'localStorage-token-000';
    
    apiService.setToken(memoryToken);
    localStorage.setItem('vaelis_token', localStorageToken);
    
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ success: true }),
    });

    // Make request
    await apiService.request('/test-endpoint');

    // Assert fetch was called with memory token (higher priority)
    expect(fetch).toHaveBeenCalledTimes(1);
    const [url, options] = fetch.mock.calls[0];
    expect(options.headers['Authorization']).toBe(`Bearer ${memoryToken}`);
  });

  test('should not attach Authorization header when no token available', async () => {
    // Setup - no token
    apiService.setToken(null);
    localStorage.removeItem('vaelis_token');
    
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ success: true }),
    });

    // Make request
    await apiService.request('/test-endpoint');

    // Assert fetch was called without Authorization header
    expect(fetch).toHaveBeenCalledTimes(1);
    const [url, options] = fetch.mock.calls[0];
    expect(options.headers['Authorization']).toBeUndefined();
  });

  test('should include credentials: include for cookie-based auth', async () => {
    // Setup
    apiService.setToken('test-token');
    
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ success: true }),
    });

    // Make request
    await apiService.request('/test-endpoint');

    // Assert fetch was called with credentials: include
    expect(fetch).toHaveBeenCalledTimes(1);
    const [url, options] = fetch.mock.calls[0];
    expect(options.credentials).toBe('include');
  });

  test('should parse error responses with ok: false format', async () => {
    // Setup
    apiService.setToken('test-token');
    
    const mockError = {
      ok: false,
      error: 'auth_error',
      message: 'Authorization header missing'
    };
    
    fetch.mockResolvedValueOnce({
      ok: false,
      status: 401,
      json: async () => mockError,
    });

    // Make request and expect error
    await expect(apiService.request('/test-endpoint')).rejects.toThrow();

    // Verify error was properly parsed
    try {
      await apiService.request('/test-endpoint');
    } catch (error) {
      expect(error.status).toBe(401);
      expect(error.ok).toBe(false);
      expect(error.errorCode).toBe('auth_error');
    }
  });
});

describe('APIService uploadAsset', () => {
  test('should attach Authorization header for file uploads', async () => {
    // Setup
    const mockToken = 'upload-token-123';
    apiService.setToken(mockToken);
    
    const mockFile = new File(['test'], 'test.txt', { type: 'text/plain' });
    
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ file_id: '123' }),
    });

    // Upload file
    await apiService.uploadAsset(mockFile);

    // Assert fetch was called with Authorization header
    expect(fetch).toHaveBeenCalledTimes(1);
    const [url, options] = fetch.mock.calls[0];
    expect(options.headers['Authorization']).toBe(`Bearer ${mockToken}`);
    expect(options.credentials).toBe('include');
  });

  test('should read token from localStorage for file uploads if not in memory', async () => {
    // Setup
    const mockToken = 'localStorage-upload-token';
    localStorage.setItem('vaelis_token', mockToken);
    apiService.setToken(null);
    
    const mockFile = new File(['test'], 'test.txt', { type: 'text/plain' });
    
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ file_id: '123' }),
    });

    // Upload file
    await apiService.uploadAsset(mockFile);

    // Assert fetch was called with Authorization header from localStorage
    expect(fetch).toHaveBeenCalledTimes(1);
    const [url, options] = fetch.mock.calls[0];
    expect(options.headers['Authorization']).toBe(`Bearer ${mockToken}`);
  });
});
