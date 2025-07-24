import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { io, Socket } from 'socket.io-client';

export interface CostUpdate {
  type: string;
  job_id?: string;
  cost_change?: number;
  timestamp: string;
  data: any;
}

@Injectable({
  providedIn: 'root'
})
export class WebSocketService {
  private socket: Socket | null = null;
  private connected = false;
  
  private costUpdatesSubject = new BehaviorSubject<CostUpdate | null>(null);
  public costUpdates$ = this.costUpdatesSubject.asObservable();
  
  private connectionStatusSubject = new BehaviorSubject<boolean>(false);
  public connectionStatus$ = this.connectionStatusSubject.asObservable();

  constructor() {}

  connect(): void {
    if (this.connected) return;

    this.socket = io('ws://localhost:8000', {
      transports: ['websocket']
    });

    this.socket.on('connect', () => {
      console.log('WebSocket connected');
      this.connected = true;
      this.connectionStatusSubject.next(true);
    });

    this.socket.on('disconnect', () => {
      console.log('WebSocket disconnected');
      this.connected = false;
      this.connectionStatusSubject.next(false);
    });

    this.socket.on('cost_update', (data: CostUpdate) => {
      this.costUpdatesSubject.next(data);
    });

    this.socket.on('job_created', (data: any) => {
      this.costUpdatesSubject.next({
        type: 'job_created',
        job_id: data.job_id,
        timestamp: new Date().toISOString(),
        data: data
      });
    });

    this.socket.on('alert_triggered', (data: any) => {
      this.costUpdatesSubject.next({
        type: 'alert_triggered',
        timestamp: new Date().toISOString(),
        data: data
      });
    });
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.connected = false;
      this.connectionStatusSubject.next(false);
    }
  }

  isConnected(): boolean {
    return this.connected;
  }
}