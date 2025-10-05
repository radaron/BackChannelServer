/**
 * Manage service
 * Handles all management-related API calls
 */

import { api } from './api';

export interface ClientData {
  name: string;
  polledTime: number;
  uptime?: number;
  cpuUsage?: number;
  memoryUsage?: number;
  diskUsage?: number;
  temperature?: number;
}

export interface ClientsResponse {
  data: ClientData[];
}

export interface ManageData {
  // Define your data structure here
  [key: string]: unknown;
}

export interface DeleteRequest {
  name: string;
}

export const manageService = {
  /**
   * Get all clients with their metrics
   */
  async getClients(): Promise<ClientData[]> {
    const response = await api.get<ClientsResponse>('/manage/data');
    return response.data;
  },

  /**
   * Get manage data
   */
  async getData(): Promise<ManageData> {
    return api.get<ManageData>('/manage/data');
  },

  /**
   * Delete data by name
   */
  async deleteData(name: string): Promise<void> {
    return api.delete<void, DeleteRequest>('/manage/data', { name });
  },

  /**
   * Create new data
   */
  async createData(data: Partial<ManageData>): Promise<ManageData> {
    return api.post<ManageData, Partial<ManageData>>('/manage/data', data);
  },

  /**
   * Update existing data
   */
  async updateData(id: string, data: Partial<ManageData>): Promise<ManageData> {
    return api.put<ManageData, Partial<ManageData>>(`/manage/data/${id}`, data);
  },

  /**
   * Connect to a client and get forwarder ID for SSE
   */
  async connect(name: string): Promise<{ forwarderId: string }> {
    return api.post<{ forwarderId: string }, { name: string }>('/manage/connect', { name });
  },

  /**
   * Delete/stop a forwarder job
   */
  async deleteForwarder(taskId: string): Promise<void> {
    return api.delete<void, never>(`/manage/forwarder/${taskId}`, undefined as never);
  },
};
