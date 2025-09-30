/**
 * Authentication service
 * Handles all auth-related API calls
 */

import { api } from './api';

export interface LoginRequest {
  password: string;
}

export interface LoginResponse {
  message: string;
  authenticated: boolean;
}

export interface LogoutResponse {
  message: string;
}

export const authService = {
  /**
   * Login with password
   */
  async login(password: string): Promise<LoginResponse> {
    return api.post<LoginResponse, LoginRequest>('/auth/login', { password });
  },

  /**
   * Logout current user
   */
  async logout(): Promise<LogoutResponse> {
    return api.post<LogoutResponse>('/auth/logout');
  },

  /**
   * Check authentication status
   */
  async checkAuth(): Promise<{ authenticated: boolean }> {
    return api.get<{ authenticated: boolean }>('/auth/check');
  },
};
