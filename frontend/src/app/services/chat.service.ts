// frontend/src/app/services/chat.service.ts
import { Injectable } from '@angular/core';
import { Observable, Subject } from 'rxjs';
import { ulid } from 'ulid';
import { UserProfile } from './auth.service';

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  public sessionId: string = ulid();
  private wsUrl = `ws://localhost:8000/ws/${this.sessionId}`;
  
  private socket!: WebSocket;
  public messagesSubject = new Subject<string>();
  private interruptSubject = new Subject<any>();

  constructor() {
  }

  public initializeWebSocket(user: UserProfile): void {
    this.wsUrl = `ws://localhost:8000/ws/${this.sessionId}/userId/${user.id}/username/${user.name}/email/${user.email}`;
    this.socket = new WebSocket(this.wsUrl);

    this.socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.interrupt && data.interrupt === true) {
        this.interruptSubject.next(data.message);
      } else {
        this.messagesSubject.next(data.message);
      }
    };
  }

  sendMessage(message: string): void {
    this.socket.send(message);
  }

  sendInterruptResponse(response: string): void {
    this.socket.send(response);
  }

  getMessages(): Observable<string> {
    return this.messagesSubject.asObservable();
  }

  getInterrupts(): Observable<any> {
    return this.interruptSubject.asObservable();
  }
}